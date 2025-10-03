# Backend architecture

### High-level layout

django_project is the main Django project, which contains top-level configurations and settings.

core is the main app, which contains application-level models and routes.

### Module organization

Within the core app, we aim for cohesive modules, where models, views, and business logic are within a single directory.

Here is an example layout for a particular module:
- startup_report
  - db
    - startup_report_prompt_db_model.py - contains a StartupReportPromptDbModel Django db model.
    - startup_report_db_model.py - contains a StartupReportDbModel Django db model.
    - startup_report_db_queries.py - contains read-only functions which query the Django db models.
    - startup_report_db_mutators.py - contains functions which read and write to the Django db models.
  - public
    - api.py - contains api routes. Calls db functions as needed to handle the api route.

### Routing

We use django-ninja for routing. The main list of routes is found in core/urls.py, and routes for individual modules is found in the module's public/api.py file.

For each route, the request and response objects should be Pydantic models, and should subclass (or be child classes of) BaseRequestModel and BaseResponseModel, which are defined in core/base_pydantic_models.py.
