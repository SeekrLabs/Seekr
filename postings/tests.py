from django.test import TestCase
from .models import Posting


class ProfileTestCase(TestCase):
    def test_posting_image(self):
        p = Posting.objects.all()[0]
        p.generate_image()
        