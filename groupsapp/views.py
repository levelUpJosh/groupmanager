from django.shortcuts import render,get_object_or_404,redirect

# Create your views here.
from django.http import HttpResponse
import groupsapp.forms as appforms
import groupsapp.models as appmodels
import groupsapp.functions as func
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as loginfunc
from django.contrib.auth.models import User
from django.contrib import messages

import groupsapp.emails as emails
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context

def login(request):
    if request.method == 'POST':
        form = appforms.UserLoginForm(request.POST)
        if form.is_valid():
            #form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            print(user,username,password)
            if user is not None:
                messages.success(request,'Account Logged in')
            #request.login(user)
                loginfunc(request,user)
                print("PPPP")
            else:
                messages.error(request,'Username or password is incorrect')
            return redirect('index')
    else:
        form =  appforms.UserLoginForm()
    return render(request, 'groupsapp/login.html', {'form': form})

def logoutpage(request):
    if request.method ==  'POST':
        logout(request)
        # Redirect
        return redirect('index')

def index(request):
    if request.user.is_authenticated:
        members = func.GetAllUserMembers(request.user)
        groups = func.GetAllMemberGroups(request.user,by_group=True)
        usergroups = func.GetAllUserGroups(request.user)
        #print(members)
        #return HttpResponse(members)
        context = {
            'members': members,
            'groups': groups,
            'usergroups': usergroups,
        }
        return render(request,'groupsapp/index.html',context=context)
    else:
        return redirect('login')


def memberprofile(request,member_id):
    if request.user.is_authenticated:
        if func.CheckUserMemberLink(request.user,member_id):
            member = appmodels.Member.objects.get(id=member_id)
            context = {
                'member': member,
                'groups': func.GetAllMemberGroups(member),
            }
            return render(request,'groupsapp/objects/member/profile.html',context=context)
        else:
            return HttpResponse("No exist")
    else:
        return redirect('login')

def groupprofile(request,group_id):
    if request.user.is_authenticated:
        group = appmodels.Group.objects.get(id=group_id)
        usergroups = func.GetAllUserGroups(group)
        membergroups = func.GetAllMemberGroups(request.user)
        print(membergroups,flush=True)
        groups1 = ""
        for i in range(len(usergroups)):
            #Checks if a user has admin control over this page
            if request.user in usergroups[i]:
                groups1 += "user"
        for i in range(len(membergroups)):
            #Checks if a user has read-only access
            if group in membergroups[i][1]:
                groups1 += "member"

        return HttpResponse(groups1)
def register(request):
    
    if request.method == 'POST':
        form = appforms.UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account registered')
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            #login(request,user)
            loginfunc(request,user)
            #emails.welcome(username,email)
            return redirect('index')
    else:
        form =  appforms.UserCreationForm()
    return render(request, 'groupsapp/register.html', {'form': form})

def add_member(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = appforms.MemberCreationForm(request.POST)
            if form.is_valid():
                member = form.save()
                link = appmodels.UserMemberLink(user=request.user,member=member).save()

                messages.success(request,'Member created')
                
        else:
            form = appforms.MemberCreationForm()
        return render(request, 'groupsapp/components/addmember.html', {'form': form})
    else:
        return HttpResponse('User not logged in',status=403)

def add_group(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = appforms.GroupCreationForm(request.POST)
            if form.is_valid():
                group = form.save()
                code = func.GenerateJoinCode(group)
                appmodels.UserGroupLink(user=request.user,group=group,role='admin').save()
                messages.success(request,'Group created')
                
        else:
            form = appforms.GroupCreationForm()
        return render(request, 'groupsapp/components/addgroup.html', {'form': form})
    else:
        return HttpResponse('User not logged in',status=403)

def join_group(request,error=''):
    print(request.user,flush=True)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = appforms.JoinCodeForm(data=request.POST,request=request)
            if form.is_valid():
                code= form.cleaned_data['code']
                if code[0] == 'M':
                    member=form.cleaned_data['member']
                    code = func.UseJoinCode(code,member)
                    messages.success(request,'Group joined')
                else:
                    code = func.UseJoinCode(code,request.user)
                    messages.success(request,'Group joined')
                if code != True:
                    form = appforms.JoinCodeForm(request=request,error=code)
        else:
            form = appforms.JoinCodeForm(request=request)
        return render(request, 'groupsapp/components/joingroup.html', {'form': form})
    else:
        return HttpResponse('User not logged in',status=403)

""" def login(request):
    if request.method == 'POST':
        form = """