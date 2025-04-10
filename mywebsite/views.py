from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.db import IntegrityError

def login_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect_to_dashboard(user)
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'auth/login.html')

def redirect_to_dashboard(user):
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')

def register_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type', 'employee')
        
        # Validate password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        
        # Check if employee exists and matches provided details
        try:
            employee = Employee.objects.get(
                working_id=employee_id,
                first_name__iexact=first_name,
                last_number__iexact=last_name
            )
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found or details do not match our records.')
            return render(request, 'auth/register.html')
        
        # Check if user already exists
        if User.objects.filter(employee_id=employee_id).exists():
            messages.error(request, 'An account with this employee ID already exists.')
            return render(request, 'auth/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=employee_id,
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                password=password,
                user_type=user_type
            )
            
            # Link the employee profile to the user
            employee.user = user
            employee.save()
            
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'An error occurred while creating your account.')
    
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def manager_dashboard_view(request):
    # Manager-specific data (for their department)
    try:
        department = request.user.employee_profile.department
        department_employees = Employee.objects.filter(department=department)
        
        context = {
            'user': request.user,
            'department': department,
            'team_members': department_employees,
            'dashboard_title': 'Manager Dashboard',
        }
        return render(request, 'dashboard/manager_dashboard.html', context)
    except AttributeError:
        # Handle case where manager doesn't have an associated department
        return render(request, 'dashboard/manager_dashboard.html', {
            'user': request.user,
            'dashboard_title': 'Manager Dashboard',
            'error': 'You are not assigned to any department'
        })

@login_required
def employee_dashboard_view(request):
    # Employee-specific data
    try:
        employee_profile = request.user.employee_profile
        
        context = {
            'user': request.user,
            'employee': employee_profile,
            'dashboard_title': 'My Dashboard',
        }
        return render(request, 'dashboard/employee_dashboard.html', context)
    except AttributeError:
        # Handle case where employee profile doesn't exist
        return render(request, 'dashboard/employee_dashboard.html', {
            'user': request.user,
            'dashboard_title': 'My Dashboard',
            'error': 'Employee profile not found'
        })
    



from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import plotly.express as px
import pandas as pd

def admin_dashboard_view(request):
    # Employee Metrics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='active').count()
    on_leave = Employee.objects.filter(employment_status='on_leave').count()
    
    # Department distribution
    dept_distribution = Department.objects.annotate(
        employee_count=Count('employees'))
    
    # Attendance metrics (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_data = Attendance.objects.filter(
        date__gte=thirty_days_ago
    ).values('status').annotate(count=Count('id'))
    
    # Payroll summary
    payroll_summary = Payroll.objects.filter(
        period_end__month=timezone.now().month
    ).aggregate(
        total_payroll=Sum('net_salary'),
        avg_salary=Avg('net_salary')
    )
    
    # Inventory metrics
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).count()
    total_products = Product.objects.count()
    total_variants = ProductVariant.objects.count()
    
    # Sales metrics (last 30 days)
    sales_data = SalesOrder.objects.filter(
        order_date__gte=thirty_days_ago
    ).aggregate(
        total_sales=Sum('total_amount'),
        order_count=Count('id')
    )
    
    # Recent activities
    recent_orders = SalesOrder.objects.order_by('-order_date')[:5]
    recent_purchases = PurchaseOrder.objects.order_by('-order_date')[:5]
    recent_deliveries = Delivery.objects.order_by('-scheduled_date')[:5]
    
    # Create charts
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave': on_leave,
        'dept_distribution': dept_distribution,
        'attendance_data': attendance_data,
        'payroll_summary': payroll_summary,
        'low_stock_items': low_stock_items,
        'total_products': total_products,
        'total_variants': total_variants,
        'sales_data': sales_data,
        'recent_orders': recent_orders,
        'recent_purchases': recent_purchases,
        'recent_deliveries': recent_deliveries,
    }
    
    # Generate department distribution chart
    dept_df = pd.DataFrame(list(dept_distribution.values('name', 'employee_count')))
    if not dept_df.empty:
        dept_fig = px.pie(dept_df, values='employee_count', names='name', 
                          title='Employee Distribution by Department')
        context['dept_chart'] = dept_fig.to_html()
    
    # Generate attendance chart
    if attendance_data:
        att_df = pd.DataFrame(list(attendance_data))
        if not att_df.empty:
            att_fig = px.bar(att_df, x='status', y='count', 
                            title='Attendance Status (Last 30 Days)')
            context['attendance_chart'] = att_fig.to_html()
    
    # Generate sales trend chart (last 7 days)
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    sales_trend = SalesOrder.objects.filter(
        order_date__gte=seven_days_ago
    ).values('order_date').annotate(
        daily_sales=Sum('total_amount'),
        order_count=Count('id')
    ).order_by('order_date')
    
    if sales_trend:
        trend_df = pd.DataFrame(list(sales_trend))
        if not trend_df.empty:
            trend_fig = px.line(trend_df, x='order_date', y='daily_sales',
                               title='Daily Sales Trend (Last 7 Days)')
            context['sales_trend_chart'] = trend_fig.to_html()
    
    return render(request, 'dashboard/admin_dashboard.html', context)