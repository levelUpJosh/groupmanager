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
""" def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    return context
 """
def login(request):
    #Custom login page provided via a form from forms.py
    if request.method == 'POST':
        #Load form
        form = appforms.UserLoginForm(request.POST)
        #Check if the form returned is valid
        if form.is_valid():
            #Extract the relevant information from the form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            #Use the information to attempt to verify the account exists and is a valid password
            user = authenticate(username=username,password=password)
            #If the authenticate line doesn't work it will return None, so check that user is not None
            if user is not None:
                messages.success(request,'Account Logged in')
                #Use django's login function (defined with a different name due to conflict with this functions name) to initiate the user session
                loginfunc(request,user)

            else:
                #Return a helpful error message if the username or password is wrong
                messages.error(request,'Username or password is incorrect')
            return redirect('index')
    else:
        form =  appforms.UserLoginForm()
    return render(request, 'groupsapp/login.html', {'form': form})

def logoutpage(request):
    if request.method ==  'POST' and request.user.is_authenticated:
        logout(request)
        messages.success(request,'User logged out')
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

def userprofile(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            ### I attempted to make it possible for users to edit their own username and email.
            ### It proved more difficult than i expected so this currently does not work.
            form = appforms.UserCreationForm(data=request.POST,instance=user)
            if form.is_valid():
                form.save()
        else:
            form = appforms.UserCreationForm(instance=user)
        context = {
            'user': user,
            'groups': func.GetAllUserGroups(user),
            'form': form,
        }
        return render(request,'groupsapp/objects/user/profile.html',context=context)
    else:
        return redirect('login')

def memberprofile(request,member_id,group_id=None):
    if request.user.is_authenticated:
        #The lines below define whether the current request has access due to user rights or indirectly by accessing via a group.
        owned_by_user = func.CheckUserMemberLink(request.user,member_id)
        owned_by_group = func.CheckMemberGroupLink(group_id,member_id)
        if owned_by_user or owned_by_group:
            member = appmodels.Member.objects.get(id=member_id)
            if request.method == "POST":
                form = appforms.MemberCreationForm(request.POST, instance=member)
                if form.is_valid():
                    form.save()
            if owned_by_user:
                users = request.user
            else:
                users = func.GetAllUserMembers(member)
            form = appforms.MemberCreationForm(instance=member)
            context = {
                'member': member,
                'owned_by_user': owned_by_user,
                'owned_by_group': owned_by_group,
                'users': users,
                'group_id': group_id, # This exists to allow us to prevent admins of one group removing a member from another
                'groups': func.GetAllMemberGroups(member)[1],
                'form': form
            }
            return render(request,'groupsapp/objects/member/profile.html',context=context)
        else:
            return HttpResponse("No exist")
    else:
        return redirect('login')

def memberprofiletask(request,member_id,*args,**kwargs):
    return HttpResponse(status=204)


def delete_view(request,object_id,objectType):
    if request.user.is_authenticated and request.method == "POST":
        if objectType == "member":
            if func.CheckUserMemberLink(request.user,object_id):
                appmodels.Member.objects.get(id=object_id).delete()
                messages.success(request,'Member deleted')
        if objectType == "user":
            #Check the user attempting to delete their account is this user
            #Also check that User is not an admin of any groups as that will break the group
            if object_id == request.user.id:
                if not func.UserIsAdmin(request.user):
                    
                    for member in func.GetAllUserMembers(request.user):
                        print(member)
                        member.delete()
                    appmodels.User.objects.get(id=object_id).delete()
                    messages.success(request,'User deleted')

                else:
                    messages.error(request,"User could not be deleted due to admin ownership of one or more group. Please delete those groups first and try again")
        return redirect('user')
    return redirect('index')


def groupprofile(request,group_id):
    if request.user.is_authenticated:
        group = appmodels.Group.objects.get(id=group_id)
        membergroups = func.GetAllMemberGroups(request.user)
        usergroups = func.GetAllUserGroups(request.user)
        members = []
        userrole = None
        has_access = False
        for link in membergroups:
            if group in link[1]:
                members += [link[0]]
                has_access = True
        for link in usergroups:
            if group in link:
                has_access = True
                userrole = link[1]
        context ={
            'group': group,
            'user': request.user,
            'role': userrole,
            'members': members,
        }
        if has_access == True:
            return render(request,'groupsapp/objects/group/profile.html',context=context)
        else:
            messages.error(request, "Access Denied or Group Not Found")
            return redirect('index')
    else:
        return redirect('login')


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
                    'pageuser': request.user,
                    'members': members,
                    'joincodes': joincodes,
                    'codeform': appforms.NewJoinCodeForm(choices=choices),
                    'role': users[i][1],
                }
                return render(request,'groupsapp/objects/group/admin.html',context=context)
    messages.error(request,'Access Denied: Only Admins & Leaders can access this page')
    return redirect('index')


