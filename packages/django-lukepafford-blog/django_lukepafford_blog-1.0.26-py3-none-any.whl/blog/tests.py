from django.test import TestCase
from datetime import datetime
from .date_conversions import extract_date_from_title


class DateTestCase(TestCase):
    def test_title_extraction(self):
        date = extract_date_from_title("2019-01-20-my-post.md")
        self.assertEqual(isinstance(date, datetime), True)
