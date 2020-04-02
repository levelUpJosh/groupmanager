import groupsapp.models as appmodels
import string,random
from django.forms import ValidationError
from django.core.exceptions import ObjectDoesNotExist

def CheckUserMemberLink(user,member_id):
	### Check that a user object and member object (from the numerical id) are linked
	# Get all members for a user
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
def CheckMemberGroupLink(group_id,member_id):
	### Check if a member and group are linked (using both object's numerical id)
	try:
		check = appmodels.MemberGroupLink.objects.get(group_id=group_id,member_id=member_id)
		# If the line above fails, the except state will activate
		return True
	except ObjectDoesNotExist:
		return False

def GetAllUserMembers(search):
	### Get a QuerySet of all Member objects linked to a User and vice versa, depending on the input object's type.
	#Use the model attributes to detect model type
	if search.__class__.__name__ == 'User':
		#Make a filter query to find all link objects for this user
		memberlist= appmodels.UserMemberLink.objects.filter(user_id=search.pk)
		#Make a filter query for all Member objects with a primary key (pk/member_id) contained in the last query
		memberlist = appmodels.Member.objects.filter(pk__in=memberlist.all().values_list('member_id'))
		return memberlist
	elif search.__class__.__name__ == 'Member':
		#Filter for all link objects
		userlist = appmodels.UserMemberLink.objects.filter(member_id=search.pk)
		#FIlter for all User objects with a pk in the last query
		userlist = appmodels.User.objects.filter(pk__in=userlist.all().values_list('user_id'))
		return userlist
	else:
		return 'Unsupported object type. Please input a User or Member object.'

def GetAllMemberGroups(search,by_group=False):
	from  itertools import chain 
	#Despite the name, this function supports both members and users.
	#The object's type is detected and if it is a user then the function scans and returns ALL associated member groups.

	#Detect if the group type provided is a 'User' object
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
			#Make use of the fact that this function has code that handles individual member queries (see the next 'elif' statement)
			#Therefore just get the output for each member and make a list
			membertrack += [GetAllMemberGroups(member)]
		if by_group == True:
			#If by_group == True, we want to sort the current list so that Members are grouped by their Group, rather than the default which is the other way around 
			for item in membertrack:
				member = item[0]
				#iterate through the previous list made
				if not item[1]:
					#Add in a 'No Group' entry for items with empty grouplist QuerySet objects
					item[1] = ['No Group']
				for group in item[1]:
					#Iterate through each group in a member's list
					if group in chain(*grouptrack):
						#check if the group is already entered elsewhere
						for i in range(0,len(grouptrack)):
							#find where the Group is entered
							try:
								grouptrack[i].index(group)
								location = i
							except:
								pass
						#append the member to the correct location with the existing group or as a new entry
						grouptrack[location][1].append(member)				
					else:
						#add the group to the list if it's not been entered previously
						grouptrack += [[group,[member]]]
						#print(group)

			return grouptrack
			#print(membertrack)

	#Detect if the object provided is one member and so we only need to create a simple query
	elif search.__class__.__name__ == 'Member':
		
		grouplist = appmodels.MemberGroupLink.objects.filter(member_id=search.pk)
		grouplist = appmodels.Group.objects.filter(pk__in=grouplist.all().values_list('group_id'))
		#print(grouplist.first().group_id,flush=True)
		membertrack = [search,grouplist]
		#Function is handled better if all data is output in the same way even if only one member is being searched so it outputs a list here too
	else:
		return 'Unsupported object type. Please input a User or Member object'
	return membertrack

def GetAllMembersInGroup(search):
	#This function gets all members that are linked to a specific Group
	#It's implemented on the GroupAdmin dashboard
	if search.__class__.__name__ == 'Group':
		memberlist = appmodels.MemberGroupLink.objects.filter(group_id=search.pk)
		memberlist = appmodels.Member.objects.filter(pk__in=memberlist.all().values_list('member_id'))
		return memberlist
	else:
		return 'Unsupported object type. Please input a Group object'


