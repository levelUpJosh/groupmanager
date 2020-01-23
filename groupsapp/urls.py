from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('addmember/', views.add_member, name="addmember"),
    path('addgroup/', views.add_group, name="addgroup"),
    path('joingroup/', views.join_group, name="joingroup")

]