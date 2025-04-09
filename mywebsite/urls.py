from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('manager-dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    path('employee-dashboard/', views.employee_dashboard_view, name='employee_dashboard'),
]