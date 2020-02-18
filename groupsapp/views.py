from django.shortcuts import render,get_object_or_404,redirect

# Create your views here.
from django.http import HttpResponse
import groupsapp.forms as appforms
import groupsapp.models as appmodels
import groupsapp.functions as func
from django.contrib.auth import login,authenticate
from django.contrib.auth.models import User
from django.contrib import messages



def index(request):
    if request.user.is_authenticated:
        members = func.GetAllUserMembers(request.user)
        groups = func.GetAllMemberGroups(request.user,by_group=True)
        #print(members)
        #return HttpResponse(members)
        context = {
            'user': request.user, 
            'members': members,
            'groups': groups,
        }
        return render(request,'groupsapp/index.html',context=context)
    else:
        return redirect('/accounts/login/')


def profile(request):
    pass
def register(request):
    
    if request.method == 'POST':
        form = appforms.UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account registered')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            #login(request,user)
            return redirect('profile')
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