from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name="login"),
    path('logout/', views.logoutpage, name="logout"),
    path('register/', views.register, name='register'),
    path('addmember/', views.add_member, name="addmember"),
    path('addgroup/', views.add_group, name="addgroup"),
    path('joingroup/', views.join_group, name="joingroup"),
    path('user/', views.userprofile, name="user"),
    path('member/<int:member_id>/', views.memberprofile, name="member"),
    path('<str:objectType>/<int:object_id>/delete/', views.delete_view, name='deleteobject'),
    path('group/<int:group_id>/', views.groupprofile, name="group"),
    path('group/<int:group_id>/admin/', views.groupadmin, name="groupadmin"),
    path('group/<int:group_id>/admin/<str:task>/<int:object_id>/', views.groupadmintask, name="removegroupmember"),
    path('group/<int:group_id>/admin/<str:task>/<str:code>/', views.groupadmintask, name="deletecode"),
    path('group/<int:group_id>/admin/<str:task>/', views.groupadmintask, name="formtask"),
    path('group/<int:group_id>/admin/member/<int:member_id>', views.memberprofile, name="editgroupmember"),
    

]