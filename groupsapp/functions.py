import groupsapp.models as appmodels
import string,random
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist


def CheckUserMemberLink(user,member_id):
	members=GetAllUserMembers(user)
	try:
		member = appmodels.Member.objects.get(id=member_id)
	except ObjectDoesNotExist:
		#If the object is not found, then return false
		return False

	if member in members:
		#Returns true if user has access to the member's info
		return True
	else:
		#If user does not have access to the member, then act as though it doesn't exist.
		return False


def GetAllUserMembers(search):
	if search.__class__.__name__ == 'User':
		memberlist= appmodels.UserMemberLink.objects.filter(user_id=search.pk)
		memberlist = appmodels.Member.objects.filter(pk__in=memberlist.all().values_list('member_id'))
		return memberlist
	elif search.__class__.__name__ == 'Member':
		userlist = appmodels.UserMemberLink.objects.filter(member_id=search.pk)
		userlist = appmodels.User.objects.filter(pk__in=userlist.all().values_list('user_id'))
		return userlist
	else:
		return 'Unsupported object type. Please input a User or Member object.'

""" def GetAllUserGroups(search):
	if search.__class__.__name__ == 'User':
		grouplist= appmodels.UserGroupLink.objects.filter(user_id=search.pk)
		grouplist = appmodels.Group.objects.filter(pk__in=memberlist.all().values_list('group_id'))
		return grouplist
	elif search.__class__.__name__=='Group':
		userlist = appmodels.UserGroupLink.objects.filter(group_id=search.pk)
		userlist = appmodels.User.objects.filter(pk__in=memberlist.all().values_list('group_id'))
	else:
		return 'Unsupported object type. Please input a User object.' """

def GetAllMemberGroups(search,by_group=False):
	from  itertools import chain 
	#Despite the name, this function supports both members and users. The object's type is detected and if it is a user then the function scans and returns ALL associated member groups.
	if search.__class__.__name__ == 'User':
		#print('user')
		#First get a QuerySet of all the Members attached to the User
		search = GetAllUserMembers(search)
		#print(search)
		#Set up empty lists
		membertrack = []
		grouptrack = []

		#iterate through the search to get all groups for all members and make a list
		for member in search:
			#print(member)
			grouplist = appmodels.MemberGroupLink.objects.filter(member_id=member.id)
			grouplist = appmodels.Group.objects.filter(pk__in=grouplist.all().values_list('group_id'))
			membertrack += [[member,grouplist]]
		if by_group == True:
			#If request, we want to sort the current list so that Members are grouped by their Group, rather than the other way around 
			for item in membertrack:
				member = item[0]
				#iterate through the previous list made
				#print(item[1].all())
				if not item[1]:
					#Retrospectively add in a 'No Group' entry for items with empty grouplist QuerySet objects
					item[1] = ['No Group']
				for group in item[1]:
					#Iterate through each group in a member's list
					if group in chain(*grouptrack):
						#check if the group is already entered
						for i in range(0,len(grouptrack)):
							#find where the Group is entered
							try:
								grouptrack[i].index(group)
								location = i
							except:
								pass
						#append the member to the correct location
						grouptrack[location][1].append(member)
						
						
					else:
						#add the group to the list if it's not been entered previously
						grouptrack += [[group,[member]]]
						#print(group)
						
				#print(grouptrack)

			
			return grouptrack
			#print(membertrack)
	elif search.__class__.__name__ == 'Member':
		#print('member')
		grouplist = appmodels.MemberGroupLink.objects.filter(member_id=search.pk)
		grouplist = appmodels.Group.objects.filter(pk__in=grouplist.all().values_list('group_id'))
		#print(grouplist.first().group_id,flush=True)
		membertrack = [search,grouplist]
		#Function is handled better if all data is output in the same way even if only one member is being searched
	else:
		return 'Unsupported object type. Please input a User or Member object'
	return membertrack
