from django.test import TestCase
import groupsapp.functions as func
import groupsapp.models as appmodels
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# Create your tests here.
class UserTest(TestCase):
    def setUp(self):
        User.objects.create_user('test','test@test.com','test2')
        appmodels.Member(first_name="Member",last_name="Test",dob="2011-10-05",gender="M").save()
        appmodels.Group(group_name="TestGroup",group_type="GR").save()


    def test_user_can_login(self):
        """Asserts that user can successfully log in."""
        self.user = authenticate(username="test",password="test2")
        self.assertTrue(self.user.is_authenticated)

    def test_user_can_change_password(self):
        self.user = authenticate(username="test",password="test2")
        self.user.set_password('new')
        self.user.save()
        self.user = authenticate(username="test",password='new')
        self.assertTrue(self.user.is_authenticated)
        self.user.set_password('test2')
        self.user.save()

    def test_user_can_retrieve_members(self):
        self.user = authenticate(username="test",password="test2")
        member = appmodels.Member.objects.get(first_name="Member")
        appmodels.UserMemberLink(user=self.user,member=member).save()
        search = func.GetAllUserMembers(self.user)
        self.assertTrue(member in search)
        
    def test_user_can_join_group(self):
        user = authenticate(username="test",password="test2")
        group = appmodels.Group.objects.get(group_name="TestGroup")
        code = func.GenerateJoinCode(group,role='leader')
        func.UseJoinCode(code,user)
        print(func.GetAllUserGroups(group),user)
        self.assertTrue(user in func.GetAllUserGroups(group)[0])
