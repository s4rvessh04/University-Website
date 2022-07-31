from django.urls import path

from . import views


app_name = 'api'

urlpatterns = [
    #USER URLS
    path('user/<int:pk>', views.api_user_details_view, name='user-details'),
    path('all-users', views.Api_allusers_view.as_view(), name='all-users'),

    #TOKEN URL
    path('token/<int:pk>', views.api_user_token_view, name='token'),

    #ACCESSIBLE LINKS URLS
    path('links-list', views.api_links_admin_view, name='links-list'),  
    path('links', views.api_links_view, name='links'),
    
    #STUDENT URLS
    path('student-list', views.Api_students_view.as_view(), name='student-list'),
    path('student/<int:pk>', views.api_student_details_view, name='student-details'),

    #ACADEMICS URLS
    path('complete-academics-list', views.Api_admin_academic_view.as_view(), name='complete-academics-list'),
    path('academics-details', views.Api_academic_view.as_view(), name='academics-details'),
    path('academics-list', views.Api_academic_list_view.as_view(), name='academics-list'),
    
    #INTERNSHIP APPLICANT URL
    path('api:internship-applicant-list', views.Api_internship_applicant_view.as_view(), name='internship-applicant-list'),

    #MICS
    path('test/', views.api_academic_view, name='student-list'),

]
