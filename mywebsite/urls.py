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
    path('products/<int:pk>/quickview/', views.quick_view, name='product_quick_view'),
    path('<int:pk>/toggle-status/', views.toggle_product_status, name='toggle_status'),
    path('import/', views.import_products, name='import_products'),


    # Warehouses
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('warehouses/<int:pk>/edit/', views.warehouse_update, name='warehouse_update'),
    
    # Stock Movements
    path('stock-movements/', views.stock_movement_list, name='stock_movement_list'),
    path('stock-movements/create/', views.stock_movement_create, name='stock_movement_create'),
    
    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    
    # Alerts
    path('low-stock-alerts/', views.low_stock_alerts, name='low_stock_alerts'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Delivery Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    # Vehicle status update
    path('vehicles/<int:pk>/update-status/', views.vehicle_update_status, name='vehicle_update_status'),
    path('vehicles/<int:pk>/upload-image/', views.vehicle_upload_image, name='vehicle_upload_image'),
    path('vehicles/<int:pk>/add-maintenance/',  views.vehicle_add_maintenance,    name='vehicle_add_maintenance'),

    # Facilities
    path('facilities/', views.facility_list, name='facility_list'),
    path('facilities/create/', views.facility_create, name='facility_create'),
    path('facilities/<int:pk>/', views.facility_detail, name='facility_detail'),
    path('facilities/<int:pk>/update/', views.facility_update, name='facility_update'),
    path('facilities/<int:pk>/changelog/',views.facility_changelog,name='facility_changelog'),
    
    # Production Lines
    
    path('facilities/<int:facility_id>/lines/create/',views.create_production_line,name='line_create'),
    path('lines/', views.production_line_list, name='line_list'),
    path('lines/create/', views.production_line_create, name='line_create'),
    path('lines/<int:pk>/', views.production_line_detail, name='line_detail'),
    
    # Batches
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batches/<int:pk>/update/', views.batch_update, name='batch_update'),
    
    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
    # Dashboard and List Views
    path('maintenance/', views.maintenance_list, name="maintenance_list"),
    path('maintenance/dashboard/', views.maintenance_dashboard, name="maintenance_dashboard"),
    path('maintenance/calendar/', views.maintenance_calendar, name="maintenance_calendar"),
    path('maintenance/analytics/', views.maintenance_analytics, name="maintenance_analytics"),

    # CRUD Operations
    path('maintenance/create/', views.maintenance_create, name="maintenance_create"),
    # path('maintenance/<int:pk>/', views.maintenance_detail, name="maintenance_detail"),
    # path('maintenance/<int:pk>/update/', views.maintenance_update, name="maintenance_update"),
    # path('maintenance/<int:pk>/delete/', views.maintenance_delete, name="maintenance_delete"),

    # # Workflow Actions
    # path('maintenance/<int:pk>/start/', views.maintenance_start, name="maintenance_start"),
    # path('maintenance/<int:pk>/complete/', views.maintenance_complete, name="maintenance_complete"),
    # path('maintenance/<int:pk>/cancel/', views.maintenance_cancel, name="maintenance_cancel"),

    # # Line-Specific Maintenance
    # path('lines/<int:line_id>/maintenance/', views.line_maintenance_list, name="line_maintenance_list"),
    # path('lines/<int:line_id>/maintenance/create/', views.line_maintenance_create, name="line_maintenance_create"),

    # # Technician Views
    # path('technicians/<int:tech_id>/assignments/', views.technician_assignments, name="technician_assignments"),
    
    # Downtime
    path('downtime/', views.downtime_list, name='downtime_list'),
    path('downtime/create/', views.downtime_create, name='downtime_create'),


    
]