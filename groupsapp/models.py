from django.db import models
from django.contrib.auth.models import User
import encrypted_model_fields.fields as e_models


# Create your models here.
# Profile Models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = e_models.EncryptedDateField(name='dob',verbose_name='Date of Birth')

class Member(models.Model):
    #First name, Surname and dob fields describe the member.
    first_name = e_models.EncryptedCharField(max_length=15)
    last_name = e_models.EncryptedCharField(max_length=15)
    dob = e_models.EncryptedDateField(name='dob',verbose_name='Date of Birth')
    GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('U','Unknown: Not Set')
    ]
    gender = e_models.EncryptedCharField(max_length=1,choices=GENDER_CHOICES,default='U')


    def __str__(self):
        return self.first_name +" "+ self.last_name

class Group(models.Model):
    group_name = e_models.EncryptedCharField(max_length=15,unique=False)
    GROUP_CHOICES = [
    ('SE', 'Section'),
    ('GR', 'Group'),
    ('DI', 'District'),
    ('CO', 'County'),
    ]
    group_type = models.CharField(max_length=2,choices=GROUP_CHOICES) #Section/Unit,Group,District,County
    def __str__(self):
        return self.group_name
#Linking tables
class UserMemberLink(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    member = models.ForeignKey(Member,on_delete=models.CASCADE)

class UserGroupLink(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    role = models.CharField(max_length=20)

class MemberGroupLink(models.Model):
    member = models.ForeignKey(Member,on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    role = models.CharField(max_length=20)

class GroupGroupLink(models.Model):
    group1 = models.ForeignKey(Group,on_delete=models.CASCADE,related_name="Group1")
    group2 = models.ForeignKey(Group,on_delete=models.CASCADE,related_name="Group2")

class JoinCode(models.Model):
    code = models.CharField(unique=True,max_length=8)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    maxno = models.IntegerField(default=1)
    def __str__(self):
        return self.code