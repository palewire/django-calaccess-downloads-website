from django.test import TestCase
from django.core import management


class WebsiteTest(TestCase):

    def test_build(self):
        management.call_command("build")
