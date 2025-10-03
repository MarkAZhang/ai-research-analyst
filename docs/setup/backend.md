# Steps to set up an initial backend

Create a new directory named backend in the root folder. The entire backend should be in the backend folder.

### pip-tools
Install and use pip-tools when managing Python dependencies. Create a separate requirements.in and requirements.txt.

### Django
Install Django.

Create a new django project called django_project and a new app called core.

For now, always use a local sqlite database as the default with:
"NAME": BASE_DIR / "dev.sqlite3"

Create a local superuser with username: admin and password: password, so
I can access the Django admin panel.

### Pydantic and Pyright
Install pydantic for data validation and serialization.
Install pyright for type checking.

### Django Ninja
Install django-ninja.

Use core/urls.py as the main file for importing django-ninja routers from across the application. django_project/urls.py should include core/urls.py at the path "/api".

Create core/base_pydantic_models.py. Define BaseRequestModel and BaseResponseModel which extend the Pydantic base model. Include `model_config = ConfigDict(frozen=True, extra="forbid")`.

Also create/default_success_response.py. Define DefaultSuccessResponse which extends BaseResponseModel and includes `success: bool = True`.
