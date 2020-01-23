import groupsapp.models as appmodels
import string,random

def GetAllUserMembers(search,reverse=False):
	if reverse == False:
		memberlist= appmodels.UserMemberLink.objects.filter(user_id=search.pk)
		memberlist = appmodels.Member.objects.filter(pk__in=memberlist)
		return memberlist
	else:
		userlist = appmodels.UserMemberLink.objects.filter(member_id=search.pk)
		userlist = appmodels.User.objects.filter(pk__in=userlist)
		return userlists




def CheckJoinCodeExists(code):
	try:
		JoinObject = appmodels.JoinCode.objects.get(code=code)
		return JoinObject
	except:
		return False
def CheckJoinCodeNotUsed(member,group):
	#Checks that a JoinCode has not already been used by the same member for this group
	try:
		appmodels.MemberGroupLink.objects.get(group=group,member=member)
		return False
	except:
		return True

def GenerateJoinCode(group,role='member',maxno=1):
	letters = string.ascii_uppercase
	generated = False
	while generated == False:
		if role == 'member':
			code = 'M'.join(random.choice(letters) for i in range(7))
		else:
			code = 'L'.join(random.choice(letters) for i in range(7))
		if not appmodels.JoinCode.objects.filter(code=code):
			new = appmodels.JoinCode(code=code,group=group,role=role,maxno=maxno)
			new.save()
			generated = True
			return new

def UseJoinCode(code,member):
	#Method to use JoinCode provided by the user facing form.
	JoinObject = CheckJoinCodeExists(code)
	if JoinObject != False:
		group = appmodels.Group.objects.get(pk=JoinObject.group_id)
		if CheckJoinCodeNotUsed(member,group) and JoinObject.role == 'member':
			mglink = appmodels.MemberGroupLink(member=member,group=group,role=JoinObject.role).save()
			JoinObject.maxno -= 1
			JoinObject.save()
			if JoinObject.maxno == 0:
				JoinObject.delete()
			return True
		else:
			return 'Member and group are already linked'
	else:
		return 'Code does not exist'

def ValidateName(name,digits=False):
	letters = string.ascii_letters
	if digits == True:
		letters += string.digits
	if any((c not in letters) for c in name):
		return False
	else:
		return True