import inspect
from collections.abc import Callable
from functools import wraps

from django.db import transaction
from ninja import Router


def wrap_in_transaction(view_func: Callable) -> Callable:
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        with transaction.atomic():
            return view_func(*args, **kwargs)

    return wrapped_view


"""
We tried for a while to get the recommended approach by Django to work,
which is setting ATOMIC_REQUESTS=True in settings.py and
using the transaction.non_atomic_requests decorator when we
wanted to disable transactions in a particular view,
Unfortunately, we weren't able to get the decorator to properly apply
to the underlying Django view function (which ninja does not expose).

Using a tag is not ideal, as tags can also be used by other tools like
swagger. But it is a convenient way to pass data from the
view definition into add_api_operation, and it works for now.
"""
DISABLE_DEFAULT_TRANSACTION_TAG = "disable-default-transaction"


class TypedResponseTransactionRouter(Router):
    """Extension of default django-ninja router to infer response type from function declaration.

    See https://github.com/vitalik/django-ninja/issues/633 for issue and solution.

    Also wraps all requests in a transaction by default.

    To disable the transaction, do:

    @router.get("/no-transaction-example", tags=["disable-default-transaction"])
    def get_no_transaction_example(request: Auth0HttpRequest) -> DefaultSuccessResponse:
        return DefaultSuccessResponse()
    """

    def add_api_operation(self, path, methods, view_func, *args, **kwargs):
        try:
            maybe_return_annotation = inspect.signature(view_func).return_annotation
            if maybe_return_annotation is not inspect.Signature.empty:
                kwargs["response"] = maybe_return_annotation
        except RuntimeError as e:
            raise RuntimeError(
                f"Did you forget to return a valid explicit type? Encountered {e} while "
                f"inferring response type."
            )

        if DISABLE_DEFAULT_TRANSACTION_TAG not in (kwargs.get("tags") or []):
            view_func = wrap_in_transaction(view_func)

        return super().add_api_operation(path, methods, view_func, *args, **kwargs)
