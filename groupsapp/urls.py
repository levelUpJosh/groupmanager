from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('register/', views.register, name='register'),
    path('addmember/', views.add_member, name="addmember"),
    path('addgroup/', views.add_group, name="addgroup"),
    path('joingroup/', views.join_group, name="joingroup"),
    path('member/<int:member_id>/', views.memberprofile, name="member"),
    path('group/<int:id>/', views.groupprofile, name="group"),

]