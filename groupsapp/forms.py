from django.forms import EmailField
from django import forms

from django.forms.widgets import SelectDateWidget

import datetime
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
import groupsapp.models as appmodels
import groupsapp.functions as func
from django.contrib.auth.forms import UserCreationForm




class UserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"),required=True,help_text=_("Required field"))

    class Meta:
        model = appmodels.User
        fields = ["username","email","password1","password2"]

        def save(self, commit=True):
            user = super(UserCreationForm,self).save(commit=False)
            user.email = self.cleaned_data["email"]
            if commit:
                user.save()
            return user

class MemberCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20,required=True)
    last_name = forms.CharField(max_length=20,required=True)
    formats = ['%Y-%m-%d','%d/%m/%Y','%d/%m/%y']
    dob = forms.DateField(label="Date of birth",input_formats=formats)
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
        if not first_name and not last_name and not dob:
            raise forms.ValidationError('Empty fields')
        if not func.ValidateName(first_name) or not func.ValidateName(last_name):
            raise forms.ValidationError('Invalid characters') 
        if dob > datetime.date.today():
            raise forms.ValidationError({'dob': ["Birthday cannot be in the future",]})
    class Meta:
        model = appmodels.Member
        fields = ["first_name","last_name","dob"]

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
    member = forms.ModelChoiceField(appmodels.Member.objects.none(),label="Select Member: ")
    def __init__(self, *args, **kwargs):
        queryset = appmodels.Member.objects.none()

        if kwargs.get('request'):
            self.user = kwargs.pop('request').user
            if self.user:
                queryset = self.GetChoices()
        if kwargs.get('error'):
            raise forms.ValidationError(kwargs.pop('error'))
        super(JoinCodeForm, self).__init__(*args, **kwargs)
        
        self.fields['member'].queryset = queryset

    def GetChoices(self):
        members= func.GetAllUserMembers(self.user)
        print(members)
        return members
    
    def clean(self):
        cleaned_data = super(JoinCodeForm, self).clean()
        code = cleaned_data.get('code')
        if code[0] == "M":
            member = cleaned_data.get('member')
        if len(code) != 8:
            raise forms.ValidationError('Code must be 8 characters long')
        if not code:
            raise forms.ValidationError('Empty code')
        if not func.ValidateName(code):
            raise forms.ValidationError('Invalid characters')
        #if error != True:
            #raise forms.ValidationError(error)

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