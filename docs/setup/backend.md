# Steps to set up an initial backend

Create a new directory named backend in the root folder. The entire backend should be in the backend folder.

### pip-tools
Install and use pip-tools when managing Python dependencies. Create a separate requirements.in and requirements.txt.

Also include a separate requirements.dev.in file, also managed by pip-tools.

### Django
Install django and django-cors-headers.

Create a new django project called django_project and a new app called core.

For initial setup, always use a local sqlite database as the default with:
"NAME": BASE_DIR / "dev.sqlite3"

Create a local superuser with username: admin and password: password, so
the local developer can access the Django admin panel.

### Pydantic and Pyright
Install pyright, pre-commit, and django-stubs in requirements.dev.in.

### Pre-commit hooks
Install pre-commit in requirements.dev.in.
Install django-stubs for Django type-checks. Add django_stubs_ext.monkeypatch() workaround to settings.py if needed.

Configure the following pre-commit hooks to run on every commit:
- pyright
- front-end linting (npm run lint)
- front-end type-checking (npm run type-check)


### Django Ninja
Install django-ninja.

Use core/urls.py as the main file for importing django-ninja routers from across the application. django_project/urls.py should include core/urls.py at the path "/api".

Create core/base_pydantic_models.py. Define BaseRequestModel and BaseResponseModel which extend the Pydantic base model. Include `model_config = ConfigDict(frozen=True, extra="forbid")`.

Also create/default_success_response.py. Define DefaultSuccessResponse which extends BaseResponseModel and includes `success: bool = True`.

### Transactions and Typed Responses

Copy docs/setup/backend/typed_response_transaction_router.py into the backend/core directory.
We use this router to ensure every API request is wrapped in a transaction and also allow inferring response type from function declaration.

### Testing
Install pytest and pytest-django in requirements.dev.in.
