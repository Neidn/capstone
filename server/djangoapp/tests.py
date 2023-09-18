from django.test import TestCase
import os

app_path = 'djangoapp'


# Create your tests here.
class PageTest(TestCase):
    def test_about_page(self):
        # Check if the response is 200 OK.
        url = f'/{app_path}/about'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        # Check if the response is 200 OK.
        url = f'/{app_path}/contact'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
