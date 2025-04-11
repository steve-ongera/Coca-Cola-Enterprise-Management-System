from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('manager-dashboard/', views.manager_dashboard_view, name='manager_dashboard'),
    path('employee-dashboard/', views.employee_dashboard_view, name='employee_dashboard'),

    #Employee Records URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    path('attendance_list/', views.attendance_list, name='attendance_list'),
    path('create/', views.attendance_create, name='attendance_create'),
    path('<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    
]