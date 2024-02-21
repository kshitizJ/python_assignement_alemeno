from django.test import TestCase
from rest_framework.test import APIClient

class CustomerTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'monthly_income': 5000,
            'phone_number': '1234567890'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, 201)

    def test_view_loans_by_customer(self):
        response = self.client.get('/api/view-loans/1/')
        self.assertEqual(response.status_code, 200)