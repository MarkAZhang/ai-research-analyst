import pytest
from django.test import Client

from core.startup_report.db.startup_report_db_model import StartupReportDbModel


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
