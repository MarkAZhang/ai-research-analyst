from django.db import models


class StartupReportPrompt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    prompt = models.TextField()

    def __str__(self):
        return f"Prompt {self.id} - {self.created_at}"  # type: ignore[reportAttributeAccessIssue]


class StartupReport(models.Model):
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

    def __str__(self):
        return f"{self.name} - {self.generation_status}"
