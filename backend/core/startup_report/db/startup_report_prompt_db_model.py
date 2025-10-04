from django.db import models


class StartupReportPromptDbModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    prompt = models.TextField()

    class Meta:
        db_table = 'core_startupreportprompt'

    def __str__(self):
        return f"Prompt {self.id} - {self.created_at}"  # type: ignore[reportAttributeAccessIssue]
