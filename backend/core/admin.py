from django.contrib import admin
from .models import StartupReportPrompt, StartupReport


@admin.register(StartupReportPrompt)
class StartupReportPromptAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'prompt')
    list_filter = ('created_at',)
    search_fields = ('prompt',)


@admin.register(StartupReport)
class StartupReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'generation_status', 'read_by_user', 'created_at')
    list_filter = ('generation_status', 'read_by_user', 'created_at')
    search_fields = ('name', 'report_text')
