from django.shortcuts import render,get_object_or_404,redirect

# Create your views here.
from django.urls import reverse
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
            if request.method == "POST":
                form = appforms.MemberCreationForm(request.POST, instance=member)
                if form.is_valid():
                    form.save()
            form = appforms.MemberCreationForm(instance=member)
            context = {
                'member': member,
                'groups': func.GetAllMemberGroups(member)[1],
                'form': form
            }
            return render(request,'groupsapp/objects/member/profile.html',context=context)
        else:
            return HttpResponse("No exist")
    else:
        return redirect('login')
def delete_view(request,object_id,objectType):
    if request.user.is_authenticated and request.method == "POST":
        print("ok",flush=True)
        if objectType == "member":
            print("member",object_id)
            if func.CheckUserMemberLink(request.user,object_id):
                appmodels.Member.objects.get(id=object_id).delete()
    return redirect('index')


def groupprofile(request,group_id):
    if request.user.is_authenticated:
        group = appmodels.Group.objects.get(id=group_id)
        membergroups = func.GetAllMemberGroups(request.user)
        print(membergroups,flush=True)

        return HttpResponse(group)
def groupadmin(request,group_id):
    if request.user.is_authenticated:
        group = appmodels.Group.objects.get(id=group_id)
        joincodes = func.GetAllJoinCodes(group)
        users = func.GetAllUserGroups(group)
        members = func.GetAllMembersInGroup(group)
        for i in range(len(users)):
            #Checks if a user has admin control over this page
            if request.user in users[i]:
                if users[i][1] == 'admin':
                    choices = [('member','member'),('leader','leader')]
                else:
                    choices = [('member','member')]
                #print(users[i])
                context = {
                    'group': group,
                    'users': users,
                    'members': members,
                    'joincodes': joincodes,
                    'codeform': appforms.NewJoinCodeForm(choices=choices),
                    'role': users[i][1],
                }
                return render(request,'groupsapp/objects/group/admin.html',context=context)
    return redirect('index')


def groupadmintask(request,group_id,admin=False,*args,**kwargs):
    group = appmodels.Group.objects.get(id=group_id)
    usergroups = func.GetAllUserGroups(group)
    for i in range(len(usergroups)):
        #Checks if a user has admin control over this page
        if request.user in usergroups[i]:
            admin = True
    if request.user.is_authenticated and admin == True and request.method=="POST":
        task = kwargs.get('task')
        if task == "remove_member":
            member_id = kwargs.get('member_id')
            appmodels.MemberGroupLink.objects.get(member_id=member_id,group_id=group.id).delete()
        elif task == "delete_code":
            code = kwargs.get('code')
            print(code)
            #For security reasons, the get command considers both the group id and the code, not just the code.
            #This should minimise the ability to delete objects not belonging to a user
            appmodels.JoinCode.objects.get(code=code,group=group.id).delete()
        elif task == "generate_code":
            print("gen")
            form = appforms.NewJoinCodeForm(request.POST)
            if form.is_valid():
                func.GenerateJoinCode(group,role=form.cleaned_data['role'],maxno=form.cleaned_data['maxno'])
        return redirect("groupadmin",group_id)
    return HttpResponse(status=204)

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
        return redirect('index')

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
        return redirect('index')

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
                else:
                    code = func.UseJoinCode(code,request.user)
                    
                if code != True:
                    error = code
                    form = appforms.JoinCodeForm(request=request)
                else:
                    messages.success(request,'Group joined')
        else:
            form = appforms.JoinCodeForm(request=request)
            error ='' 
        return render(request, 'groupsapp/components/joingroup.html', {'form': form,'error':error})
    else:
        return redirect('index')

def access_denied(request):
    return render(status=403)
""" def login(request):
    if request.method == 'POST':
        form = """