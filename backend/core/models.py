# Models have been moved to their respective modules
# Import them here for Django admin and migrations compatibility
from core.startup_report.db.startup_report_db_model import (
    StartupReportDbModel as StartupReport,
)
from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel as StartupReportPrompt,
)
