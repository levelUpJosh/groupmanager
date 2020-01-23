from django.test import TestCase
import groupsapp.functions as func
import groupsapp.models as appmodels
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# Create your tests here.
class UserTest(TestCase):
    def setUp(self):
        User.objects.create_user('test','test@test.com','test2')
    def test_user_can_login(self):
        """Asserts that user can successfully log in."""
        self.user = authenticate(username="test",password="test2")
        print(user)
        self.assertTrue(user.is_authenticated)
    def test_user_can_change_password(self):
        user = User.objects.get(username='test')
        user.set_password('new')
        user.save()
        user = authenticate(username="test",password='new')
        self.assertTrue(user.is_authenticated)
        user.set_password('test2')
        user.save()
