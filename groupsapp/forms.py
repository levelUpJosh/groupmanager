from django.forms import EmailField
from django import forms
import django.contrib.auth.forms as contribforms
from django.forms.widgets import SelectDateWidget

import datetime
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
import groupsapp.models as appmodels
import groupsapp.functions as func
from django.contrib.auth.forms import UserCreationForm




class UserCreationForm(contribforms.UserCreationForm):
    username = forms.CharField(label="Username")
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    password1= forms.CharField(label="Password",widget=forms.PasswordInput())
    password2 =forms.CharField(label="Confirm Password",widget=forms.PasswordInput())
    email = forms.EmailField(label=_("Email address"),required=True)
    formats = ['%Y-%m-%d','%d/%m/%Y','%d/%m/%y']
    this_year = datetime.date.today().year
    years = range(this_year,this_year-100,-1)
    dob = forms.DateField(label="Date of birth",input_formats=formats,widget=forms.SelectDateWidget(years=years))
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.user = kwargs.get('instance')
        print(self.user)

    def clean(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        dob = self.cleaned_data.get("dob")
        #Enforcing the minimum age of 18, but only if dob is given.
        #dob would not be given when editing the User Profile because it is only checked when registering an account.
        if dob and (18 > ((datetime.date.today() - dob).days)/365.25):
            raise forms.ValidationError({'dob': ["Users must be at least 18 years old due to data consent laws",]})
        if self.user:
            #When editing an existing user, the program uses the user id to exclude the current username and email from checks for existing records
            user_id = self.user.id
        else:
            #If user is not given then this tells the program it is not dealing with an existing user.
            #This means that username should not beconsidered in the filter lines below when registering a new user.
            user_id = 0
        
        if not func.ValidateName(username):
            raise forms.ValidationError({'username': ["Name has invalid characters",]})
        if appmodels.User.objects.filter(username=username).exclude(id=user_id).exists():

            raise forms.ValidationError({'username': ["Username is not available",]})
        if appmodels.User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError({'email': ["Email is already taken",]})
        
    class Meta:
        model = appmodels.User
        fields = ["username","email","first_name","last_name","dob","password1","password2"]

        def save(self, commit=True):
            user = super(UserCreationForm,self).save(commit=False)
            if commit:
                user.save()
            return user

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password= forms.CharField(label="Password",widget=forms.PasswordInput())

    class Meta:
        model = appmodels.User
        fields = ["username","password"]


class MemberCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20,required=True)
    last_name = forms.CharField(max_length=20,required=True)
    formats = ['%Y-%m-%d','%d/%m/%Y','%d/%m/%y']
    dob = forms.DateField(label="Date of birth",input_formats=formats)
    gender = forms.ChoiceField(choices=appmodels.Member.GENDER_CHOICES)
    def __init__(self, *args, **kwargs):
        super(MemberCreationForm, self).__init__(*args, **kwargs)
        this_year = datetime.date.today().year
        years = range(this_year,this_year-100,-1)
        #need to add constraint to stop births entered in the future
        #years.reverse()
        self.fields["dob"].widget = SelectDateWidget(years=years)
    
    def clean(self):
        cleaned_data = super(MemberCreationForm, self).clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        dob = cleaned_data.get('dob')
        gender = cleaned_data.get('gender')
        if not first_name and not last_name and not dob:
            raise forms.ValidationError('Empty fields')
        if not func.ValidateName(first_name) or not func.ValidateName(last_name):
            raise forms.ValidationError('Invalid characters') 
        if dob > datetime.date.today():
            raise forms.ValidationError({'dob': ["Birthday cannot be in the future",]})
    class Meta:
        model = appmodels.Member
        fields = ["first_name","last_name","dob","gender"]

        def save(self, commit=True):
            member = super(MemberCreationForm,self).save(commit=False)
            if commit:
                member.save()
            return member

class GroupCreationForm(forms.ModelForm):
    group_name = forms.CharField(max_length=15)
    group_type = forms.ChoiceField(choices=appmodels.Group.GROUP_CHOICES)
    def clean(self):
        cleaned_data = super(GroupCreationForm, self).clean()
        group_name = cleaned_data.get('group_name')
        group_type = cleaned_data.get('group_type')
        if not group_name and not group_type:
            raise forms.ValidationError('Empty fields')
        if not func.ValidateName(group_name, digits=True) :
            raise forms.ValidationError('Invalid characters') 
    class Meta:
        model = appmodels.Group
        fields = ["group_name","group_type"]

        def save(self, commit=True):
            group = super(GroupCreationForm,self).save(commit=False)
            if commit:
                group.save()
            return group

class JoinCodeForm(forms.Form):
    code = forms.CharField(max_length=8)
    member = forms.ModelChoiceField(appmodels.Member.objects.none(),label="Select Member: ",required=False)
    def __init__(self, *args, **kwargs):
        queryset = appmodels.Member.objects.none()

        if kwargs.get('request'):
            self.user = kwargs.pop('request').user
            if self.user:
                queryset = self.GetChoices()
        super(JoinCodeForm, self).__init__(*args, **kwargs)
        
        self.fields['member'].queryset = queryset

    def GetChoices(self):
        members= func.GetAllUserMembers(self.user)
        return members
    
    def clean(self):
        cleaned_data = super(JoinCodeForm, self).clean()
        code = cleaned_data.get('code')
        # If first letter is 'M'
        if code[0] == "M":
            member = cleaned_data.get('member')
        #Length must be exactly 8 characters
        if len(code) != 8:
            raise forms.ValidationError('Code must be 8 characters long')
        #Code field must be populated
        if not code:
            raise forms.ValidationError('Empty code')
        #Code must only have letters
        if not func.ValidateName(code):
            raise forms.ValidationError('Invalid characters')


class NewJoinCodeForm(forms.Form):
    maxno = forms.IntegerField(min_value=1)
    role = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(NewJoinCodeForm, self).__init__(*args, **kwargs)
        self.fields['role'].choices = choices
        print(choices)

    def clean(self):
        cleaned_data = super(NewJoinCodeForm, self).clean()
        maxno = cleaned_data.get('maxno')
        role = cleaned_data.get('role')
        if not maxno and not role:
            raise forms.ValidationError('Empty fields')

"""class JoinCodeForm(forms.Form):
    def __init__(self,*args,**kwargs):
        self.user= kwargs.pop('user')
        members = func.GetAllUserMembers(self.user)
        self.code = forms.CharField(max_length=8)
        self.member = forms.ModelChoiceField(queryset=members)
        super(JoinCodeForm, self).__init__(*args, **kwargs)
    class Meta:
        fields = ['code','member']

"""