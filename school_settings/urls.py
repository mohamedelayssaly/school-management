from django.urls import path

from . import views

urlpatterns = [
    path('settings/', views.SettingsHome.as_view(), name='settings_home'),
    path('settings/school/', views.SchoolProfileView.as_view(), name='school_profile'),
    path('settings/users/', views.UserList.as_view(), name='user_list'),
    path('settings/users/<int:pk>/edit/', views.UserEdit.as_view(), name='user_edit'),
    path('settings/users/<int:pk>/password/', views.UserPasswordReset.as_view(), name='user_password'),
    path('account/', views.my_account, name='my_account'),
    path('account/password/', views.MyPasswordChange.as_view(), name='my_password'),
]