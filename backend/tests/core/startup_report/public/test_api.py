import pytest
from django.test import Client

from core.startup_report.db.startup_report_db_model import StartupReportDbModel
from core.startup_report.db.startup_report_prompt_db_model import (
    StartupReportPromptDbModel,
)


@pytest.fixture
def client():
    """Create a Django test client."""
    return Client()


@pytest.mark.django_db
class TestGetStartupReports:
    """Tests for GET /api/startup-report endpoint."""

    def test_get_empty_reports(self, client):
        """Test getting reports when database is empty."""
        response = client.get('/api/startup-report')

        assert response.status_code == 200
        data = response.json()
        assert 'reports' in data
        assert data['reports'] == []

    def test_get_single_report(self, client):
        """Test getting a single startup report."""
        # Create a test report
        report = StartupReportDbModel.objects.create(
            name='Test Startup',
            generation_status='pending',
            read_by_user=False,
            report_text='',
        )

        response = client.get('/api/startup-report')

        assert response.status_code == 200
        data = response.json()
        assert len(data['reports']) == 1
        assert data['reports'][0]['name'] == 'Test Startup'
        assert data['reports'][0]['generation_status'] == 'pending'
        assert data['reports'][0]['read_by_user'] is False
        assert data['reports'][0]['id'] == report.id  # type: ignore[reportAttributeAccessIssue]

    def test_get_multiple_reports_ordered_by_date(self, client):
        """Test getting multiple reports ordered by creation date."""
        # Create multiple reports
        report1 = StartupReportDbModel.objects.create(
            name='First Startup', generation_status='pending'
        )
        report2 = StartupReportDbModel.objects.create(
            name='Second Startup', generation_status='completed'
        )
        report3 = StartupReportDbModel.objects.create(
            name='Third Startup', generation_status='started'
        )

        response = client.get('/api/startup-report')

        assert response.status_code == 200
        data = response.json()
        assert len(data['reports']) == 3
        # Should be ordered by created_at descending (newest first)
        assert data['reports'][0]['name'] == 'Third Startup'
        assert data['reports'][1]['name'] == 'Second Startup'
        assert data['reports'][2]['name'] == 'First Startup'


