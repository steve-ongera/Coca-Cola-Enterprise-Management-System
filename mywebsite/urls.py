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
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/', views.attendance_detail, name='attendance_detail'),
    path('attendance/<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),


    path('leave_list', views.leave_list, name='leave_list'),
    path('create_leave/', views.leave_create, name='leave_create'),
    path('leave/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leave/<int:pk>/update/', views.leave_update, name='leave_update'),
    path('leave/<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('leave/<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('leave/<int:pk>/reject/', views.leave_reject, name='leave_reject'),

    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/<int:pk>/', views.payroll_detail, name='payroll_detail'),
    path('payroll/<int:pk>/edit/', views.payroll_update, name='payroll_update'),
    path('payroll/<int:pk>/delete/', views.payroll_delete, name='payroll_delete'),
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/<int:pk>/process/', views.payroll_process, name='payroll_process'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # Products
    path('store', views.product_list, name='product_list'),
    path('store/<int:pk>/', views.product_detail, name='product_detail'),
    path('store/create/', views.product_create, name='product_create'),
    
    # Variants
    path('store/<int:product_pk>/variants/create/', views.variant_create, name='variant_create'),

     # AJAX Endpoints
    path('search/', views.product_search, name='product_search'),
    path('<int:pk>/quickview/', views.quick_view, name='quick_view'),
    path('<int:pk>/toggle-status/', views.toggle_product_status, name='toggle_status'),
    path('import/', views.import_products, name='import_products'),
    
]