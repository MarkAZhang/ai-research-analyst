from django.db import models

from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel,
)


class StartupReportDbModel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read_by_user = models.BooleanField(default=False)
    generation_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    report_text = models.TextField(blank=True)
    prompt = models.ForeignKey(
        StartupReportPromptDbModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
    )

    class Meta:
        db_table = 'core_startupreport'

    def __str__(self):
        return f"{self.name} - {self.generation_status}"