@pytest.mark.django_db
class TestCreateStartupReports:
    """Tests for POST /api/startup-report/create endpoint."""

    def test_create_single_report(self, client):
        """Test creating a single startup report."""
        # Create a prompt first (required for creating reports)
        StartupReportPromptDbModel.objects.create(prompt='Test prompt')

        payload = {'names': ['Test Startup']}

        response = client.post(
            '/api/startup-report/create',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify the report was created in the database
        reports = StartupReportDbModel.objects.filter(name='Test Startup')
        assert reports.count() == 1
        assert reports[0].generation_status == 'pending'
        assert reports[0].read_by_user is False

    def test_create_multiple_reports(self, client):
        """Test creating multiple startup reports at once."""
        # Create a prompt first (required for creating reports)
        StartupReportPromptDbModel.objects.create(prompt='Test prompt')

        payload = {'names': ['Startup A', 'Startup B', 'Startup C']}

        response = client.post(
            '/api/startup-report/create',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify all reports were created
        assert StartupReportDbModel.objects.count() == 3
        assert StartupReportDbModel.objects.filter(name='Startup A').exists()
        assert StartupReportDbModel.objects.filter(name='Startup B').exists()
        assert StartupReportDbModel.objects.filter(name='Startup C').exists()

    def test_create_with_empty_names_list(self, client):
        """Test creating reports with an empty names list returns error."""
        payload = {'names': []}

        response = client.post(
            '/api/startup-report/create',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 400
        # Verify no reports were created
        assert StartupReportDbModel.objects.count() == 0

    def test_create_with_missing_names_field(self, client):
        """Test creating reports without names field returns error."""
        payload = {}

        response = client.post(
            '/api/startup-report/create',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 422  # Unprocessable entity from pydantic validation
        # Verify no reports were created
        assert StartupReportDbModel.objects.count() == 0

    def test_create_without_prompt(self, client):
        """Test creating reports when no prompt exists returns error."""
        payload = {'names': ['Test Startup']}

        response = client.post(
            '/api/startup-report/create',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 400
        # Verify no reports were created
        assert StartupReportDbModel.objects.count() == 0


@pytest.mark.django_db
class TestDeleteStartupReports:
    """Tests for POST /api/startup-report/delete endpoint."""

    def test_delete_single_report(self, client):
        """Test deleting a single startup report."""
        # Create a test report
        report = StartupReportDbModel.objects.create(
            name='Test Startup', generation_status='pending'
        )
        report_id = report.id  # type: ignore[reportAttributeAccessIssue]

        payload = {'report_ids': [report_id]}

        response = client.post(
            '/api/startup-report/delete',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify the report was deleted
        assert not StartupReportDbModel.objects.filter(id=report_id).exists()

    def test_delete_multiple_reports(self, client):
        """Test deleting multiple startup reports at once."""
        # Create multiple reports
        report1 = StartupReportDbModel.objects.create(
            name='Startup A', generation_status='pending'
        )
        report2 = StartupReportDbModel.objects.create(
            name='Startup B', generation_status='completed'
        )
        report3 = StartupReportDbModel.objects.create(
            name='Startup C', generation_status='started'
        )

        report_ids = [
            report1.id,  # type: ignore[reportAttributeAccessIssue]
            report2.id,  # type: ignore[reportAttributeAccessIssue]
            report3.id,  # type: ignore[reportAttributeAccessIssue]
        ]

        payload = {'report_ids': report_ids}

        response = client.post(
            '/api/startup-report/delete',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify all reports were deleted
        assert StartupReportDbModel.objects.count() == 0

    def test_delete_with_empty_report_ids_list(self, client):
        """Test deleting reports with an empty report_ids list returns error."""
        payload = {'report_ids': []}

        response = client.post(
            '/api/startup-report/delete',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 400

    def test_delete_with_missing_report_ids_field(self, client):
        """Test deleting reports without report_ids field returns error."""
        payload = {}

        response = client.post(
            '/api/startup-report/delete',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 422  # Unprocessable entity from pydantic validation

    def test_delete_nonexistent_report(self, client):
        """Test deleting a nonexistent report succeeds silently."""
        payload = {'report_ids': [99999]}

        response = client.post(
            '/api/startup-report/delete',
            data=payload,
            content_type='application/json',
        )

        # Should succeed even if report doesn't exist
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True


@pytest.mark.django_db
class TestUpdatePrompt:
    """Tests for POST /api/startup-report/update-prompt endpoint."""

    def test_update_prompt_success(self, client):
        """Test updating the startup report prompt."""
        payload = {'prompt': 'Generate a detailed report on the startup'}

        response = client.post(
            '/api/startup-report/update-prompt',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify the prompt was created in the database
        prompts = StartupReportPromptDbModel.objects.all()
        assert prompts.count() == 1
        assert prompts[0].prompt == 'Generate a detailed report on the startup'

    def test_update_prompt_multiple_times(self, client):
        """Test updating the prompt multiple times creates separate records."""
        # First update
        payload1 = {'prompt': 'First prompt'}
        response1 = client.post(
            '/api/startup-report/update-prompt',
            data=payload1,
            content_type='application/json',
        )
        assert response1.status_code == 200

        # Second update
        payload2 = {'prompt': 'Second prompt'}
        response2 = client.post(
            '/api/startup-report/update-prompt',
            data=payload2,
            content_type='application/json',
        )
        assert response2.status_code == 200

        # Verify both prompts are stored
        prompts = StartupReportPromptDbModel.objects.all().order_by('created_at')
        assert prompts.count() == 2
        assert prompts[0].prompt == 'First prompt'
        assert prompts[1].prompt == 'Second prompt'

    def test_update_prompt_with_empty_string(self, client):
        """Test updating prompt with empty string returns error."""
        payload = {'prompt': ''}

        response = client.post(
            '/api/startup-report/update-prompt',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 400
        # Verify no prompt was created
        assert StartupReportPromptDbModel.objects.count() == 0

    def test_update_prompt_with_whitespace_only(self, client):
        """Test updating prompt with whitespace only returns error."""
        payload = {'prompt': '   '}

        response = client.post(
            '/api/startup-report/update-prompt',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 400
        # Verify no prompt was created
        assert StartupReportPromptDbModel.objects.count() == 0

    def test_update_prompt_with_missing_prompt_field(self, client):
        """Test updating prompt without prompt field returns error."""
        payload = {}

        response = client.post(
            '/api/startup-report/update-prompt',
            data=payload,
            content_type='application/json',
        )

        assert response.status_code == 422  # Unprocessable entity from pydantic validation
        # Verify no prompt was created
        assert StartupReportPromptDbModel.objects.count() == 0


@pytest.mark.django_db
class TestGetCurrentPrompt:
    """Tests for GET /api/startup-report/current-prompt endpoint."""

    def test_get_current_prompt_when_none_exists(self, client):
        """Test getting current prompt when none exists returns empty string."""
        response = client.get('/api/startup-report/current-prompt')

        assert response.status_code == 200
        data = response.json()
        assert 'prompt' in data
        assert data['prompt'] == ''

    def test_get_current_prompt_when_one_exists(self, client):
        """Test getting current prompt when one exists."""
        # Create a prompt
        StartupReportPromptDbModel.objects.create(prompt='Test prompt')

        response = client.get('/api/startup-report/current-prompt')

        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Test prompt'

    def test_get_current_prompt_returns_most_recent(self, client):
        """Test getting current prompt returns the most recently created one."""
        # Create multiple prompts
        StartupReportPromptDbModel.objects.create(prompt='Old prompt')
        StartupReportPromptDbModel.objects.create(prompt='Newer prompt')
        StartupReportPromptDbModel.objects.create(prompt='Newest prompt')

        response = client.get('/api/startup-report/current-prompt')

        assert response.status_code == 200
        data = response.json()
        assert data['prompt'] == 'Newest prompt'


@pytest.mark.django_db
class TestGetStartupReportById:
    """Tests for GET /api/startup-report/{report_id} endpoint."""

    def test_get_report_by_id_success(self, client):
        """Test getting a startup report by its ID."""
        # Create a test report
        report = StartupReportDbModel.objects.create(
            name='Test Startup',
            generation_status='completed',
            read_by_user=True,
            report_text='This is a test report',
        )
        report_id = report.id  # type: ignore[reportAttributeAccessIssue]

        response = client.get(f'/api/startup-report/{report_id}')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == report_id
        assert data['name'] == 'Test Startup'
        assert data['generation_status'] == 'completed'
        assert data['read_by_user'] is True
        assert data['report_text'] == 'This is a test report'
        assert 'created_at' in data
        assert data['prompt_text'] is None

    def test_get_report_by_id_with_prompt(self, client):
        """Test getting a report that has an associated prompt."""
        # Create a prompt
        prompt = StartupReportPromptDbModel.objects.create(
            prompt='Generate a detailed report'
        )

        # Create a report with the prompt
        report = StartupReportDbModel.objects.create(
            name='Test Startup',
            generation_status='completed',
            report_text='Report content',
            prompt=prompt,
        )
        report_id = report.id  # type: ignore[reportAttributeAccessIssue]

        response = client.get(f'/api/startup-report/{report_id}')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == report_id
        assert data['name'] == 'Test Startup'
        assert data['prompt_text'] == 'Generate a detailed report'

    def test_get_report_by_id_not_found(self, client):
        """Test getting a nonexistent report returns 404."""
        response = client.get('/api/startup-report/99999')

        assert response.status_code == 404

    def test_get_report_by_id_invalid_id(self, client):
        """Test getting a report with invalid ID format."""
        response = client.get('/api/startup-report/invalid')

        # Django/Ninja should return 422 for invalid path parameter
        assert response.status_code == 422