def GetAllUserGroups(search):
	returnlist = []
	if search.__class__.__name__ == 'User':
		grouplist= appmodels.UserGroupLink.objects.filter(user_id=search.pk)
		for link in grouplist:
			role = link.role
			group = appmodels.Group.objects.get(pk=link.group_id)
			returnlist += [[group,role]]
		return returnlist
	elif search.__class__.__name__ == 'Group':
		userlist = appmodels.UserGroupLink.objects.filter(group_id=search.pk)
		for link in userlist:
			role = link.role
			user = appmodels.User.objects.get(pk=link.user_id)
			returnlist += [[user,role]]
		return returnlist
	else:
		return 'Unsupported object type. Please input a User or Member object.'

def CheckJoinCodeExists(code):
	#Checks for and returns the JoinCode onject
	try:
		JoinObject = appmodels.JoinCode.objects.get(code=code)
		return JoinObject
	except:
		return False
def CheckJoinCodeNotUsed(member,group):
	inputObjectType = member.__class__.__name__
	#Checks that a JoinCode has not already been used by the same member for this group
	#objectType determines whether the member parameter is treated as a member object or a user object, depending on the link type
	try:
		if inputObjectType == 'Member':
			appmodels.MemberGroupLink.objects.get(group=group,member=member)
		if inputOobjectType == 'User':
			appmodels.UserGroupLink.objects.get(group=group,user=member)

		return False
	except:
		return True
def GenerateJoinCode(group,role='member',maxno=1):
	letters = string.ascii_uppercase
	#An odd issue of using random sequences of the full alphabet is that there is a small chance that the code could spell out words, some of which groups may not wish to distribute to parents.
	#This might not be too favourable so we'll remove the vowels from the letter selection,
	letters = letters.translate({ord('A'): None, ord('E'): None, ord('I'): None, ord('O'): None, ord('U'): None})
	generated = False
	while generated == False:
		code = ''
		for i in range(7):
			code += random.choice(letters)
		if role == 'member':
			code = 'M'+code
		else:
			code = 'L'+code
		if not appmodels.JoinCode.objects.filter(code=code):
			new = appmodels.JoinCode(code=code,group=group,role=role,maxno=maxno)
			new.save()
			generated = True
			return new
def UseJoinCode(code,member):
	#Method to use JoinCode provided by the user facing form.
	#member in this case can actually represent a member or user object, which object is used depends on the role entry in the JoinCode object
	JoinObject = CheckJoinCodeExists(code)

	
	#inputObjectType helps to deal with the hopefully unlikely problem that a code may include the correct attributes for 'member' but member may be provided as a 'User' object (intended for Leader role codes only) and vice versa.
	#The javascript in the joingroup.html file SHOULD prevent this being necessary but in case of finding a way to use the console to enter into the member field when it is hidden
	inputObjectType = member.__class__.__name__
	if JoinObject != False:
		is_not_used = CheckJoinCodeNotUsed(member,JoinObject.group)
		group = appmodels.Group.objects.get(pk=JoinObject.group_id) # What if the group no longer exists. I suppose a delete group function would also scrap the joincodes
		if is_not_used == True and JoinObject.role == 'member':
			if inputObjectType == 'Member':
				mglink = appmodels.MemberGroupLink(member=member,group=group,role=JoinObject.role).save()
				JoinObject.maxno -= 1
				JoinObject.save()
				if JoinObject.maxno == 0:
					JoinObject.delete()
				return True
			else:
				return 'This code can only be associated with a member object.'
		elif is_not_used == True and JoinObject.role in ['leader','admin']:
			if inputObjectType == 'User':
				uglink = appmodels.UserGroupLink(user=member,group=group,role=JoinObject.role).save()
				JoinObject.maxno -= 1
				JoinObject.save()

				if JoinObject.maxno == 0:
					JoinObject.delete()
				return True
			else:
				return 'This code can only be associated with a user, but a member object was provided.'
		else:
			return 'Member/User and Group are already linked'
	else:
		return 'Code does not exist'

def ValidateName(name,digits=False):
	letters = string.ascii_letters+" "
	if digits == True:
		letters += string.digits
	if any((c not in letters) for c in name):
		return False
	else:
		return True