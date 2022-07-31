from django.urls import path

from app import views
from pages.views import change_account_settings, profile_view

urlpatterns = [
    path('', views.user_view, name='user_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('academic-filter/', views.academic_filter, name='academic-filter'),
    path('academic-record/', views.create_academic_record, name='academic-record'),
    path('register', views.register_view, name='register'),
    path('account-settings', change_account_settings, name='account_settings'),
    path('profile', profile_view, name='profile_view'),
    path('<str:user>', views.viewuser_general_view, name='viewuser_general_view'),
]
