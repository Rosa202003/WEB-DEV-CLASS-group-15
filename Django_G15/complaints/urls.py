from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Complaint CRUD
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/create/', views.complaint_create, name='complaint_create'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:pk>/update/', views.complaint_update, name='complaint_update'),
    path('complaints/<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/complaints/', views.staff_complaint_list, name='staff_complaint_list'),
    path('staff/complaints/<int:pk>/', views.staff_complaint_detail, name='staff_complaint_detail'),
]