def GetAllUserGroups(search):
	#Similar to GetAllMembersInGroup but instead returns either all Groups a User is linked to or vice versa.
	returnlist = []
	#If search is a User object then find all Groups that User has a role in (admin/leader)
	if search.__class__.__name__ == 'User':
		grouplist= appmodels.UserGroupLink.objects.filter(user_id=search.pk)
		for link in grouplist:
			role = link.role
			group = appmodels.Group.objects.get(pk=link.group_id)
			returnlist += [[group,role]]
		return returnlist
	#If search is a Group object then find all Users that have a role in that Group
	elif search.__class__.__name__ == 'Group':
		userlist = appmodels.UserGroupLink.objects.filter(group_id=search.pk)
		for link in userlist:
			role = link.role
			user = appmodels.User.objects.get(pk=link.user_id)
			returnlist += [[user,role]]
		return returnlist
	else:
		return 'Unsupported object type. Please input a User or Group object.'



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
		if inputObjectType == 'User':
			appmodels.UserGroupLink.objects.get(group=group,user=member)
		return False
	except:
	 	return True 
def GenerateJoinCode(group,role='member',maxno=1):
	### Generate a new join code made up of 8 characters for a given group, role and maximum uses number
	letters = string.ascii_uppercase
	#An odd issue of using random sequences of the full alphabet is that there is a small chance that the code could spell out words, some of which groups may not wish to distribute to parents.
	#This might not be too favourable so we'll remove the vowels from the letter selection,
	letters = letters.translate({ord('A'): None, ord('E'): None, ord('I'): None, ord('O'): None, ord('U'): None})
	generated = False
	while generated == False:
		#Repeat this stage until a unique, valid code has been generated
		code = ''
		for i in range(7):
			# Generate a string of 7 random letters
			code += random.choice(letters)
		if role == 'member':
			# Concentate 'M' or 'L' with the string of 7 characters generated previously
			code = 'M'+code
		else:
			code = 'L'+code
		# Make a query to see if this code is already in use
		if not appmodels.JoinCode.objects.filter(code=code):
			#If not, then save the new object
			new = appmodels.JoinCode(code=code,group=group,role=role,maxno=maxno)
			new.save()
			# Set generated to true to end the while loop
			generated = True
			#Return JoinCode object
			return new

def UseJoinCode(code,member):
	#Method to use JoinCode provided by the user facing form.
	#member in this case can actually represent a member or user object, which object is used depends on the role entry in the JoinCode object
	JoinObject = CheckJoinCodeExists(code)

	#inputObjectType helps to deal with the hopefully unlikely problem that a code may include the correct attributes for 'member' but member may be provided as a 'User' object (intended for Leader role codes only) and vice versa.
	#The javascript in the joingroup.html file prevents this being necessary.
	inputObjectType = member.__class__.__name__

	#If JoinObject is anything except False (meaning no object was found) then continue
	if JoinObject != False:
		#Check that there is not an existing link between the object and group
		is_not_used = CheckJoinCodeNotUsed(member,JoinObject.group)
		#Store the group as a seperate variable
		group = appmodels.Group.objects.get(pk=JoinObject.group_id)
		
		#If there is not an existing link object then continue
		if is_not_used == True:
			#Detect if the JoinObject refers to a member or leader/admin code
			if  JoinObject.role == 'member':
				#Detect if the program should treat the input object (member) as a member or user object
				#As a result this also checks that it matches the code
				if inputObjectType == 'Member':
					#Create and save a new link object
					mglink = appmodels.MemberGroupLink(member=member,group=group,role=JoinObject.role).save()
					#Reduce the maxno of the JoinObject by 1
					JoinObject.maxno -= 1
					#Save the JoinObject with the new maxno
					JoinObject.save()
					#If the JoinObject has no more uses left after this use then delete it
					if JoinObject.maxno == 0:
						JoinObject.delete()
					return True
				else:
					return 'This code can only be associated with a member object.'
			#See comments in last if block
			elif JoinObject.role in ['leader','admin']:
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
def GetAllJoinCodes(group):
	### Returns all JoinCodes associated with a group
	if group.__class__.__name__ == 'Group':
		joincodes = appmodels.JoinCode.objects.filter(group=group)
		return joincodes
def ValidateName(name,digits=False):
	### Validates a string to check it only has letters (and digits if required)
	letters = string.ascii_letters+" "
	if digits == True:
		letters += string.digits
	if any((c not in letters) for c in name):
		return False
	else:
		return True

def UserIsAdmin(user):
	#Returns True if the given user has the 'admin' role in ANY group and False if it is not linked or only a 'leader'.
	admin = False
	usergroups = GetAllUserGroups(user)
	for link in usergroups:
		if link[1] == "admin":
			admin = True
	return admin