def groupadmintask(request,group_id,admin=False,*args,**kwargs):
    # This view acts as an interface for the group admin pages to carry out functions involving adjusting the live database 
    group = appmodels.Group.objects.get(id=group_id)
    #get the Group object
    usergroups = func.GetAllUserGroups(group)
    #obtain the queryset of all User objects that have access to this group
    print(kwargs)
    for i in range(len(usergroups)):
        #Checks if a user has admin control over this page
        if request.user in usergroups[i]:
            admin = True
            if usergroups[i][1] == 'admin':
                role = 'admin'
            else:
                role ='leader'
    task = kwargs.get('task')
    if request.user.is_authenticated and admin == True and request.method=="POST":
        if task == "remove_member":
            #Obtain the specific MemberGroupLink for the member_id and group_id and delete the database record.
            member_id = kwargs.get('object_id')
            appmodels.MemberGroupLink.objects.get(member_id=member_id,group_id=group.id).delete()
            messages.success(request,'Member removed')
            
        elif task == "delete_code":
            #For security reasons, the program considers both the group id and the code, not just the code.
            #This should minimise the ability to delete joincode objects not belonging to a user/group.
            code = kwargs.get('code')
            appmodels.JoinCode.objects.get(code=code,group=group.id).delete()
            messages.success(request,'Code deleted')

        elif task == "generate_code":
            #This code should mirror the relevant code in the groupadmin view
            if role == 'admin':
                choices = [('member','member'),('leader','leader')]
            else:
                choices = [('member','member')]
            #Receive the data from the admin page as a form which includes maxno and role as well as the group_id.
            form = appforms.NewJoinCodeForm(request.POST,choices=choices)
            

            if form.is_valid():
                code =func.GenerateJoinCode(group,role=form.cleaned_data['role'],maxno=form.cleaned_data['maxno'])
                messages.success(request,'Join code generated: '+code.code)
        elif task == "leave_group" and role != "admin":
            appmodels.UserGroupLink.objects.get(group_id=group.id,user_id=request.user.id).delete()
            messages.success(request,"Successfully left "+group.group_name+". To rejoin, another join code must be issued.")
            return redirect('index')
        if role == 'admin':
            if task == "remove_user":
                user_id = kwargs.get('object_id')
                print(user_id,group_id)
                appmodels.UserGroupLink.objects.get(group_id=group.id,user_id=user_id).delete()
                messages.success(request,'User removed')

            elif task == "delete_group":
                group.delete()
                messages.success(request,"Group deleted")
                return redirect('index')
        return redirect("groupadmin",group_id)
    else:
        #Users should also be able to remove their own members from groups as well.
        if task == 'remove_member':
            member_id = kwargs.get('object_id')
            #Check if user has direct ownership of the given member
            if func.CheckUserMemberLink(request.user,member_id):
                #delete link
                appmodels.MemberGroupLink.objects.get(member_id=member_id,group_id=group.id).delete()
                #Show success message
                messages.success(request,'Member successfully removed from '+group.group_name)
                return redirect('index')

    return HttpResponse(status=204)
    # We only return a HttpResponse containing the status 204 (No content)
    # This tells the browser not to render a new page or change the URL which means that users appear to not leave the admin page

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    elif request.method == 'POST':
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
                    messages.error(request,code)
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