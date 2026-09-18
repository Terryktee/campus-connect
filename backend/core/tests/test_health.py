from django.test import Client, TestCase


class HealthCheckTests(TestCase):
    def test_health_check_reports_database_status_without_caching(self):
        response = Client().get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")
