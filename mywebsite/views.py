from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.db import IntegrityError
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def login_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect_to_dashboard(user)
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'auth/login.html')

def redirect_to_dashboard(user):
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'manager':
        return redirect('manager_dashboard')
    
    elif user.user_type == 'security':
        return redirect('security_guard_dashboard')
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
                last_name__iexact=last_name
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
                email=employee.email, 
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
    messages.success(request, "You have successfully logged out.")
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
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    Employee, Department, Attendance, 
    SalesOrder, PurchaseOrder, Payroll
)
import json

from django.core.exceptions import PermissionDenied

def admin_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        raise PermissionDenied  # This triggers 403.html if set up

    # ... (rest of your dashboard logic remains the same)

    # Employee Metrics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(employment_status='active').count()
    on_leave = Employee.objects.filter(employment_status='on_leave').count()
    
    # Department distribution data for Chart.js
    departments = Department.objects.annotate(employee_count=Count('employees'))
    dept_labels = [dept.name for dept in departments]
    dept_data = [dept.employee_count for dept in departments]
    
    # Attendance data (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_statuses = Attendance.objects.filter(
        date__gte=thirty_days_ago
    ).values('status').annotate(count=Count('id'))
    
    attendance_labels = [status['status'].title() for status in attendance_statuses]
    attendance_data = [status['count'] for status in attendance_statuses]
    
    # Sales trend data (last 7 days)
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    sales_trend = SalesOrder.objects.filter(
        order_date__gte=seven_days_ago
    ).values('order_date').annotate(
        daily_sales=Sum('total_amount')
    ).order_by('order_date')
    
    sales_dates = [order['order_date'].strftime("%Y-%m-%d") for order in sales_trend]
    sales_amounts = [float(order['daily_sales']) for order in sales_trend]
    
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
    
    # Recent activities
    recent_orders = SalesOrder.objects.order_by('-order_date')[:5]
    recent_purchases = PurchaseOrder.objects.order_by('-order_date')[:5]
    recent_deliveries = Delivery.objects.order_by('-scheduled_date')[:5]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'on_leave': on_leave,
        'dept_labels': json.dumps(dept_labels),
        'dept_data': json.dumps(dept_data),
        'attendance_labels': json.dumps(attendance_labels),
        'attendance_data': json.dumps(attendance_data),
        'sales_dates': json.dumps(sales_dates),
        'sales_amounts': json.dumps(sales_amounts),
        'payroll_summary': payroll_summary,
        'low_stock_items': low_stock_items,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'recent_purchases': recent_purchases,
        'recent_deliveries': recent_deliveries,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Employee, Attendance, Task, Announcement, Leave
from django.db.models import Count
from .forms import *

@login_required
def employee_dashboard(request):
    # Get the employee profile
    employee = request.user.employee_profile
    
    # Attendance summary for the current month
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__range=[first_day, last_day]
    )
    
    attendance_summary = {
        'present_days': attendance_records.filter(status='present').count(),
        'absent_days': attendance_records.filter(status='absent').count(),
        'late_days': attendance_records.filter(status='late').count(),
        'leave_days': attendance_records.filter(status='on_leave').count(),
        'working_days': (last_day - first_day).days + 1
    }
    
    # Leave balance
    leave_balance = {
        'total_days': 21,  # Typically 21 days annual leave
        'used_days': Leave.objects.filter(
            employee=employee,
            status='approved',
            start_date__year=today.year
        ).count(),
        'remaining_days': 21 - Leave.objects.filter(
            employee=employee,
            status='approved',
            start_date__year=today.year
        ).count()
    }
    
    # Tasks (today and overdue)
    tasks = Task.objects.filter(
        assigned_to=employee,
        due_date__lte=today + timedelta(days=7)  # Show tasks due in next 7 days
    ).order_by('due_date', 'priority')
    
    # Weekly schedule (simplified example)
    schedule = [
        {'day': 'Monday', 'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00', 'location': 'Production Line A'},
        {'day': 'Tuesday', 'shift_name': 'Morning', 'start_time': '08:00', 'end_time': '16:00', 'location': 'Production Line A'},
        {'day': 'Wednesday', 'shift_name': 'Afternoon', 'start_time': '12:00', 'end_time': '20:00', 'location': 'Packaging'},
        # Add more days as needed
    ]
    
    # Recent announcements
    announcements = Announcement.objects.filter(
        target_departments=employee.department
    ).order_by('-created_at')[:3]
    
    context = {
        'employee': employee,
        'attendance_summary': attendance_summary,
        'leave_balance': leave_balance,
        'tasks': tasks,
        'schedule': schedule,
        'announcements': announcements,
    }
    
    return render(request, 'employee_dashboard.html', context)

@login_required
def clock_in_out(request):
    employee = request.user.employee_profile
    today = timezone.now().date()
    
    # Check if already clocked in today
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today,
        defaults={'status': 'present'}
    )
    
    if not created:
        if not attendance.check_out_time:
            # Clock out
            attendance.check_out_time = timezone.now().time()
            attendance.save()
            messages.success(request, "Successfully clocked out")
        else:
            # Already clocked out
            messages.warning(request, "You've already clocked out today")
    else:
        # Clocked in
        messages.success(request, "Successfully clocked in")
    
    return redirect('employee_dashboard')

@login_required
def request_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user.employee_profile
            leave.save()
            messages.success(request, "Leave request submitted successfully")
            return redirect('employee_dashboard')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'request_leave.html', {'form': form})

@login_required
def submit_timesheet(request):
    if request.method == 'POST':
        form = TimesheetForm(request.POST)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.employee = request.user.employee_profile
            timesheet.save()
            messages.success(request, "Timesheet submitted successfully")
            return redirect('employee_dashboard')
    else:
        form = TimesheetForm()
    
    return render(request, 'submit_timesheet.html', {'form': form})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Employee, Attendance, ProductionTarget, QualityCheck, Announcement, TrainingSession, SafetyAlert

@login_required
def staff_dashboard(request):
    employee = request.user.employee_profile
    
    # Today's shift information
    today = timezone.now().date()
    today_shift = {
        'shift_name': 'Morning Shift',
        'start_time': timezone.now().replace(hour=8, minute=0, second=0),
        'end_time': timezone.now().replace(hour=16, minute=0, second=0),
        'location': 'Production Line 3'
    }
    
    # Attendance status
    attendance_status = {
        'clocked_in': Attendance.objects.filter(
            employee=employee,
            date=today,
            check_in_time__isnull=False
        ).exists(),
        'time': Attendance.objects.filter(
            employee=employee,
            date=today
        ).first().check_in_time if Attendance.objects.filter(
            employee=employee,
            date=today
        ).exists() else None
    }
    
    # Production targets
    production_targets = [
        {
            'product': {'name': 'Coca-Cola 330ml'},
            'target_quantity': 5000,
            'completed_quantity': 3750,
            'percent_complete': 75
        },
        {
            'product': {'name': 'Sprite 500ml'},
            'target_quantity': 3000,
            'completed_quantity': 2700,
            'percent_complete': 90
        },
        {
            'product': {'name': 'Fanta Orange 1L'},
            'target_quantity': 2000,
            'completed_quantity': 2200,
            'percent_complete': 110
        }
    ]
    
    # Quality checks
    quality_checks = [
        {
            'check_name': 'Bottle Seal Integrity',
            'description': 'Check seal quality on random samples',
            'status': 'passed',
            'last_checked': timezone.now() - timedelta(hours=2)
        },
        {
            'check_name': 'Sugar Content',
            'description': 'Verify sugar levels in production batch',
            'status': 'pending',
            'last_checked': timezone.now() - timedelta(hours=4)
        },
        {
            'check_name': 'Label Alignment',
            'description': 'Inspect label placement accuracy',
            'status': 'failed',
            'last_checked': timezone.now() - timedelta(hours=1)
        }
    ]
    
    # Announcements
    announcements = Announcement.objects.filter(
        target_departments=employee.department
    ).order_by('-created_at')[:5]
    
    new_announcements = announcements.filter(
        created_at__gte=timezone.now() - timedelta(days=1))
    
    # Training sessions
    upcoming_training = TrainingSession.objects.filter(
        target_groups__in=[employee.position],
        date__gte=today
    ).order_by('date')[:3]
    
    # Safety information
    safety_status = {
        'level': 'Normal',
        'message': 'All safety protocols are being followed'
    }
    
    safety_alerts = SafetyAlert.objects.filter(
        is_active=True
    ).order_by('-created_at')[:3]
    
    context = {
        'today_shift': today_shift,
        'attendance_status': attendance_status,
        'production_targets': production_targets,
        'quality_checks': quality_checks,
        'announcements': announcements,
        'new_announcements': new_announcements,
        'upcoming_training': upcoming_training,
        'safety_status': safety_status,
        'safety_alerts': safety_alerts,
    }
    
    return render(request, 'dashboard/staff_dashboard.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import Employee, Department
from .forms import EmployeeForm
@login_required
@permission_required('employees.view_employee', raise_exception=True)


def employee_list(request):
    # Get filter and search parameters from request
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    search_query = request.GET.get('search', '')
    
    employees = Employee.objects.select_related('department', 'user').all()
    
    # Apply filters if provided
    if department_id:
        employees = employees.filter(department_id=department_id)
    if status:
        employees = employees.filter(employment_status=status)
    
    # Apply search if provided
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(working_id__icontains=search_query) |
            Q(position__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(employees, 10)  # Show 10 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.all()
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
        'current_department': int(department_id) if department_id else None,
        'current_status': status if status else None,
        'search_query': search_query,
    }
    return render(request, 'employees/employee_list.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff  # or use user.is_superuser

@user_passes_test(is_admin)
@permission_required('employees.add_employee', raise_exception=True)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.user.get_full_name()} created successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    context = {'form': form, 'title': 'Add New Employee'}
    return render(request, 'employees/employee_form.html', context)

from django.shortcuts import render, get_object_or_404
from datetime import date
from .models import Employee, PositionHistory, Attendance, Leave, Payroll, PerformanceReview


def is_admin(user):
    return user.is_authenticated and user.is_staff  # or use user.is_superuser

@user_passes_test(is_admin)
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    #stats
    # Calculate date range for past 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    
    # Get attendance data for past 6 months
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__gte=six_months_ago
    ).order_by('-date')
    
    # Calculate attendance percentage
    total_work_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    attendance_percentage = 0
    if total_work_days > 0:
        attendance_percentage = round((present_days / total_work_days) * 100)
    
    # Get leave data for past 6 months
    leave_stats = Leave.objects.filter(
        employee=employee,
        start_date__gte=six_months_ago
    ).aggregate(
        total_leaves=Count('id'),
        approved_leaves=Count('id', filter=Q(status='approved'))
    )
    
    # Get related data with pagination (5 items per page)
    position_history = PositionHistory.objects.filter(employee=employee).order_by('-start_date')[:20]
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:20]
    leave_requests = Leave.objects.filter(employee=employee).order_by('-start_date')[:20]
    payroll_records = Payroll.objects.filter(employee=employee).order_by('-period_start')[:20]
    performance_reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_period')[:20]
    
    # Create paginators
    position_paginator = Paginator(position_history, 5)
    attendance_paginator = Paginator(attendance_records, 5)
    leave_paginator = Paginator(leave_requests, 5)
    payroll_paginator = Paginator(payroll_records, 5)
    performance_paginator = Paginator(performance_reviews, 5)
    
    # Get page numbers from request
    position_page = request.GET.get('position_page', 1)
    attendance_page = request.GET.get('attendance_page', 1)
    leave_page = request.GET.get('leave_page', 1)
    payroll_page = request.GET.get('payroll_page', 1)
    performance_page = request.GET.get('performance_page', 1)
    
    # Get page objects
    position_history_page = position_paginator.get_page(position_page)
    attendance_records_page = attendance_paginator.get_page(attendance_page)
    leave_requests_page = leave_paginator.get_page(leave_page)
    payroll_records_page = payroll_paginator.get_page(payroll_page)
    performance_reviews_page = performance_paginator.get_page(performance_page)
    
    # Calculate tenure
    tenure_years = None
    tenure_months = None
    if employee.hire_date:
        today = date.today()
        tenure = today - employee.hire_date
        tenure_years = tenure.days // 365
        tenure_months = (tenure.days % 365) // 30
    
    context = {
        'employee': employee,
        'position_history': position_history_page,
        'attendance_records': attendance_records_page,
        'leave_requests': leave_requests_page,
        'payroll_records': payroll_records_page,
        'performance_reviews': performance_reviews_page,
        'tenure_years': tenure_years,
        'tenure_months': tenure_months,
        'attendance_percentage': attendance_percentage,
        'leave_stats': leave_stats,
    }
    
    return render(request, 'employees/employee_detail.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff  # or use user.is_superuser

@user_passes_test(is_admin)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            updated_employee = form.save()
            messages.success(request, f'Employee  updated successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)


    full_name = employee.user.get_full_name() if employee.user else "Unnamed"
    
    context = {
        'form': form,
        'title': f'Edit {full_name}',
        'employee': employee,
    }
    return render(request, 'employees/employee_form.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff  # or use user.is_superuser

@user_passes_test(is_admin)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        full_name = employee.user.get_full_name()
        employee.delete()
        messages.success(request, f'Employee {full_name} deleted successfully!')
        return redirect('employee_list')
    
    context = {'employee': employee}
    return render(request, 'employees/employee_confirm_delete.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from .models import Attendance, Employee
from .forms import AttendanceForm
from datetime import date, timedelta
import json

# Create
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, f'Attendance record for {attendance.employee} on {attendance.date} created successfully!')
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm()
    
    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Create Attendance Record'
    })

# Read (Detail View with Graph)
def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    # Prepare data for monthly attendance chart (last 6 months)
    today = date.today()
    six_months_ago = today - timedelta(days=180)
    
    # Initialize default chart data
    chart_data = {
        'months': json.dumps([]),
        'present': json.dumps([]),
        'absent': json.dumps([]),
        'half_day': json.dumps([]),
    }

    try:
        # Get attendance data for the past six months
        attendance_records = Attendance.objects.filter(
            employee=attendance.employee,
            date__gte=six_months_ago,
            date__lte=today
        )
        
        # Create a dictionary to store monthly counts by status
        data_dict = {}
        
        # Process each attendance record manually instead of using complex aggregations
        for record in attendance_records:
            month = record.date.month
            status = record.status
            
            if month not in data_dict:
                data_dict[month] = {'present': 0, 'absent': 0, 'half_day': 0}
            
            # Only count recognized status values
            if status in ('present', 'absent', 'half_day'):
                data_dict[month][status] += 1
        
        # Generate labels and data for last 6 months
        months = []
        present_data = []
        absent_data = []
        half_day_data = []

        # Get the current month number
        current_month = today.month
        current_year = today.year
        
        # Loop through the past 6 months
        for i in range(5, -1, -1):
            # Calculate month and year
            month_idx = current_month - i
            year = current_year
            
            if month_idx <= 0:
                month_idx += 12
                year -= 1
                
            # Get the month name
            month_name = date(year, month_idx, 1).strftime('%b')
            months.append(month_name)
            
            # Get data for this month or use zeros if no data exists
            month_data = data_dict.get(month_idx, {'present': 0, 'absent': 0, 'half_day': 0})
            
            present_data.append(month_data['present'])
            absent_data.append(month_data['absent'])
            half_day_data.append(month_data['half_day'])

        chart_data = {
            'months': json.dumps(months),
            'present': json.dumps(present_data),
            'absent': json.dumps(absent_data),
            'half_day': json.dumps(half_day_data),
        }

    except Exception as e:
        import traceback
        print(f"Error generating chart data: {str(e)}")
        print(traceback.format_exc())  # Print full traceback

    return render(request, 'attendance/attendance_detail.html', {
        'attendance': attendance,
        'chart_data': chart_data
    })

# Update
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, f'Attendance record for {attendance.employee} on {attendance.date} updated successfully!')
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Update Attendance Record',
        'attendance': attendance
    })

# Delete
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        employee_name = attendance.employee.user.get_full_name()
        date_str = attendance.date.strftime('%Y-%m-%d')
        attendance.delete()
        messages.success(request, f'Attendance record for {employee_name} on {date_str} deleted successfully!')
        return redirect('attendance_list')
    
    return render(request, 'attendance/attendance_confirm_delete.html', {
        'attendance': attendance
    })

# Attendance List View
from django.core.paginator import Paginator

def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date', 'employee__user__last_name')
    
    # Filtering
    employee_id = request.GET.get('employee')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    
    if employee_id:
        attendances = attendances.filter(employee__id=employee_id)
    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if status:
        attendances = attendances.filter(status=status)
    
    # Pagination
    paginator = Paginator(attendances, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    employees = Employee.objects.all()
    
    return render(request, 'attendance/attendance_list.html', {
        'page_obj': page_obj,
        'employees': employees,
        'status_choices': Attendance.STATUS_CHOICES
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Leave, Employee
from .forms import LeaveForm
from datetime import date

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('leave_detail', pk=leave.pk)
    else:
        form = LeaveForm()
    
    return render(request, 'leave/leave_form.html', {
        'form': form,
        'title': 'Create Leave Request'
    })

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    # Calculate leave duration
    duration = (leave.end_date - leave.start_date).days + 1
    
    return render(request, 'leave/leave_detail.html', {
        'leave': leave,
        'duration': duration
    })

@login_required
def leave_update(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request updated successfully!')
            return redirect('leave_detail', pk=leave.pk)
    else:
        form = LeaveForm(instance=leave)
    
    return render(request, 'leave/leave_form.html', {
        'form': form,
        'title': 'Update Leave Request',
        'leave': leave
    })

@login_required
def leave_delete(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave request deleted successfully!')
        return redirect('leave_list')
    
    return render(request, 'leave/leave_confirm_delete.html', {
        'leave': leave
    })

# views.py
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

@login_required
def leave_list(request):
    leaves = Leave.objects.all().order_by('-start_date')
    
    # Filtering
    employee_id = request.GET.get('employee')
    status = request.GET.get('status')
    leave_type = request.GET.get('leave_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if employee_id:
        leaves = leaves.filter(employee__id=employee_id)
    if status:
        leaves = leaves.filter(status=status)
    if leave_type:
        leaves = leaves.filter(leave_type=leave_type)
    if date_from:
        leaves = leaves.filter(start_date__gte=date_from)
    if date_to:
        leaves = leaves.filter(end_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(leaves, 10)  # Show 10 leaves per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    employees = Employee.objects.all()
    
    return render(request, 'leave/leave_list.html', {
        'page_obj': page_obj,
        'employees': employees,
        'status_choices': Leave.STATUS_CHOICES,
        'leave_type_choices': Leave.LEAVE_TYPE_CHOICES,
        'current_filters': {
            'employee': employee_id,
            'status': status,
            'leave_type': leave_type,
            'date_from': date_from,
            'date_to': date_to,
        }
    })

@login_required
def leave_approve(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.save()
        messages.success(request, 'Leave request approved successfully!')
    return redirect('leave_detail', pk=leave.pk)

@login_required
def leave_reject(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    if request.method == 'POST':
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.save()
        messages.success(request, 'Leave request rejected successfully!')
    return redirect('leave_detail', pk=leave.pk)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Payroll, Employee
from .forms import PayrollForm
from datetime import date
import json

def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save()
            messages.success(request, f'Payroll record for {payroll.employee} created successfully!')
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        initial = {
            'year': date.today().year,
            'month': date.today().month,
            'payment_date': date.today(),
        }
        form = PayrollForm(initial=initial)
    
    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Create Payroll Record'
    })

def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    
    # Prepare data for salary breakdown chart
    salary_breakdown = {
        'Basic Salary': float(payroll.basic_salary),
        'Allowances': float(payroll.total_allowances),
        'Tax': float(payroll.tax_amount),
        'Deductions': float(payroll.total_deductions),
    }
    
    # Prepare data for monthly salary trend (last 6 months)
    six_months_ago = date.today() - timedelta(days=180)
    monthly_data = Payroll.objects.filter(
        employee=payroll.employee,
        payment_date__gte=six_months_ago,
        payment_date__lte=date.today()
    ).order_by('year', 'month')
    
    months = []
    net_salary_data = []
    
    for record in monthly_data:
        months.append(f"{record.get_month_display()} {record.year}")
        net_salary_data.append(float(record.net_salary))
    
    chart_data = {
        'salary_breakdown': json.dumps(salary_breakdown),
        'months': json.dumps(months),
        'net_salary': json.dumps(net_salary_data),
    }
    
    return render(request, 'payroll/payroll_detail.html', {
        'payroll': payroll,
        'chart_data': chart_data,
    })

def payroll_update(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payroll record for {payroll.employee} updated successfully!')
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm(instance=payroll)
    
    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Update Payroll Record',
        'payroll': payroll
    })

def payroll_delete(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    
    if request.method == 'POST':
        employee_name = payroll.employee.user.get_full_name()
        period = payroll.get_pay_period_display()
        payroll.delete()
        messages.success(request, f'Payroll record for {employee_name} ({period}) deleted successfully!')
        return redirect('payroll_list')
    
    return render(request, 'payroll/payroll_confirm_delete.html', {
        'payroll': payroll
    })

def payroll_list(request):
    payrolls = Payroll.objects.all().order_by('-year', '-month', 'employee__user__last_name')
    
    # Filtering
    employee_id = request.GET.get('employee')
    year = request.GET.get('year')
    month = request.GET.get('month')
    status = request.GET.get('status')
    
    if employee_id:
        payrolls = payrolls.filter(employee__id=employee_id)
    if year:
        payrolls = payrolls.filter(year=year)
    if month:
        payrolls = payrolls.filter(month=month)
    if status:
        payrolls = payrolls.filter(payment_status=status)
    
    employees = Employee.objects.all()
    years = Payroll.objects.dates('period_start', 'year').distinct()
    
    return render(request, 'payroll/payroll_list.html', {
        'payrolls': payrolls,
        'employees': employees,
        'years': years,
        'month_choices': Payroll._meta.get_field('month').choices,
        'status_choices': Payroll.PAYMENT_STATUS_CHOICES,
    })

def payroll_process(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if request.method == 'POST':
        payroll.payment_status = 'processed'
        payroll.save()
        messages.success(request, f'Payroll for {payroll.employee} marked as processed!')
    return redirect('payroll_detail', pk=payroll.pk)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from .models import Product, ProductCategory, ProductVariant
from .forms import ProductForm, ProductVariantForm, ProductCategoryForm

# --- Product Category Views ---
def category_list(request):
    categories = ProductCategory.objects.filter(parent_category__isnull=True)
    return render(request, 'products/category_list.html', {'categories': categories})

def category_detail(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    subcategories = category.subcategories.all()
    products = category.products.all()
    return render(request, 'products/category_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'products': products
    })

def category_create(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = ProductCategoryForm()
    return render(request, 'products/category_form.html', {'form': form})

# --- Product Views ---
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse , HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.contrib import messages
from .models import Product, ProductCategory, ProductVariant
from .forms import ProductForm, ProductImportForm

def product_list(request):
    # Base queryset
    products = Product.objects.annotate(
        variant_count=Count('variants'))
    
    # Filtering
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    search_query = request.GET.get('q')
    
    if category_id:
        products = products.filter(category__id=category_id)
    if status:
        products = products.filter(status=status)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(product_code__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Get filter options
    categories = ProductCategory.objects.all()
    launch_years = Product.objects.dates('launch_date', 'year')
    
    # Pagination
    paginator = Paginator(products.order_by('-launch_date'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context for full page load
    context = {
        'products': page_obj,
        'categories': categories,
        'launch_years': [date.year for date in launch_years],
        'active_count': Product.objects.filter(status='active').count(),
        'variant_count': ProductVariant.objects.count(),
        'is_paginated': paginator.num_pages > 1
    }
    
    # AJAX response for HTMX requests
    # HTMX check - using headers instead of middleware
    if request.headers.get('HX-Request') == 'true':
        html = render_to_string(
            'products/partials/product_grid.html', 
            {'products': page_obj},
            request=request
        )
        return HttpResponse(html)
    
    return render(request, 'products/product_list.html', context)

def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(product_code__icontains=query)
    )[:10]
    
    html = render_to_string(
        'products/partials/search_results.html', 
        {'products': products},
        request=request
    )
    return HttpResponse(html)

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def quick_view(request, pk):
    try:
        product = get_object_or_404(
            Product.objects.select_related('category'),
            pk=pk
        )
        variants = product.variants.all()
        
        return render(request, 'products/partials/quick_view.html', {
            'product': product,
            'variants': variants,
            'user_has_edit_perms': request.user.has_perm('products.change_product')
        })
        
    except Exception as e:
        logger.error(f"Quick view error for product {pk}: {str(e)}")
        return render(request, 'products/partials/error.html', {
            'error': 'Failed to load product details. Please try again later.'
        }, status=500)


def import_csv(file, update_existing: bool) -> tuple[int, int, list[dict]]:
    """Returns: (success_count, error_count, error_list)"""
    ...

from django.http import JsonResponse
from .forms import ProductImportForm

def import_products(request):
    if request.method == 'POST':
        form = ProductImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                success_count, error_count, error_list = import_csv(
                    form.cleaned_data['csv_file'],
                    form.cleaned_data['update_existing']
                )
                
                return JsonResponse({
                    'status': 'success',
                    'imported': success_count,
                    'errors': error_count,
                    'error_samples': error_list[:5] if error_count > 0 else None
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
        
        # Return form errors if validation fails
        return JsonResponse({
            'status': 'error',
            'errors': form.errors.get_json_data()
        }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST requests are allowed'
    }, status=405)

def toggle_product_status(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.status = 'discontinued' if product.status == 'active' else 'active'
        product.save()
        return JsonResponse({
            'status': 'success',
            'new_status': product.get_status_display(),
            'is_active': product.status == 'active'
        })
    return JsonResponse({'status': 'error'}, status=405)
    return render(request, 'products/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'variants': variants
    })

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product {product.name} created!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

# --- Product Variant Views ---
def variant_create(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            messages.success(request, f'Variant {variant.name} added!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductVariantForm()
    return render(request, 'products/variant_form.html', {
        'form': form,
        'product': product
    })


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Warehouse, InventoryItem
from .forms import WarehouseForm

def warehouse_list(request):
    warehouses = Warehouse.objects.all().order_by('name')
    paginator = Paginator(warehouses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'warehouses': page_obj.object_list,
    }
    return render(request, 'inventory/warehouse_list.html', context)

def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('warehouse_list')
    else:
        form = WarehouseForm()
    
    return render(request, 'inventory/warehouse_form.html', {'form': form})

def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect('warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'inventory/warehouse_form.html', {'form': form})

def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    inventory_items = InventoryItem.objects.filter(warehouse=warehouse)
    
    context = {
        'warehouse': warehouse,
        'inventory_items': inventory_items,
    }
    return render(request, 'inventory/warehouse_detail.html', context)



# views.py
from .models import StockMovement
from .forms import StockMovementForm

def stock_movement_list(request):
    movements = StockMovement.objects.all().order_by('-date')
    paginator = Paginator(movements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'movements': page_obj.object_list,
    }
    return render(request, 'inventory/stock_movement_list.html', context)

def stock_movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.performed_by = request.user
            movement.save()
            
            # Update inventory quantity
            inventory_item = movement.inventory_item
            if movement.movement_type == 'in':
                inventory_item.quantity += movement.quantity_change
            else:
                inventory_item.quantity -= movement.quantity_change
            inventory_item.save()
            
            return redirect('stock_movement_list')
    else:
        form = StockMovementForm()
    
    return render(request, 'inventory/stock_movement_form.html', {'form': form})




# views.py
from .models import PurchaseOrder, PurchaseOrderItem
from .forms import PurchaseOrderForm, PurchaseOrderItemFormSet

def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().order_by('-order_date')
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
    }
    return render(request, 'inventory/purchase_order_list.html', context)

def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                    item = item_form.save(commit=False)
                    item.purchase_order = order
                    item.save()
            
            action = request.POST.get('action', 'save_draft')
            if action == 'submit_order':
                order.status = 'sent'
                order.save()
            
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm(initial={'status': 'draft'})  # Set default status
        formset = PurchaseOrderItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'content_types': ContentType.objects.filter(model__in=['ingredient', 'productvariant'])
    }
    return render(request, 'inventory/purchase_order_form.html', context)

def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    items = order.items.all()
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'inventory/purchase_order_detail.html', context)




# views.py
from .models import Supplier
from .forms import SupplierForm

def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    status_filter = request.GET.get('status')
    
    if status_filter:
        suppliers = suppliers.filter(status=status_filter)
    
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'suppliers': page_obj.object_list,
    }
    return render(request, 'inventory/supplier_list.html', context)

def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    
    return render(request, 'inventory/supplier_form.html', {'form': form})

def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    purchase_orders = supplier.purchase_orders.all()
    
    context = {
        'supplier': supplier,
        'purchase_orders': purchase_orders,
    }
    return render(request, 'inventory/supplier_detail.html', context)


def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'inventory/supplier_form.html', {'form': form, 'supplier': supplier})

from django.views.decorators.http import require_POST
@require_POST
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect('supplier_list')

# views.py
from django.db.models import Q

def low_stock_alerts(request):
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).select_related('product_variant', 'warehouse')
    
    # Calculate critical items (below 50% of reorder level)
    critical_count = low_stock_items.filter(
        quantity__lte=models.F('reorder_level') * 0.5
    ).count()
    
    # Warning items are the rest (above 50% but below reorder level)
    warning_count = low_stock_items.count() - critical_count
    
    context = {
        'low_stock_items': low_stock_items,
        'critical_count': critical_count,
        'warning_count': warning_count,
    }
    return render(request, 'inventory/low_stock_alerts.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer
from .forms import CustomerForm

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers/customer_list.html', {'customers': customers})

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Create Customer'})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Update Customer'})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DeliveryVehicle
from .forms import DeliveryVehicleForm

def vehicle_list(request):
    vehicles = DeliveryVehicle.objects.select_related('driver').all()
    context = {
        'vehicles': vehicles,
        'status_counts': {
            'available': vehicles.filter(status='available').count(),
            'in_transit': vehicles.filter(status='in_transit').count(),
            'maintenance': vehicles.filter(status='maintenance').count()
        }
    }
    return render(request, 'delivery/vehicle_list.html', context)

def vehicle_create(request):
    if request.method == 'POST':
        form = DeliveryVehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} created successfully!')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = DeliveryVehicleForm()
    
    return render(request, 'delivery/vehicle_form.html', {
        'form': form,
        'title': 'Register New Vehicle',
        'action': 'Create'
    })

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import DeliveryVehicle

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(
        DeliveryVehicle.objects.select_related('driver')
                              .prefetch_related('maintenance_records'), 
        pk=pk
    )
    
    # Maintenance records pagination
    maintenance_records = vehicle.maintenance_records.all().order_by('-date')
    paginator = Paginator(maintenance_records, 5)  # Show 5 records per page
    page_number = request.GET.get('page')
    maintenance_page = paginator.get_page(page_number)
    
    context = {
        'vehicle': vehicle,
        'maintenance_page': maintenance_page,
        'maintenance_count': maintenance_records.count(),
        'last_maintenance': maintenance_records.first(),
        #'maintenance_due': vehicle.maintenance_due,  # From the model property we added earlier
    }
    
    return render(request, 'delivery/vehicle_detail.html', context)

def vehicle_update(request, pk):
    vehicle = get_object_or_404(DeliveryVehicle, pk=pk)
    if request.method == 'POST':
        form = DeliveryVehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} updated successfully!')
            return redirect('vehicle_detail', pk=vehicle.pk)
    else:
        form = DeliveryVehicleForm(instance=vehicle)
    
    return render(request, 'delivery/vehicle_form.html', {
        'form': form,
        'title': f'Update {vehicle.vehicle_number}',
        'action': 'Update'
    })

def vehicle_delete(request, pk):
    vehicle = get_object_or_404(DeliveryVehicle, pk=pk)
    if request.method == 'POST':
        vehicle_number = vehicle.vehicle_number
        vehicle.delete()
        messages.success(request, f'Vehicle {vehicle_number} deleted successfully!')
        return redirect('vehicle_list')
    
    return render(request, 'delivery/vehicle_confirm_delete.html', {'vehicle': vehicle})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import DeliveryVehicle

@login_required
def vehicle_update_status(request, pk):
    """
    View to handle vehicle status updates from the detail page
    """
    vehicle = get_object_or_404(DeliveryVehicle, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Validate the status is one of our choices
        valid_statuses = dict(DeliveryVehicle.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status selected')
            return redirect('vehicle_detail', pk=vehicle.pk)
        
        # Check for business logic constraints
        if new_status == 'available':
            active_count = vehicle.deliveries.filter(
                status__in=['scheduled', 'in_transit']
            ).count()
            if active_count > 0:
                messages.warning(
                    request,
                    f"Cannot set status to Available while vehicle has {active_count} active deliveries"
                )
                return redirect('delivery:vehicle_detail', pk=vehicle.pk)
        
        # Check if driver is assigned when setting to in_transit
        if new_status == 'in_transit' and not vehicle.driver:
            messages.warning(
                request,
                "Cannot set status to In Transit without an assigned driver"
            )
            return redirect('delivery:vehicle_detail', pk=vehicle.pk)
        
        # Update the status
        old_status = vehicle.get_status_display()
        vehicle.status = new_status
        vehicle.save()
        
        # Log the status change
        vehicle.status_logs.create(
            user=request.user,
            from_status=old_status,
            to_status=vehicle.get_status_display(),
            notes=f"Status changed via quick update"
        )
        
        messages.success(
            request,
            f"Vehicle {vehicle.vehicle_number} status updated from {old_status} to {vehicle.get_status_display()}"
        )
    
    return redirect('vehicle_detail', pk=vehicle.pk)



@login_required
def vehicle_upload_image(request, pk):
    vehicle = get_object_or_404(DeliveryVehicle, pk=pk)
    
    if request.method == 'POST':
        # Check if image was provided
        if 'image' not in request.FILES:
            messages.error(request, "No image file provided")
            return redirect('vehicle_detail', pk=vehicle.pk)
        
        # Validate image size (max 5MB)
        image_file = request.FILES['image']
        if image_file.size > 5 * 1024 * 1024:  # 5MB
            messages.error(request, "Image file too large (max 5MB)")
            return redirect('vehicle_detail', pk=vehicle.pk)
        
        # Save the new image
        if vehicle.image:
            vehicle.image.delete()  # Remove old image
        vehicle.image = image_file
        vehicle.save()
        
        messages.success(request, "Vehicle image updated successfully")
        return redirect('vehicle_detail', pk=vehicle.pk)




from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import DeliveryVehicle, MaintenanceRecord

@login_required
def vehicle_add_maintenance(request, pk):
    vehicle = get_object_or_404(DeliveryVehicle, pk=pk)
    
    if request.method == 'POST':
        try:
            # Validate date is not in the future
            date = request.POST.get('date')
            if date > now().date().isoformat():
                messages.error(request, "Maintenance date cannot be in the future")
                return redirect('vehicle_detail', pk=vehicle.pk)
            
            # Create maintenance record
            MaintenanceRecord.objects.create(
                vehicle=vehicle,
                maintenance_type=request.POST.get('maintenance_type'),
                date=date,
                description=request.POST.get('description'),
                cost=request.POST.get('cost') or None,
                created_by=request.user
            )
            
            messages.success(request, "Maintenance record added successfully")
            
            # If vehicle was in maintenance, mark as available if appropriate
            if vehicle.status == 'maintenance' and request.POST.get('maintenance_type') != 'repair':
                vehicle.status = 'available'
                vehicle.save()
                messages.info(request, "Vehicle status changed to Available")
                
        except Exception as e:
            messages.error(request, f"Error adding maintenance record: {str(e)}")
    
    return redirect('vehicle_detail', pk=vehicle.pk)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *

# Facilities
from django.db.models import Sum
from django.shortcuts import render
from .models import ProductionFacility, FacilityChangeLog

from django.db.models import Sum
from django.shortcuts import render
from .models import ProductionFacility, FacilityChangeLog

def facility_list(request):
    facilities = ProductionFacility.objects.select_related('manager').all()
    active_count = facilities.filter(status='active').count()
    
    # Get recent changes for the sidebar
    recent_changes = FacilityChangeLog.objects.select_related(
        'facility', 'user'
    ).order_by('-changed_at')[:5]
    
    # Calculate total capacity in the view instead of template
    total_capacity = facilities.aggregate(total=Sum('capacity'))['total'] or 0
    
    return render(request, 'production/facility_list.html', {
        'facilities': facilities,
        'active_count': active_count,
        'total_capacity': total_capacity,
        'recent_changes': recent_changes,
        'page_title': 'Production Facilities Management',
    })

def facility_create(request):
    if request.method == 'POST':
        form = ProductionFacilityForm(request.POST)
        if form.is_valid():
            facility = form.save()
            messages.success(request, f'{facility.name} created successfully!')
            return redirect('facility_detail', pk=facility.pk)
    else:
        form = ProductionFacilityForm()
    return render(request, 'production/facility_form.html', {'form': form})

@login_required
def facility_update(request, pk):
    facility = get_object_or_404(ProductionFacility, pk=pk)
    
    if request.method == 'POST':
        form = ProductionFacilityForm(request.POST, instance=facility)
        if form.is_valid():
            updated_facility = form.save()
            
            # Log the change
            FacilityChangeLog.objects.create(
                facility=updated_facility,
                user=request.user,
                changed_fields=', '.join(form.changed_data),
                notes=f"Updated via facility update form"
            )
            
            messages.success(
                request, 
                f"{updated_facility.name} updated successfully"
            )
            return redirect('production:facility_detail', pk=updated_facility.pk)
    else:
        form = ProductionFacilityForm(instance=facility)
    
    context = {
        'form': form,
        'facility': facility,
        'title': f'Update {facility.name}',
        'action': 'Update'
    }
    return render(request, 'production/facility_form.html', context)

def facility_detail(request, pk):
    facility = get_object_or_404(ProductionFacility.objects.prefetch_related('production_lines'), pk=pk)
    return render(request, 'production/facility_detail.html', {'facility': facility})


from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import ProductionFacility, FacilityChangeLog

def facility_changelog(request, pk):
    facility = get_object_or_404(ProductionFacility, pk=pk)
    changelog_entries = FacilityChangeLog.objects.filter(
        facility=facility
    ).select_related('user').order_by('-changed_at')
    
    # Pagination - 10 items per page
    paginator = Paginator(changelog_entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'facility': facility,
        'page_obj': page_obj,
        'title': f'Change Log - {facility.name}',
    }
    return render(request, 'production/facility_changelog.html', context)
# Production Lines

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import ProductionLine, ProductionFacility
from .forms import ProductionLineForm

def create_production_line(request, facility_id):
    facility = get_object_or_404(ProductionFacility, pk=facility_id)
    
    if request.method == 'POST':
        form = ProductionLineForm(request.POST)
        if form.is_valid():
            production_line = form.save(commit=False)
            production_line.facility = facility
            production_line.save()
            form.save_m2m()  # Required for saving many-to-many relations (like product_types)
            
            messages.success(
                request,
                f"Successfully created new production line: {production_line.name}"
            )
            return redirect('facility_detail', pk=facility_id)
    else:
        initial = {'facility': facility_id}
        form = ProductionLineForm(initial=initial)
    
    context = {
        'form': form,
        'facility': facility,
        'title': f"Add New Production Line to {facility.name}",
    }
    
    return render(request, 'production/line_form.html', context)


from django.shortcuts import render
from django.db.models import Count, Q
from .models import ProductionLine

def production_line_list(request):
    # Get all production lines with optimized queries
    lines = ProductionLine.objects.select_related('facility')\
                                 .prefetch_related('product_types')\
                                 .annotate(
                                     product_count=Count('product_types')
                                 ).order_by('facility__name', 'name')
    
    # Calculate status counts
    status_counts = {
        'operational': lines.filter(status='operational').count(),
        'maintenance': lines.filter(status='maintenance').count(),
        'inactive': lines.filter(status='inactive').count(),
    }
    
    # Get total production capacity
    total_capacity = lines.aggregate(total=Sum('capacity_per_hour'))['total'] or 0
    
    context = {
        'lines': lines,
        'status_counts': status_counts,
        'total_capacity': total_capacity,
        'total_lines': lines.count(),
        'page_title': 'Production Lines Management',
    }
    return render(request, 'production/line_list.html', context)

def production_line_create(request):
    if request.method == 'POST':
        form = ProductionLineForm(request.POST)
        if form.is_valid():
            line = form.save()
            messages.success(request, f'Production line {line.name} created!')
            return redirect('line_detail', pk=line.pk)
    else:
        form = ProductionLineForm()
    return render(request, 'production/line_form.html', {'form': form})

from .utils import calculate_uptime
@login_required
def production_line_detail(request, pk):
    line = get_object_or_404(
        ProductionLine.objects.select_related('facility')
                            .prefetch_related('product_types', 'batches', 'maintenance_schedules'),
        pk=pk
    )
    
    # Get stats for dashboard
    active_batches = line.batches.filter(end_time__isnull=True)
    scheduled_maintenance = line.maintenance_schedules.filter(status='scheduled')
    recent_downtime = DowntimeIncident.objects.filter(
        production_line=line,
        end_time__isnull=False
    ).order_by('-start_time')[:3]
    
    context = {
        'line': line,
        'active_batches': active_batches,
        'scheduled_maintenance': scheduled_maintenance,
        'recent_downtime': recent_downtime,
        'product_types': line.product_types.all(),
        'uptime_last_week': calculate_uptime(line),  # Custom function you'd implement
    }
    return render(request, 'production/line_detail.html', context)





# Downtime
def downtime_list(request):
    incidents = DowntimeIncident.objects.select_related('production_line', 'reported_by')
    return render(request, 'production/downtime_list.html', {
        'incidents': incidents,
        'active': incidents.filter(end_time__isnull=True).count(),
    })

def downtime_create(request):
    if request.method == 'POST':
        form = DowntimeIncidentForm(request.POST)
        if form.is_valid():
            downtime = form.save()
            messages.warning(request, f'Downtime reported for {downtime.production_line.name}')
            return redirect('downtime_list')
    else:
        form = DowntimeIncidentForm()
    return render(request, 'production/downtime_form.html', {'form': form})

# Batches
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from .models import ProductionBatch, ProductionLine, Product

def batch_list(request):
    # Get all batches with optimized queries
    batches = ProductionBatch.objects.select_related(
        'production_line__facility',
        'product'
    ).order_by('-start_time')
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter in ['pending', 'passed', 'failed']:
        batches = batches.filter(quality_check_status=status_filter)
    
    line_filter = request.GET.get('line')
    if line_filter:
        batches = batches.filter(production_line_id=line_filter)
    
    # Statistics
    total_quantity = batches.aggregate(total=Sum('quantity_produced'))['total'] or 0
    status_counts = batches.values('quality_check_status').annotate(count=Count('id'))
    
    context = {
        'batches': batches,
        'production_lines': ProductionLine.objects.all(),
        'total_quantity': total_quantity,
        'status_counts': status_counts,
        'current_status_filter': status_filter,
        'current_line_filter': line_filter,
        'page_title': 'Production Batch Management',
    }
    return render(request, 'production/batch_list.html', context)



from .forms import ProductionBatchForm

def batch_create(request):
    if request.method == 'POST':
        form = ProductionBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.batch_number = generate_batch_number()  # Custom function needed
            batch.save()
            
            messages.success(
                request,
                f'Batch {batch.batch_number} created successfully! '
                f'Produced {batch.quantity_produced} units of {batch.product.name}'
            )
            return redirect('batch_detail', pk=batch.pk)
    else:
        form = ProductionBatchForm(initial={
            'start_time': timezone.now(),
            'quality_check_status': 'pending'
        })
    
    context = {
        'form': form,
        'title': 'Create New Production Batch',
    }
    return render(request, 'production/batch_form.html', context)

# Helper function (put in utils.py)
def generate_batch_number():
    now = timezone.now()
    return f"CC-{now.year}{now.month:02d}{now.day:02d}-{now.hour:02d}{now.minute:02d}"



def batch_detail(request, pk):
    batch = get_object_or_404(
        ProductionBatch.objects.select_related(
            'production_line__facility',
            'product'
        ),
        pk=pk
    )
    
    # Calculate duration
    duration = None
    duration_hours = 0
    duration_minutes = 0
    if batch.end_time:
        duration = batch.end_time - batch.start_time
        duration_hours = duration.seconds // 3600
        duration_minutes = (duration.seconds % 3600) // 60
    
    # Calculate approximate pallets (assuming 100 units per pallet)
    pallets = batch.quantity_produced / 100
    
    context = {
        'batch': batch,
        'duration_hours': duration_hours,
        'duration_minutes': duration_minutes,
        'pallets': pallets,
        'page_title': f'Batch {batch.batch_number}',
    }
    return render(request, 'production/batch_detail.html', context)



def batch_update(request, pk):
    batch = get_object_or_404(ProductionBatch, pk=pk)
    
    if request.method == 'POST':
        form = ProductionBatchForm(request.POST, instance=batch)
        if form.is_valid():
            updated_batch = form.save()
            
            messages.success(
                request,
                f'Batch {updated_batch.batch_number} updated successfully!'
            )
            return redirect('batch_detail', pk=updated_batch.pk)
    else:
        form = ProductionBatchForm(instance=batch)
    
    context = {
        'form': form,
        'batch': batch,
        'title': f'Update Batch {batch.batch_number}',
    }
    return render(request, 'production/batch_form.html', context)



from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from .models import MaintenanceSchedule

# Maintenance
def maintenance_list(request):
    schedules = MaintenanceSchedule.objects.select_related('production_line', 'assigned_technician')
    return render(request, 'maintenance/maintenance_list.html', {
        'schedules': schedules,
        'upcoming': schedules.filter(status='scheduled').count(),
    })

def maintenance_create(request):
    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, f'Maintenance scheduled for {maintenance.production_line.name}')
            return redirect('maintenance_list')
    else:
        form = MaintenanceScheduleForm()
    return render(request, 'production/maintenance_form.html', {'form': form})


def maintenance_dashboard(request):
    # Get counts for different statuses
    status_counts = MaintenanceSchedule.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Get overdue maintenance (scheduled but not completed past their date)
    overdue = MaintenanceSchedule.objects.filter(
        scheduled_date__lt=timezone.now(),
        status__in=['scheduled', 'in_progress']
    ).select_related('production_line', 'assigned_technician')
    
    # Get upcoming maintenance (next 7 days)
    upcoming = MaintenanceSchedule.objects.filter(
        scheduled_date__range=[
            timezone.now(),
            timezone.now() + timezone.timedelta(days=7)
        ],
        status='scheduled'
    ).select_related('production_line', 'assigned_technician')
    
    # Maintenance by type statistics
    maintenance_types = MaintenanceSchedule.objects.values(
        'maintenance_type'
    ).annotate(
        count=Count('id'),
        completed=Count('id', filter=Q(status='completed'))
    )
    
    context = {
        'status_counts': status_counts,
        'overdue_maintenance': overdue,
        'upcoming_maintenance': upcoming,
        'maintenance_types': maintenance_types,
        'current_date': timezone.now(),
    }
    return render(request, 'maintenance/dashboard.html', context)


from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .forms import MaintenanceScheduleForm

def create_maintenance_schedule(request, line_id=None):
    initial = {}
    production_line = None
    
    if line_id:
        production_line = get_object_or_404(ProductionLine, pk=line_id)
        initial['production_line'] = production_line
    
    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST)  # Remove initial from POST form
        if form.is_valid():
            maintenance = form.save(commit=False)
            
            # Ensure production_line is set if it came from line_id
            if line_id and production_line:
                maintenance.production_line = production_line
            
            maintenance.status = 'scheduled'
            maintenance.save()
            
            # Log maintenance creation
            MaintenanceLog.objects.create(
                maintenance=maintenance,
                action='created',
                user=request.user,
                notes=f"Scheduled {maintenance.maintenance_type} maintenance"
            )
            
            messages.success(
                request,
                f"{maintenance.maintenance_type} maintenance scheduled for "
                f"{maintenance.production_line.name} on "
                f"{maintenance.scheduled_date.strftime('%b %d, %Y %H:%M')}"
            )
            return redirect('maintenance_detail', pk=maintenance.pk)
        else:
            # Debug if form is not valid
            print(f"Form errors: {form.errors}")
    else:
        form = MaintenanceScheduleForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Schedule New Maintenance',
        'production_line': production_line,
    }
    return render(request, 'maintenance/schedule_form.html', context)


def maintenance_detail(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    
    # Get maintenance logs for this maintenance
    logs = MaintenanceLog.objects.filter(maintenance=maintenance).order_by('-timestamp')
    
    # Calculate downtime if maintenance is completed
    downtime = None
    if maintenance.status == 'completed' and maintenance.actual_start and maintenance.actual_end:
        downtime = maintenance.actual_end - maintenance.actual_start
    
    context = {
        'maintenance': maintenance,
        'logs': logs,
        'downtime': downtime,
        'title': f'Maintenance Details: {maintenance.maintenance_type}',
    }
    
    return render(request, 'maintenance/maintenance_detail.html', context)

def start_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    
    if maintenance.status != 'scheduled':
        messages.error(
            request,
            "Maintenance can only be started from 'scheduled' status"
        )
        return redirect('maintenance_detail', pk=pk)
    
    maintenance.status = 'in_progress'
    maintenance.actual_start = timezone.now()
    maintenance.save()
    
    # Create log entry
    MaintenanceLog.objects.create(
        maintenance=maintenance,
        action='started',
        user=request.user,
        notes="Maintenance work begun"
    )
    
    messages.success(
        request,
        f"Maintenance on {maintenance.production_line.name} has begun"
    )
    return redirect('maintenance_detail', pk=pk)

def complete_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceSchedule, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceCompletionForm(request.POST, instance=maintenance)
        if form.is_valid():
            completed_maintenance = form.save(commit=False)
            completed_maintenance.status = 'completed'
            completed_maintenance.actual_end = timezone.now()
            completed_maintenance.save()
            
            # Calculate downtime impact
            downtime = (completed_maintenance.actual_end - completed_maintenance.actual_start)
            
            # Create log entry
            MaintenanceLog.objects.create(
                maintenance=completed_maintenance,
                action='completed',
                user=request.user,
                notes=f"Completed with notes: {form.cleaned_data['completion_notes']}"
            )
            
            messages.success(
                request,
                f"Maintenance completed successfully. Downtime: {downtime}"
            )
            return redirect('maintenance_detail', pk=pk)
    else:
        form = MaintenanceCompletionForm(instance=maintenance)
    
    context = {
        'form': form,
        'maintenance': maintenance,
        'title': 'Complete Maintenance',
    }
    return render(request, 'maintenance/complete_form.html', context)


from django.db.models.functions import TruncMonth
from django.db.models import Avg, F

def maintenance_analytics(request):
    # Monthly maintenance counts
    monthly_data = MaintenanceSchedule.objects.annotate(
        month=TruncMonth('scheduled_date')
    ).values('month').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed'))
    ).order_by('month')
    
    # Average duration by type
    duration_stats = MaintenanceSchedule.objects.filter(
        status='completed'
    ).values('maintenance_type').annotate(
        avg_estimated=Avg(F('estimated_duration')),
        avg_actual=Avg(F('actual_end') - F('actual_start'))
    )
    
    # Technician workload
    technician_workload = Employee.objects.filter(
        maintenance_assignments__isnull=False
    ).annotate(
        assigned=Count('maintenance_assignments'),
        completed=Count('maintenance_assignments', filter=Q(maintenance_assignments__status='completed'))
    ).order_by('-assigned')
    
    context = {
        'monthly_data': monthly_data,
        'duration_stats': duration_stats,
        'technician_workload': technician_workload,
    }
    return render(request, 'maintenance/analytics.html', context)


from datetime import datetime, timedelta

from datetime import datetime, timedelta
from django.shortcuts import render

def maintenance_calendar(request):
    # Parse month parameter (format: MM/YYYY)
    month_str = request.GET.get('month')
    if month_str:
        try:
            month, year = map(int, month_str.split('/'))
        except (ValueError, AttributeError):
            # Fallback to current month if invalid format
            today = datetime.now()
            month, year = today.month, today.year
    else:
        today = datetime.now()
        month, year = today.month, today.year
    
    # Calculate date range
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get maintenance for this period
    maintenance = MaintenanceSchedule.objects.filter(
        scheduled_date__gte=start_date,
        scheduled_date__lt=end_date
    ).select_related('production_line', 'assigned_technician')
    
    # Prepare calendar data in weekly chunks
    calendar_weeks = []
    current_day = start_date
    week = []
    
    # Add days from previous month if needed
    if current_day.weekday() != 6:  # If not Sunday
        prev_days = current_day.weekday() + 1
        prev_date = current_day - timedelta(days=prev_days)
        for i in range(prev_days):
            week.append({
                'date': prev_date + timedelta(days=i),
                'maintenance': [],
                'is_weekend': (prev_date + timedelta(days=i)).weekday() >= 5,
                'in_month': False
            })
    
    # Add current month days
    while current_day < end_date:
        day_maintenance = [m for m in maintenance if m.scheduled_date.date() == current_day.date()]
        week.append({
            'date': current_day,
            'maintenance': day_maintenance,
            'is_weekend': current_day.weekday() >= 5,
            'in_month': True
        })
        
        if len(week) == 7:
            calendar_weeks.append(week)
            week = []
        
        current_day += timedelta(days=1)
    
    # Add days from next month if needed
    if week:
        remaining_days = 7 - len(week)
        for i in range(1, remaining_days + 1):
            week.append({
                'date': current_day,
                'maintenance': [],
                'is_weekend': current_day.weekday() >= 5,
                'in_month': False
            })
            current_day += timedelta(days=1)
        calendar_weeks.append(week)
    
    # Format navigation dates
    prev_month = (start_date - timedelta(days=1)).strftime('%m/%Y')
    next_month = end_date.strftime('%m/%Y')
    
    context = {
        'calendar_weeks': calendar_weeks,
        'month': start_date.strftime('%B %Y'),
        'prev_month': prev_month,
        'next_month': next_month,
    }
    return render(request, 'maintenance/calendar.html', context)


import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

#finance departent views 
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Account, Transaction, Payment, Invoice, SalesOrder, Budget, TaxRecord

def finance_dashboard(request):
    # Date ranges
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    thirty_days_ago = today - timedelta(days=30)
    
    ## 1. Financial Position Summary
    # Account balances by type
    account_balances = Account.objects.filter(is_active=True).values(
        'account_type'
    ).annotate(
        total_balance=Sum('balance')
    ).order_by('account_type')
    
    # Convert to dictionary for easier access
    balance_summary = {item['account_type']: item['total_balance'] for item in account_balances}
    
    ## 2. Cash Flow Overview
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        status='posted',
        transaction_date__gte=thirty_days_ago
    ).order_by('-transaction_date')[:10]
    
    # Payment methods breakdown
    payment_methods = Payment.objects.filter(
        payment_date__gte=thirty_days_ago
    ).values('payment_method').annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    )
    
    ## 3. Revenue Tracking
    # Invoice status summary
    invoice_summary = Invoice.objects.aggregate(
        total_invoiced=Sum('total_amount'),
        unpaid=Sum('total_amount', filter=Q(status='unpaid')),
        partial=Sum('total_amount', filter=Q(status='partial')),
        paid=Sum('total_amount', filter=Q(status='paid'))
    )
    
    # Sales by customer type
    sales_by_customer_type = SalesOrder.objects.filter(
        order_date__gte=start_of_year
    ).values('customer__customer_type').annotate(
        total_sales=Sum('total_amount')
    )
    
    ## 4. Budget vs Actual
    # Current period budget performance
    budget_performance = Budget.objects.filter(
        fiscal_year=str(today.year),
        period='monthly'
    ).select_related('account', 'department').annotate(
        actual_spend=Sum('account__transaction_entries__amount',
                        filter=Q(account__transaction_entries__entry_type='debit') &
                               Q(account__transaction_entries__transaction__transaction_date__gte=start_of_month))
    )[:5]
    
    ## 5. Tax Compliance
    # Tax obligations
    tax_summary = TaxRecord.objects.filter(
        period_end__gte=start_of_year
    ).values('tax_type', 'status').annotate(
        total_amount=Sum('amount')
    )
    
    # Convert Decimal objects to float for JavaScript compatibility
    account_balance_labels = [dict(Account.ACCOUNT_TYPE_CHOICES).get(t) for t in balance_summary.keys()]
    account_balance_data = [float(value) for value in balance_summary.values()]
    
    payment_method_labels = [p['payment_method'] for p in payment_methods]
    payment_method_data = [float(p['total_amount']) for p in payment_methods]
    
    sales_customer_labels = [s['customer__customer_type'] for s in sales_by_customer_type]
    sales_customer_data = [float(s['total_sales']) for s in sales_by_customer_type]
    
    budget_labels = [b.account.name for b in budget_performance]
    budget_data = [float(b.amount) for b in budget_performance]
    actual_data = [float(b.actual_spend or 0) for b in budget_performance]
    
    context = {
        # Summary Cards
        'summary_cards': [
            {
                'title': 'Total Assets',
                'value': balance_summary.get('asset', 0),
                'icon': 'fa-piggy-bank',
                'color': 'success'
            },
            {
                'title': 'Total Liabilities',
                'value': balance_summary.get('liability', 0),
                'icon': 'fa-hand-holding-usd',
                'color': 'danger'
            },
            {
                'title': 'Monthly Revenue',
                'value': invoice_summary.get('paid', 0),
                'icon': 'fa-chart-line',
                'color': 'info'
            },
            {
                'title': 'Pending Invoices',
                'value': invoice_summary.get('unpaid', 0),
                'icon': 'fa-file-invoice-dollar',
                'color': 'warning'
            },
        ],
        
        # Charts Data (pre-converted to float)
        'charts': {
            # Account Balances Pie Chart
            'account_balances': {
                'labels': account_balance_labels,
                'data': account_balance_data,
                'type': 'pie'
            },
            
            # Payment Methods Breakdown
            'payment_methods': {
                'labels': payment_method_labels,
                'data': payment_method_data,
                'type': 'bar'
            },
            
            # Sales by Customer Type
            'sales_by_customer_type': {
                'labels': sales_customer_labels,
                'data': sales_customer_data,
                'type': 'doughnut'
            },
            
            # Monthly Budget Performance
            'budget_performance': {
                'labels': budget_labels,
                'budget': budget_data,
                'actual': actual_data,
                'type': 'bar'
            }
        },
        
        # Tables
        'recent_transactions': recent_transactions,
        'budget_performance': budget_performance,
        'tax_summary': tax_summary,
        
        # Additional context
        'current_period': f"{start_of_month.strftime('%B %Y')}",
        'fiscal_year': today.year
    }
    
    return render(request, 'finance/dashboard.html', context)



from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Transaction, TransactionEntry
from .forms import TransactionForm, TransactionEntryFormSet

class TransactionListView(ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('created_by', 'approved_by')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(reference_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
            
        return queryset.order_by('-transaction_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Transaction.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.object.entries.all().select_related('account')
        return context


class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transaction_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['entry_formset'] = TransactionEntryFormSet(self.request.POST)
        else:
            context['entry_formset'] = TransactionEntryFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        entry_formset = context['entry_formset']
        
        if entry_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()
            
            entries = entry_formset.save(commit=False)
            for entry in entries:
                entry.transaction = self.object
                entry.save()
                
                # Update account balance
                account = entry.account
                if entry.entry_type == 'debit':
                    account.balance += entry.amount
                else:
                    account.balance -= entry.amount
                account.save()
            
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    
    def get_success_url(self):
        return reverse_lazy('transaction_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['entry_formset'] = TransactionEntryFormSet(self.request.POST, instance=self.object)
        else:
            context['entry_formset'] = TransactionEntryFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        entry_formset = context['entry_formset']
        
        if entry_formset.is_valid():
            # First, reverse all existing entries' impact on account balances
            for entry in self.object.entries.all():
                account = entry.account
                if entry.entry_type == 'debit':
                    account.balance -= entry.amount
                else:
                    account.balance += entry.amount
                account.save()
            
            # Save the transaction and new entries
            self.object = form.save()
            entries = entry_formset.save(commit=False)
            
            for entry in entries:
                entry.transaction = self.object
                entry.save()
                
                # Update account balance with new values
                account = entry.account
                if entry.entry_type == 'debit':
                    account.balance += entry.amount
                else:
                    account.balance -= entry.amount
                account.save()
            
            # Delete any entries marked for deletion
            for entry in entry_formset.deleted_objects:
                entry.delete()
                
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
    
    def delete(self, request, *args, **kwargs):
        # First, reverse all entries' impact on account balances
        transaction = self.get_object()
        for entry in transaction.entries.all():
            account = entry.account
            if entry.entry_type == 'debit':
                account.balance -= entry.amount
            else:
                account.balance += entry.amount
            account.save()
        
        return super().delete(request, *args, **kwargs)
    



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from .models import Customer, SalesOrder, SalesOrderItem, Invoice, ProductVariant
from .forms import CustomerForm, SalesOrderForm, SalesOrderItemFormSet, InvoiceForm

class SalesRecordingView(View):
    template_name = 'sales/sales_recording.html'
    
    def get(self, request):
        # Initialize forms
        customer_form = CustomerForm(prefix='customer')
        sales_order_form = SalesOrderForm(prefix='order')
        sales_order_item_formset = SalesOrderItemFormSet(prefix='items')
        invoice_form = InvoiceForm(prefix='invoice')
        
        # Generate a new order number based on current date (example: SO-20250507-001)
        today = timezone.now().date()
        order_number = f"SO-{today.strftime('%Y%m%d')}-001"
        
        # Check if there's an existing order for today and increment
        existing_orders = SalesOrder.objects.filter(
            order_number__startswith=f"SO-{today.strftime('%Y%m%d')}"
        ).order_by('order_number')
        
        if existing_orders.exists():
            last_order = existing_orders.last()
            last_number = int(last_order.order_number.split('-')[-1])
            order_number = f"SO-{today.strftime('%Y%m%d')}-{str(last_number + 1).zfill(3)}"
        
        # Generate invoice number
        invoice_number = f"INV-{today.strftime('%Y%m%d')}-001"
        existing_invoices = Invoice.objects.filter(
            invoice_number__startswith=f"INV-{today.strftime('%Y%m%d')}"
        ).order_by('invoice_number')
        
        if existing_invoices.exists():
            last_invoice = existing_invoices.last()
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            invoice_number = f"INV-{today.strftime('%Y%m%d')}-{str(last_number + 1).zfill(3)}"
        
        # Set initial values for forms
        sales_order_form.initial = {
            'order_number': order_number,
            'order_date': today,
            'delivery_date': today + timedelta(days=7),  # Add default delivery date
        }
        
        invoice_form.initial = {
            'invoice_number': invoice_number,
            'invoice_date': today,
            'due_date': today + timedelta(days=30),  # Default: 30 days payment term
            'payment_terms': 'Net 30 days',
        }
        
        # Get all product variants for AJAX
        product_variants = ProductVariant.objects.all()
        products_data = [{
            'id': variant.id,
            'name': variant.name,
            'price': float(variant.selling_price)
        } for variant in product_variants]
        
        # Get all customers for AJAX
        customers = Customer.objects.all()
        customers_data = [{
            'id': customer.id,
            'name': customer.name,
            'address': customer.address,
            'payment_terms': customer.payment_terms or 'Net 30 days'
        } for customer in customers]

        context = {
            'customer_form': customer_form,
            'sales_order_form': sales_order_form,
            'sales_order_item_formset': sales_order_item_formset,
            'invoice_form': invoice_form,
            'products_data': products_data,
            'customers_data': customers_data,
        }
        return render(request, self.template_name, context)
    
    @transaction.atomic
    def post(self, request):
        # Debug print to see what's in the POST data
        print("POST data:", request.POST)
        
        # Initialize forms with POST data
        customer_form = CustomerForm(request.POST, prefix='customer')
        sales_order_form = SalesOrderForm(request.POST, prefix='order')
        invoice_form = InvoiceForm(request.POST, prefix='invoice')
        
        # Handle customer selection or creation
        customer = None
        using_existing_customer = 'customer_select' in request.POST and request.POST['customer_select']
        
        # Debug
        print(f"Using existing customer: {using_existing_customer}")
        if using_existing_customer:
            print(f"Selected customer ID: {request.POST['customer_select']}")
        
        if using_existing_customer:
            # Use existing customer
            try:
                customer = Customer.objects.get(id=request.POST['customer_select'])
                is_customer_valid = True  # Skip customer form validation
                print(f"Found customer: {customer.name}")
            except Customer.DoesNotExist:
                messages.error(request, "Selected customer not found")
                is_customer_valid = False
                print("Customer not found")
        else:
            # Create new customer
            is_customer_valid = customer_form.is_valid()
            if is_customer_valid:
                customer = customer_form.save(commit=False)
                # Make sure required fields are filled
                if not (customer.name and customer.address):
                    messages.error(request, "Customer name and address are required")
                    is_customer_valid = False
                else:
                    customer.save()
                    print(f"Created new customer: {customer.name}")
            else:
                print("Customer form invalid:", customer_form.errors)
        
        # Validate order form and debug any errors
        is_order_valid = sales_order_form.is_valid()
        if not is_order_valid:
            print("Order form invalid:", sales_order_form.errors)
        
        # Validate invoice form and debug any errors
        is_invoice_valid = invoice_form.is_valid()
        if not is_invoice_valid:
            print("Invoice form invalid:", invoice_form.errors)
            
        # Initialize items formset
        sales_order_item_formset = SalesOrderItemFormSet(request.POST, prefix='items')
        is_items_valid = sales_order_item_formset.is_valid()
        if not is_items_valid:
            print("Items formset invalid:", sales_order_item_formset.errors)
            
        # Validate that at least one item is present and has a quantity
        has_valid_items = False
        for form in sales_order_item_formset.forms:
            if form.is_valid() and form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                product_variant = form.cleaned_data.get('product_variant')
                quantity = form.cleaned_data.get('quantity', 0)
                if product_variant and quantity > 0:
                    has_valid_items = True
                    break
        
        if not has_valid_items:
            is_items_valid = False
            messages.error(request, "At least one item with a valid product and quantity is required")
            print("No valid items found in formset")
        
        # Calculate total from items
        total_amount = 0
        if is_items_valid:
            for form in sales_order_item_formset.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    quantity = form.cleaned_data.get('quantity', 0)
                    unit_price = form.cleaned_data.get('unit_price', 0)
                    discount = form.cleaned_data.get('discount', 0)
                    
                    item_total = quantity * unit_price * (1 - discount/100)
                    total_amount += item_total
                    print(f"Item total: {item_total}, Running total: {total_amount}")
        
        # If all forms are valid, save everything
        print(f"Validation status - Customer: {is_customer_valid}, Order: {is_order_valid}, Items: {is_items_valid}, Invoice: {is_invoice_valid}")
        
        if is_customer_valid and is_order_valid and is_items_valid and is_invoice_valid:
            # Save the order first
            sales_order = sales_order_form.save(commit=False)
            sales_order.customer = customer
            sales_order.status = 'new'
            sales_order.payment_status = 'pending'
            sales_order.total_amount = total_amount
            sales_order.save()
            print(f"Sales order saved with ID: {sales_order.id}")
            
            # Save items with subtotals
            items = sales_order_item_formset.save(commit=False)
            for item in items:
                item.sales_order = sales_order  # Important: link to sales order
                item.subtotal = item.quantity * item.unit_price * (1 - item.discount/100)
                item.save()
                print(f"Item saved: {item.product_variant.name}, qty: {item.quantity}")
            
            # Handle deleted items
            for obj in sales_order_item_formset.deleted_objects:
                obj.delete()
                print(f"Deleted item: {obj.product_variant.name}")
            
            # Create invoice with the sales order
            invoice = invoice_form.save(commit=False)
            invoice.sales_order = sales_order
            invoice.status = 'unpaid'
            invoice.total_amount = total_amount
            invoice.save()
            print(f"Invoice saved with number: {invoice.invoice_number}")
            
            messages.success(request, "Sale recorded successfully!")
            return redirect('sales_order_detail', pk=sales_order.pk)
        
        # If any form is invalid, show errors and repopulate the form
        product_variants = ProductVariant.objects.all()
        products_data = [{
            'id': variant.id,
            'name': variant.name,
            'price': float(variant.selling_price)
        } for variant in product_variants]
        
        customers = Customer.objects.all()
        customers_data = [{
            'id': customer.id,
            'name': customer.name,
            'address': customer.address,
            'payment_terms': customer.payment_terms or 'Net 30 days'
        } for customer in customers]
        
        context = {
            'customer_form': customer_form,
            'sales_order_form': sales_order_form,
            'sales_order_item_formset': sales_order_item_formset,
            'invoice_form': invoice_form,
            'products_data': products_data,
            'customers_data': customers_data,
        }
        
        if not is_customer_valid:
            if using_existing_customer:
                messages.error(request, "Selected customer not found or invalid")
            else:
                messages.error(request, "Please correct customer information")
        if not is_order_valid:
            messages.error(request, "Please correct order information")
        if not is_items_valid:
            messages.error(request, "Please check item details (all products must have quantities)")
        if not is_invoice_valid:
            messages.error(request, "Please correct invoice information")
            
        return render(request, self.template_name, context)
    


def sales_order_detail(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    items = order.items.all()  # Changed from salesorderitem_set to items
    invoice = getattr(order, 'invoice', None)
    
    context = {
        'order': order,
        'items': items,
        'invoice': invoice,
        'title': f'Sales Order #{order.order_number}'
    }
    return render(request, 'sales/salesorder_detail.html', context)



from django.core.paginator import Paginator
from django.shortcuts import render
from .models import SalesOrder
from django.db.models import Q

def sales_order_list(request):
    # Get search parameters from request
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    customer_filter = request.GET.get('customer', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Start with all orders
    orders = SalesOrder.objects.select_related('customer', 'sales_representative').all()
    
    # Apply filters
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(sales_representative__user__first_name__icontains=search_query) |
            Q(sales_representative__user__last_name__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    if customer_filter:
        orders = orders.filter(customer_id=customer_filter)
        
    if date_from:
        orders = orders.filter(order_date__gte=date_from)
        
    if date_to:
        orders = orders.filter(order_date__lte=date_to)
    
    # Order by most recent first
    orders = orders.order_by('-order_date')
    
    # Pagination
    paginator = Paginator(orders, 25)  # Show 25 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'customer_filter': customer_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': SalesOrder.STATUS_CHOICES,
        'customers': Customer.objects.filter(status='active').order_by('name'),
    }
    
    return render(request, 'sales/sales_order_list.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SalesOrder, Customer, ProductVariant
from .forms import SalesOrderForm, SalesOrderItemFormSet

def sales_order_update(request, pk):
    order = get_object_or_404(SalesOrder.objects.prefetch_related('items'), pk=pk)
    
    if request.method == 'POST':
        order_form = SalesOrderForm(request.POST, instance=order, prefix='order')
        item_formset = SalesOrderItemFormSet(request.POST, instance=order, prefix='items')
        
        if order_form.is_valid() and item_formset.is_valid():
            try:
                order = order_form.save()
                items = item_formset.save()
                
                # Delete any items marked for deletion
                for item in item_formset.deleted_objects:
                    item.delete()
                
                # Recalculate order total
                order.total_amount = sum(item.subtotal for item in order.items.all())
                order.save()
                
                messages.success(request, f'Sales order {order.order_number} has been updated successfully!')
                return redirect('sales_order_detail', pk=order.pk)
            
            except Exception as e:
                messages.error(request, f'Error updating order: {str(e)}')
    else:
        order_form = SalesOrderForm(instance=order, prefix='order')
        item_formset = SalesOrderItemFormSet(instance=order, prefix='items')
    
    context = {
        'order_form': order_form,
        'item_formset': item_formset,
        'order': order,
        'title': f'Update Order #{order.order_number}',
        'customers': Customer.objects.filter(status='active').order_by('name'),
        'products': ProductVariant.objects.filter(status='active').select_related('product'),
    }
    
    return render(request, 'sales/sales_order_form.html', context)



from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SalesOrder

class SalesOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = SalesOrder
    template_name = 'sales/sales_order_confirm_delete.html'
    context_object_name = 'order'
    
    def get_success_url(self):
        messages.success(self.request, f"Sales order {self.object.order_number} has been deleted successfully.")
        return reverse('sales_order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Order #{self.object.order_number}"
        return context
    


from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from .models import SalesOrder, Invoice
from .forms import InvoiceForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'sales/invoice_create.html'

    def get_initial(self):
        order = get_object_or_404(SalesOrder, pk=self.kwargs['pk'])
        return {
            'sales_order': order,
            'invoice_number': f"INV-{order.order_number}",
            'invoice_date': order.order_date,
            'due_date': order.order_date + timedelta(days=30),
            'payment_terms': order.customer.payment_terms or 'Net 30 days',
            'total_amount': order.total_amount
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(SalesOrder, pk=self.kwargs['pk'])
        context['order'] = order
        context['title'] = f"Create Invoice for Order #{order.order_number}"
        return context

    def form_valid(self, form):
        order = get_object_or_404(SalesOrder, pk=self.kwargs['pk'])
        form.instance.sales_order = order
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Update order payment status if needed
        if form.cleaned_data['status'] == 'paid':
            order.payment_status = 'paid'
            order.save()
        
        messages.success(self.request, f"Invoice {form.instance.invoice_number} created successfully!")
        return response

    def get_success_url(self):
        return reverse('sales_order_detail', kwargs={'pk': self.kwargs['pk']})
    


from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import Invoice, Customer
from django.utils import timezone

def invoice_list(request):
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    customer_filter = request.GET.get('customer', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    overdue = request.GET.get('overdue', '')
    
    # Start with all invoices
    invoices = Invoice.objects.select_related(
        'sales_order', 
        'sales_order__customer',
        'sales_order__sales_representative__user'
    ).order_by('-invoice_date')
    
    # Apply filters
    if search_query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search_query) |
            Q(sales_order__order_number__icontains=search_query) |
            Q(sales_order__customer__name__icontains=search_query)
        )
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
        
    if customer_filter:
        invoices = invoices.filter(sales_order__customer_id=customer_filter)
        
    if date_from:
        invoices = invoices.filter(invoice_date__gte=date_from)
        
    if date_to:
        invoices = invoices.filter(invoice_date__lte=date_to)
        
    if overdue:
        today = timezone.now().date()
        invoices = invoices.filter(status__in=['unpaid', 'partial'], due_date__lt=today)
    
    # Pagination
    paginator = Paginator(invoices, 25)  # Show 25 invoices per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'customer_filter': customer_filter,
        'date_from': date_from,
        'date_to': date_to,
        'overdue': overdue,
        'status_choices': Invoice.STATUS_CHOICES,
        'customers': Customer.objects.filter(status='active').order_by('name'),
        'today': timezone.now().date(),
    }
    
    return render(request, 'sales/invoice_list.html', context)
from django.shortcuts import render
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, FloatField, DecimalField
from django.utils import timezone
from datetime import timedelta
from .models import SalesOrder, SalesOrderItem, Customer, ProductVariant, Invoice
import calendar

def sales_dashboard(request):
    today = timezone.now().date()
    twelve_months_ago = today - timedelta(days=365)
    six_months_ago = today - timedelta(days=180)

    # 1. Revenue Trend
    monthly_revenue = []
    month_labels = []

    for i in range(12):
        month = today.month - i
        year = today.year
        if month < 1:
            month += 12
            year -= 1

        start_date = today.replace(year=year, month=month, day=1)
        if month == 12:
            end_date = start_date.replace(year=year+1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=month+1, day=1) - timedelta(days=1)

        revenue = Invoice.objects.filter(
            invoice_date__range=(start_date, end_date)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        monthly_revenue.insert(0, float(revenue))
        month_labels.insert(0, f"{calendar.month_abbr[month]} {year}")

    total_revenue = sum(monthly_revenue)
    average_monthly_revenue = round(total_revenue / 12, 2) if monthly_revenue else 0
    max_monthly_revenue = max(monthly_revenue) if monthly_revenue else 0

    # 2. Top Products
    top_products_qs = SalesOrderItem.objects.filter(
        sales_order__order_date__gte=twelve_months_ago
    ).values(
        'product_variant__name',
        'product_variant__size',
        'product_variant__packaging_type'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=ExpressionWrapper(
            Sum(F('quantity') * F('unit_price') * (1.0 - F('discount') / 100.0)),
            output_field=FloatField()
        )
    ).order_by('-total_revenue')[:10]

    top_products = list(top_products_qs)

    top_product_labels = [
        f"{item['product_variant__name']} ({item['product_variant__size']}, {item['product_variant__packaging_type']})"
        for item in top_products
    ]

    # 3. Product Performance
    performance_months = []
    product_performance = {}
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        if month < 1:
            month += 12
            year -= 1
        performance_months.append(calendar.month_abbr[month])

    top_5_products = SalesOrderItem.objects.filter(
        sales_order__order_date__gte=six_months_ago
    ).values('product_variant__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    for product in top_5_products:
        name = product['product_variant__name']
        product_performance[name] = []

        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            if month < 1:
                month += 12
                year -= 1

            start_date = today.replace(year=year, month=month, day=1)
            if month == 12:
                end_date = start_date.replace(year=year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=month+1, day=1) - timedelta(days=1)

            sold = SalesOrderItem.objects.filter(
                product_variant__name=name,
                sales_order__order_date__range=(start_date, end_date)
            ).aggregate(total=Sum('quantity'))['total'] or 0

            product_performance[name].append(float(sold))

    # 4. Top Customers
    top_customers_qs = Customer.objects.filter(
        sales_orders__order_date__gte=twelve_months_ago
    ).annotate(
        total_spent=Sum('sales_orders__total_amount'),
        order_count=Count('sales_orders')
    ).order_by('-total_spent')[:11]

    top_customers = list(top_customers_qs)

    # 5. Analysis Tables
    recent_orders = SalesOrder.objects.select_related('customer').order_by('-order_date')[:10]
    overdue_invoices = Invoice.objects.filter(
        status__in=['unpaid', 'partial'],
        due_date__lt=today
    ).select_related('sales_order__customer').order_by('due_date')[:10]

    product_variant_performance = ProductVariant.objects.filter(
        status='active'
    ).annotate(
        total_sold=Sum('salesorderitem__quantity'),
        total_revenue=ExpressionWrapper(
            Sum(F('salesorderitem__quantity') * F('salesorderitem__unit_price') * (1.0 - F('salesorderitem__discount') / 100.0)),
            output_field=FloatField()
        )
    ).order_by('-total_revenue')

    # Fix for division error - ensure operands are the same type and specify output field
    if recent_orders:
        avg_revenue_per_order = round(float(total_revenue) / len(recent_orders), 2)
    else:
        avg_revenue_per_order = 0

    # Sample Chart Colors (add more if needed)
    chart_colors = [
        "#F40009", "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0",
        "#9966FF", "#FF9F40", "#C9CBCF", "#3D9970", "#B10DC9"
    ]

    context = {
        'monthly_revenue': monthly_revenue,
        'month_labels': month_labels,
        'top_products': top_products,
        'top_product_labels': top_product_labels,
        'product_performance': product_performance,
        'performance_months': performance_months,
        'top_customers': top_customers,
        'total_revenue': total_revenue,
        'average_monthly_revenue': average_monthly_revenue,
        'max_monthly_revenue': max_monthly_revenue,
        'avg_revenue_per_order': avg_revenue_per_order,
        'recent_orders': recent_orders,
        'overdue_invoices': overdue_invoices,
        'product_variant_performance': product_variant_performance,
        'chart_colors': chart_colors,
        'today': today,
    }

    return render(request, 'sales/dashboard.html', context)

# Add to your imports
import json
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from .models import VisitLog, Attendance, SecurityGuard, VehicleLog
import calendar
from collections import defaultdict

def security_guard_dashboard(request):
    # Check if user is authenticated and is a security guard
    if not request.user.is_authenticated or request.user.user_type != 'security':
        return render(request, 'security/unauthorized.html')
    
    # Get the current security guard
    security_guard = request.user
    
    # Today's date
    today = timezone.now().date()
    
    # Starting date for visitor statistics (12 months ago)
    twelve_months_ago = today - relativedelta(months=11, day=1)  # Start from the 1st of the month, 11 months ago
    
    # Get all visit logs from the last 12 months
    all_visits = VisitLog.objects.filter(
        check_in_time__gte=twelve_months_ago
    ).order_by('check_in_time')
    
    # Manually aggregate by month (SQLite compatible)
    month_data = defaultdict(lambda: {
        'total_visits': 0,
        'checked_out': 0,
        'still_inside': 0
    })
    
    for visit in all_visits:
        # Extract year and month for grouping
        year_month = visit.check_in_time.strftime('%Y-%m')
        
        # Increment counters
        month_data[year_month]['total_visits'] += 1
        
        if visit.check_out_time is not None:
            month_data[year_month]['checked_out'] += 1
        else:
            month_data[year_month]['still_inside'] += 1
    
    # Prepare data for charts
    months = []
    visit_counts = []
    checked_out_counts = []
    
    # Generate complete 12-month data, including the current month
    current_date = twelve_months_ago
    end_date = today
    
    while current_date <= end_date:
        month_key = current_date.strftime('%Y-%m')
        month_name = calendar.month_name[current_date.month] + ' ' + str(current_date.year)
        
        months.append(month_name)
        visit_counts.append(month_data[month_key]['total_visits'])
        checked_out_counts.append(month_data[month_key]['checked_out'])
        
        # Move to the next month
        current_date = current_date + relativedelta(months=1)
    
    # Today's visitors
    todays_visits = VisitLog.objects.filter(
        check_in_time__date=today
    )
    
    # Visitors currently inside
    visitors_inside = VisitLog.objects.filter(
        is_inside=True
    ).count()
    
    # Vehicle statistics
    todays_vehicles = VehicleLog.objects.filter(
        entry_time__date=today
    )
    vehicles_inside = VehicleLog.objects.filter(
        is_inside=True
    ).count()
    
    # Attendance statistics
    todays_attendance = Attendance.objects.filter(date=today)
    signed_in = todays_attendance.filter(check_in_time__isnull=False).count()
    signed_out = todays_attendance.filter(check_out_time__isnull=False).count()
    signed_in_not_out = todays_attendance.filter(
        check_in_time__isnull=False,
        check_out_time__isnull=True
    ).count()
    
    context = {
        'security_guard': security_guard,
        'today': today,
        
        # Visitor statistics
        'total_visitors_last_12_months': sum(visit_counts),
        'visitors_today': todays_visits.count(),
        'visitors_inside': visitors_inside,
        
        # Vehicle statistics
        'vehicles_today': todays_vehicles.count(),
        'vehicles_inside': vehicles_inside,
        
        # Attendance statistics
        'employees_signed_in': signed_in,
        'employees_signed_out': signed_out,
        'employees_signed_in_not_out': signed_in_not_out,
        'total_employees': todays_attendance.count(),

        # Chart data - properly serialize for JavaScript
        'months_json': json.dumps(months),
        'visit_counts_json': json.dumps(visit_counts),
        'checked_out_counts_json': json.dumps(checked_out_counts),
        
        # Chart data
        'months': months,
        'visit_counts': visit_counts,
        'checked_out_counts': checked_out_counts,
        
        # Recent logs
        'recent_visits': todays_visits.order_by('-check_in_time')[:5],
        'recent_vehicles': todays_vehicles.order_by('-entry_time')[:5],
    }
    
    return render(request, 'security/dashboard.html', context)




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import VisitorCheckInForm, VisitorCheckOutForm
from .models import Visitor, VisitLog, SecurityGuard

@login_required
def visitor_check_in(request):
    if request.method == 'POST':
        form = VisitorCheckInForm(request.POST)
        if form.is_valid():
            visitor = form.save()
            
            # Create visit log
            visit = VisitLog.objects.create(
                visitor=visitor,
                purpose=form.cleaned_data['purpose'],
                department=form.cleaned_data['department'],
                security_guard=request.user.securityguard,
                badge_issued=True,
                badge_number=f"CC-{timezone.now().strftime('%Y%m%d')}-{visitor.id}"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'badge_number': visit.badge_number,
                    'visitor_name': f"{visitor.first_name} {visitor.last_name}",
                    'check_in_time': visit.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            return redirect('visitor_check_in_success')
    else:
        form = VisitorCheckInForm()
    
    return render(request, 'visitors/check_in.html', {'form': form})

@login_required
def visitor_check_out(request):
    if request.method == 'POST':
        form = VisitorCheckOutForm(request.POST)
        
        if form.is_valid():
            id_number = form.cleaned_data['id_number']
            
            try:
                # Try to find visitor by ID number
                visitor = Visitor.objects.get(id_number=id_number)
                visit = VisitLog.objects.filter(
                    visitor=visitor, 
                    check_out_time__isnull=True
                ).latest('check_in_time')
                
                visit.check_out_time = timezone.now()
                visit.is_inside = False
                visit.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'visitor_name': f"{visitor.first_name} {visitor.last_name}",
                        'check_in_time': visit.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'check_out_time': visit.check_out_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                return redirect('visitor_check_out_success')
                
            except Visitor.DoesNotExist:
                # If visitor not found by ID number, try using the value as primary key
                try:
                    visitor = Visitor.objects.get(pk=id_number)
                    visit = VisitLog.objects.filter(
                        visitor=visitor, 
                        check_out_time__isnull=True
                    ).latest('check_in_time')
                    
                    visit.check_out_time = timezone.now()
                    visit.is_inside = False
                    visit.save()
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'visitor_name': f"{visitor.first_name} {visitor.last_name}",
                            'check_in_time': visit.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'check_out_time': visit.check_out_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    return redirect('visitor_check_out_success')
                    
                except (Visitor.DoesNotExist, VisitLog.DoesNotExist):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': 'No active visit found with this ID'
                        }, status=404)
                    form.add_error('id_number', 'No active visit found with this ID number')
        
        # Handle form errors for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Invalid form data',
                'errors': dict(form.errors.items())
            }, status=400)
    
    # For GET requests or regular form submissions
    form = VisitorCheckOutForm()
    return render(request, 'visitors/check_out.html', {'form': form})

def find_visitor(request):
    if request.method == 'GET' and 'id_number' in request.GET:
        id_number = request.GET['id_number']
        try:
            visitor = Visitor.objects.get(id_number=id_number)
            active_visit = VisitLog.objects.filter(
                visitor=visitor,
                check_out_time__isnull=True
            ).latest('check_in_time')
            
            return JsonResponse({
                'found': True,
                'visitor_name': f"{visitor.first_name} {visitor.last_name}",
                'company': visitor.company,
                'check_in_time': active_visit.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'badge_number': active_visit.badge_number
            })
        except (Visitor.DoesNotExist, VisitLog.DoesNotExist):
            return JsonResponse({'found': False})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def check_in_success(request):
    """Display success page after visitor check-in"""
    context = {
        'title': 'Check-In Successful',
        'icon': 'fas fa-check-circle',
        'heading': 'Visitor Checked In Successfully',
        'message': 'The visitor has been successfully registered in the system.',
        'action_text': 'Check In Another Visitor',
        'action_url': 'visitor_check_in',
        'badge_info': request.session.pop('badge_info', None)  # Optional: if you want to show badge info
    }
    return render(request, 'visitors/success_page.html', context)

@login_required
def check_out_success(request):
    """Display success page after visitor check-out"""
    context = {
        'title': 'Check-Out Successful',
        'icon': 'fas fa-check-circle',
        'heading': 'Visitor Checked Out Successfully',
        'message': 'The visitor has been successfully checked out of the system.',
        'action_text': 'Check Out Another Visitor',
        'action_url': 'visitor_check_out',
        'badge_return_message': True  # Flag to show badge return reminder
    }
    return render(request, 'visitors/success_page.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def check_in_success(request):
    """Display success page after visitor check-in"""
    context = {
        'title': 'Check-In Successful',
        'icon': 'fas fa-check-circle',
        'heading': 'Visitor Checked In Successfully',
        'message': 'The visitor has been successfully registered in the system.',
        'action_text': 'Check In Another Visitor',
        'action_url': 'visitor_check_in',
        'badge_info': request.session.pop('badge_info', None)  # Optional: if you want to show badge info
    }
    return render(request, 'visitors/success_page.html', context)

@login_required
def check_out_success(request):
    """Display success page after visitor check-out"""
    context = {
        'title': 'Check-Out Successful',
        'icon': 'fas fa-check-circle',
        'heading': 'Visitor Checked Out Successfully',
        'message': 'The visitor has been successfully checked out of the system.',
        'action_text': 'Check Out Another Visitor',
        'action_url': 'visitor_check_out',
        'badge_return_message': True  # Flag to show badge return reminder
    }
    return render(request, 'visitors/success_page.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .models import Vehicle, VehicleLog, SecurityGuard
from .models import Visitor
from django.utils import timezone

User = get_user_model()

@login_required
def vehicle_management(request):
    # Get security guard instance for the current user
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        security_guard = None
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'check_in':
            return handle_vehicle_checkin(request, security_guard)
        elif action == 'check_out':
            return handle_vehicle_checkout(request, security_guard)
    
    # Get active vehicle logs and recent activity
    active_vehicle_logs = VehicleLog.objects.filter(is_inside=True).order_by('-entry_time')[:20]
    recent_vehicle_logs = VehicleLog.objects.all().order_by('-entry_time')[:10]
    
    # Get lists for owner selection
    employees = User.objects.filter(is_active=True).order_by('last_name')
    visitors = Visitor.objects.order_by('last_name')
    
    context = {
        'active_vehicle_logs': active_vehicle_logs,
        'recent_vehicle_logs': recent_vehicle_logs,
        'employees': employees,
        'visitors': visitors,
    }
    return render(request, 'security/vehicle_management.html', context)

def handle_vehicle_checkin(request, security_guard):
    license_plate = request.POST.get('license_plate', '').strip().upper()
    vehicle_type = request.POST.get('vehicle_type')
    make = request.POST.get('make', '').strip()
    model = request.POST.get('model', '').strip()
    color = request.POST.get('color', '').strip()
    purpose = request.POST.get('purpose', '').strip()
    owner_type = request.POST.get('owner_type')
    
    # Validate required fields
    if not license_plate or not vehicle_type or not owner_type:
        return JsonResponse({'success': False, 'error': 'Required fields are missing'})
    
    try:
        # Get or create the vehicle
        vehicle, created = Vehicle.objects.get_or_create(
            license_plate=license_plate,
            defaults={
                'make': make,
                'model': model,
                'color': color,
                'vehicle_type': vehicle_type,
            }
        )
        
        # Update owner based on owner type
        if owner_type == 'employee':
            employee_id = request.POST.get('employee_owner')
            if employee_id:
                employee = User.objects.get(id=employee_id)
                vehicle.owner = employee
                vehicle.visitor_owner = None
        elif owner_type == 'visitor':
            visitor_id = request.POST.get('visitor_owner')
            if visitor_id:
                visitor = Visitor.objects.get(id=visitor_id)
                vehicle.visitor_owner = visitor
                vehicle.owner = None
        
        # Update vehicle details if they were provided
        if make:
            vehicle.make = make
        if model:
            vehicle.model = model
        if color:
            vehicle.color = color
        if vehicle_type:
            vehicle.vehicle_type = vehicle_type
        
        vehicle.save()
        
        # Create vehicle log entry
        VehicleLog.objects.create(
            vehicle=vehicle,
            security_guard=security_guard,
            purpose=purpose,
            is_inside=True
        )
        
        return JsonResponse({
            'success': True,
            'license_plate': vehicle.license_plate,
            'vehicle_type': vehicle.get_vehicle_type_display(),
            'entry_time': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def handle_vehicle_checkout(request, security_guard):
    license_plate = request.POST.get('license_plate', '').strip().upper()
    
    if not license_plate:
        return JsonResponse({'success': False, 'error': 'License plate is required'})
    
    try:
        # Get the active vehicle log
        vehicle_log = VehicleLog.objects.filter(
            vehicle__license_plate=license_plate,
            is_inside=True
        ).latest('entry_time')
        
        # Update the log with checkout info
        vehicle_log.exit_time = timezone.now()
        vehicle_log.is_inside = False
        vehicle_log.save()
        
        return JsonResponse({
            'success': True,
            'license_plate': vehicle_log.vehicle.license_plate,
            'vehicle_type': vehicle_log.vehicle.get_vehicle_type_display(),
            'exit_time': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    except VehicleLog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No active vehicle found with that license plate'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(['GET'])
def get_vehicle_details(request):
    license_plate = request.GET.get('license_plate', '').strip().upper()
    
    if not license_plate:
        return JsonResponse({'exists': False, 'error': 'License plate is required'})
    
    try:
        # Get the active vehicle log
        vehicle_log = VehicleLog.objects.filter(
            vehicle__license_plate=license_plate,
            is_inside=True
        ).latest('entry_time')
        
        vehicle = vehicle_log.vehicle
        owner = ''
        
        if vehicle.owner:
            owner = f"{vehicle.owner.get_full_name()} (Employee)"
        elif vehicle.visitor_owner:
            owner = f"{vehicle.visitor_owner.first_name} {vehicle.visitor_owner.last_name} (Visitor)"
        
        return JsonResponse({
            'exists': True,
            'license_plate': vehicle.license_plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'color': vehicle.color,
            'vehicle_type': vehicle.get_vehicle_type_display(),
            'owner': owner,
            'entry_time': timezone.localtime(vehicle_log.entry_time).strftime('%Y-%m-%d %H:%M:%S'),
            'purpose': vehicle_log.purpose or '',
        })
    
    except VehicleLog.DoesNotExist:
        return JsonResponse({'exists': False, 'error': 'No active vehicle found with that license plate'})
    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)})
    


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Attendance, Employee, SecurityGuard
from django.contrib import messages

@login_required
def employee_attendance(request):
    # Get security guard instance for the current user
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        security_guard = None
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'check_in':
            return handle_employee_checkin(request, security_guard)
        elif action == 'check_out':
            return handle_employee_checkout(request, security_guard)
    
    # Get today's attendance records
    today = timezone.localdate()
    todays_attendance = Attendance.objects.filter(date=today).select_related('employee').order_by('-check_in_time')[:20]
    recent_attendance = Attendance.objects.all().select_related('employee').order_by('-date', '-check_in_time')[:10]
    
    # Get active employees for dropdown
    active_employees = Employee.objects.order_by('user__last_name')
    
    context = {
        'todays_attendance': todays_attendance,
        'recent_attendance': recent_attendance,
        'active_employees': active_employees,
    }
    return render(request, 'security/employee_attendance.html', context)


"""
This implementation includes:
1. A new Django view function to handle AJAX employee search
2. HTML changes to replace dropdown with search input
3. JavaScript to implement the search functionality
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Employee  # Adjust import as needed


# Enhanced employee search view with additional details
@login_required
@require_http_methods(['GET'])
def search_employees(request):
    search_term = request.GET.get('term', '').strip()
    
    if not search_term:
        return JsonResponse({'results': []})
    
    # Search by working_id, first name, or last name
    employees = Employee.objects.filter(
        Q(working_id__icontains=search_term) | 
        Q(first_name__icontains=search_term) |
        Q(last_name__icontains=search_term)
    ).select_related('user', 'department')[:10]

    results = []
    for employee in employees:
        # Get full name from user if available, otherwise use employee fields
        user = getattr(employee, 'user', None)
        if user:
            full_name = user.get_full_name() or f"{employee.first_name} {employee.last_name}"
        else:
            full_name = f"{employee.first_name} {employee.last_name}"

        # Get department name if available
        department_name = employee.department.name if employee.department else 'N/A'
        
        # Get role display name if available
        role_display = dict(Employee.ROLE_CHOICES).get(employee.role, 'N/A') if employee.role else 'N/A'
        
        # Build result with additional details
        results.append({
            'id': employee.id,
            'name': full_name,
            'department': department_name,
            'phone_number': employee.phone_number or 'N/A',
            'email': employee.email or 'N/A',
            'role': role_display,
            'working_id': employee.working_id or 'N/A'
        })
    
    return JsonResponse({'results': results})



def handle_employee_checkin(request, security_guard):
    employee_id = request.POST.get('employee')
    status = request.POST.get('status', 'present')
    
    if not employee_id:
        return JsonResponse({'success': False, 'error': 'Employee selection is required'})
    
    try:
        employee = Employee.objects.get(id=employee_id)
        today = timezone.localdate()
        now = timezone.localtime()
        
        # Create or update attendance record
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in_time': now.time(),
                'status': status,
            }
        )
        
        # If record exists but check-in time is empty (manual status update)
        if not created and not attendance.check_in_time:
            attendance.check_in_time = now.time()
            attendance.status = status
            attendance.save()
        
        return JsonResponse({
            'success': True,
            'employee_name': employee.user.get_full_name(),
            'check_in_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'status': attendance.get_status_display(),
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def handle_employee_checkout(request, security_guard):
    employee_id = request.POST.get('employee')
    
    if not employee_id:
        return JsonResponse({'success': False, 'error': 'Employee selection is required'})
    
    try:
        employee = Employee.objects.get(id=employee_id)
        today = timezone.localdate()
        now = timezone.localtime()
        
        # Get today's attendance record
        attendance = Attendance.objects.get(
            employee=employee,
            date=today
        )
        
        # Update checkout time
        attendance.check_out_time = now.time()
        
        # Update status to half_day if check-out is before 1 PM (example logic)
        if now.hour < 13 and attendance.status == 'present':
            attendance.status = 'half_day'
        
        attendance.save()
        
        return JsonResponse({
            'success': True,
            'employee_name': employee.user.get_full_name(),
            'check_out_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'status': attendance.get_status_display(),
        })
    
    except Attendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No check-in record found for today'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(['GET'])
def get_employee_attendance(request):
    employee_id = request.GET.get('employee')
    date = request.GET.get('date', timezone.localdate().isoformat())
    
    if not employee_id:
        return JsonResponse({'exists': False, 'error': 'Employee ID is required'})
    
    try:
        employee = Employee.objects.get(id=employee_id)
        
        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=date
            )
            
            return JsonResponse({
                'exists': True,
                'employee_name': employee.user.get_full_name(),
                'check_in_time': attendance.check_in_time.strftime('%H:%M:%S') if attendance.check_in_time else None,
                'check_out_time': attendance.check_out_time.strftime('%H:%M:%S') if attendance.check_out_time else None,
                'status': attendance.get_status_display(),
            })
        
        except Attendance.DoesNotExist:
            return JsonResponse({'exists': False})
    
    except Employee.DoesNotExist:
        return JsonResponse({'exists': False, 'error': 'Employee not found'})
    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)})
    


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import Visitor
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, OuterRef, Subquery, BooleanField
from django.db.models.functions import Coalesce
from .models import Visitor, VisitLog

@login_required
def visitor_management(request):
    # Create a subquery to get the latest visit log for each visitor
    latest_visit = VisitLog.objects.filter(
        visitor=OuterRef('pk')
    ).order_by('-check_in_time')
    
    # Annotate visitors with their latest visit status
    visitors_list = Visitor.objects.annotate(
        latest_visit_id=Subquery(latest_visit.values('id')[:1]),
        latest_check_in=Subquery(latest_visit.values('check_in_time')[:1]),
        latest_check_out=Subquery(latest_visit.values('check_out_time')[:1]),
        is_inside=Subquery(latest_visit.values('is_inside')[:1]),
        badge_number=Subquery(latest_visit.values('badge_number')[:1]),
    ).order_by('-id')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        visitors_list = visitors_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(id_number__icontains=search_query)
        )
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter == 'inside':
        visitors_list = visitors_list.filter(is_inside=True)
    elif status_filter == 'outside':
        visitors_list = visitors_list.filter(is_inside=False)
    
    # Pagination
    paginator = Paginator(visitors_list, 10)  # Show 10 visitors per page
    page_number = request.GET.get('page')
    visitors = paginator.get_page(page_number)
    
    context = {
        'visitors': visitors,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'security/visitor_management.html', context)

@login_required
@require_http_methods(['GET'])
def get_visitor_details(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    data = {
        'id': visitor.id,
        'first_name': visitor.first_name,
        'last_name': visitor.last_name,
        'company': visitor.company,
        'email': visitor.email,
        'phone': visitor.phone,
        'visitor_type': visitor.visitor_type,
        'visitor_type_display': visitor.get_visitor_type_display(),
        'id_number': visitor.id_number,
        'id_type': visitor.id_type,
    }
    return JsonResponse(data)

@login_required
@require_http_methods(['POST'])
def update_visitor(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    try:
        visitor.first_name = request.POST.get('first_name', visitor.first_name)
        visitor.last_name = request.POST.get('last_name', visitor.last_name)
        visitor.company = request.POST.get('company', visitor.company)
        visitor.email = request.POST.get('email', visitor.email)
        visitor.phone = request.POST.get('phone', visitor.phone)
        visitor.visitor_type = request.POST.get('visitor_type', visitor.visitor_type)
        visitor.id_number = request.POST.get('id_number', visitor.id_number)
        visitor.id_type = request.POST.get('id_type', visitor.id_type)
        visitor.save()
        
        return JsonResponse({'success': True, 'message': 'Visitor updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(['POST'])
def delete_visitor(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    
    try:
        visitor.delete()
        return JsonResponse({'success': True, 'message': 'Visitor deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def emergency_protocols(request):
    return render(request, 'security/emergency_protocols.html')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Vehicle, VehicleLog, SecurityGuard

@login_required
def vehicle_record_management(request):
    # Create a subquery to get the latest log for each vehicle
    latest_log = VehicleLog.objects.filter(
        vehicle=OuterRef('pk')
    ).order_by('-entry_time')
    
    # Annotate vehicles with their latest log status
    vehicles_list = Vehicle.objects.annotate(
        latest_log_id=Subquery(latest_log.values('id')[:1]),
        latest_entry=Subquery(latest_log.values('entry_time')[:1]),
        latest_exit=Subquery(latest_log.values('exit_time')[:1]),
        is_inside=Subquery(latest_log.values('is_inside')[:1]),
        purpose=Subquery(latest_log.values('purpose')[:1]),
    ).order_by('-latest_entry')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        vehicles_list = vehicles_list.filter(
            Q(license_plate__icontains=search_query) |
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(color__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(visitor_owner__first_name__icontains=search_query) |
            Q(visitor_owner__last_name__icontains=search_query)
        )
    
    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter == 'inside':
        vehicles_list = vehicles_list.filter(is_inside=True)
    elif status_filter == 'outside':
        vehicles_list = vehicles_list.filter(is_inside=False)
    
    # Filter by vehicle type if requested
    type_filter = request.GET.get('type', '')
    if type_filter:
        vehicles_list = vehicles_list.filter(vehicle_type=type_filter)
    
    # Pagination
    paginator = Paginator(vehicles_list, 10)
    page_number = request.GET.get('page')
    vehicles = paginator.get_page(page_number)
    
    context = {
        'vehicles': vehicles,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'security/vehicle_record_management.html', context)

@login_required
def get_vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    data = {
        'id': vehicle.id,
        'license_plate': vehicle.license_plate,
        'make': vehicle.make,
        'model': vehicle.model,
        'color': vehicle.color,
        'vehicle_type': vehicle.vehicle_type,
        'owner': vehicle.owner.username if vehicle.owner else None,
        'visitor_owner': f"{vehicle.visitor_owner.first_name} {vehicle.visitor_owner.last_name}" if vehicle.visitor_owner else None,
    }
    return JsonResponse(data)

@login_required
@require_POST
def update_vehicle(request):
    vehicle_id = request.POST.get('vehicle_id')
    if not vehicle_id:
        return JsonResponse({'success': False, 'message': 'Vehicle ID is required'})
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    try:
        vehicle.license_plate = request.POST.get('license_plate', vehicle.license_plate)
        vehicle.make = request.POST.get('make', vehicle.make)
        vehicle.model = request.POST.get('model', vehicle.model)
        vehicle.color = request.POST.get('color', vehicle.color)
        vehicle.vehicle_type = request.POST.get('vehicle_type', vehicle.vehicle_type)
        vehicle.save()
        return JsonResponse({'success': True, 'message': 'Vehicle updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def delete_vehicle(request):
    vehicle_id = request.POST.get('vehicle_id')
    if not vehicle_id:
        return JsonResponse({'success': False, 'message': 'Vehicle ID is required'})
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    try:
        vehicle.delete()
        return JsonResponse({'success': True, 'message': 'Vehicle deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def check_in_out_vehicle(request):
    vehicle_id = request.POST.get('vehicle_id')
    action = request.POST.get('action')
    
    if not vehicle_id or not action:
        return JsonResponse({'success': False, 'message': 'Missing parameters'})
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Only security guards can perform this action'})
    
    if action == 'in':
        # Create new log entry
        VehicleLog.objects.create(
            vehicle=vehicle,
            security_guard=security_guard,
            purpose=request.POST.get('purpose', ''),
            is_inside=True
        )
        message = 'Vehicle checked in successfully'
    else:
        # Update latest log entry
        log = VehicleLog.objects.filter(vehicle=vehicle, is_inside=True).order_by('-entry_time').first()
        if log:
            log.exit_time = timezone.now()
            log.is_inside = False
            log.save()
            message = 'Vehicle checked out successfully'
        else:
            return JsonResponse({'success': False, 'message': 'No active check-in found for this vehicle'})
    
    return JsonResponse({'success': True, 'message': message})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import SecurityIncidentReport, IncidentMedia, IncidentCategory, IncidentLocation, SecurityGuard
from .forms import IncidentReportForm

@login_required
def incident_dashboard(request):
    # Get the security guard profile
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        return redirect('access_denied')

    # Get all incidents reported by this guard
    incidents_list = SecurityIncidentReport.objects.filter(
        reported_by=security_guard
    ).order_by('-reported_datetime')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        incidents_list = incidents_list.filter(
            Q(reference_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(location__name__icontains=search_query)
        )

    # Filter by status if requested
    status_filter = request.GET.get('status', '')
    if status_filter:
        incidents_list = incidents_list.filter(status=status_filter)

    # Filter by severity if requested
    severity_filter = request.GET.get('severity', '')
    if severity_filter:
        incidents_list = incidents_list.filter(severity=severity_filter)

    # Pagination
    paginator = Paginator(incidents_list, 10)
    page_number = request.GET.get('page')
    incidents = paginator.get_page(page_number)

    context = {
        'incidents': incidents,
        'search_query': search_query,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
    }
    return render(request, 'security/incident_dashboard.html', context)

@login_required
def report_incident(request):
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        return redirect('access_denied')

    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = security_guard
            incident.save()

            # Handle file uploads
            files = request.FILES.getlist('media_files')
            for file in files:
                file_type = 'photo' if file.content_type.startswith('image/') else 'video' if file.content_type.startswith('video/') else 'document'
                IncidentMedia.objects.create(
                    incident=incident,
                    file=file,
                    file_type=file_type
                )

            return redirect('incident_detail', incident_id=incident.id)
    else:
        form = IncidentReportForm()

    context = {
        'form': form,
        'categories': IncidentCategory.objects.all(),
        'locations': IncidentLocation.objects.all(),
    }
    return render(request, 'security/report_incident.html', context)

@login_required
def incident_detail(request, incident_id):
    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
    except SecurityGuard.DoesNotExist:
        return redirect('access_denied')

    incident = get_object_or_404(SecurityIncidentReport, id=incident_id, reported_by=security_guard)
    media_files = IncidentMedia.objects.filter(incident=incident)

    context = {
        'incident': incident,
        'media_files': media_files,
    }
    return render(request, 'security/incident_detail.html', context)

@login_required
@require_POST
def update_incident_status(request):
    incident_id = request.POST.get('incident_id')
    new_status = request.POST.get('new_status')

    if not incident_id or not new_status:
        return JsonResponse({'success': False, 'message': 'Missing parameters'})

    try:
        security_guard = SecurityGuard.objects.get(user=request.user)
        incident = SecurityIncidentReport.objects.get(id=incident_id, reported_by=security_guard)
        incident.status = new_status
        incident.save()
        return JsonResponse({'success': True, 'message': 'Status updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    


from django.shortcuts import render, get_object_or_404
from .models import CCTV, CCTVRecording

def cctv_list(request):
    cctvs = CCTV.objects.all().order_by('location')
    return render(request, 'security/cctv_list.html', {'cctvs': cctvs})

def cctv_detail(request, cctv_id):
    cctv = get_object_or_404(CCTV, pk=cctv_id)
    recordings = cctv.recordings.all().order_by('-start_time')
    return render(request, 'security/cctv_detail.html', {
        'cctv': cctv,
        'recordings': recordings
    })

def recording_detail(request, recording_id):
    recording = get_object_or_404(CCTVRecording, pk=recording_id)
    return render(request, 'security/recording_detail.html', {'recording': recording})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Door, BiometricData, AccessLog
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Door, AccessLog

User = get_user_model()

@login_required
def access_control_dashboard(request):
    doors = Door.objects.filter(is_active=True)
    access_logs = AccessLog.objects.all().order_by('-access_time')[:50]
    users_with_biometrics = User.objects.filter(biometricdata__isnull=False)

    context = {
        'doors': doors,
        'access_logs': access_logs,
        'users': users_with_biometrics,
    }
    return render(request, 'access_control/dashboard.html', context)


@login_required
def door_detail(request, door_id):
    door = Door.objects.get(id=door_id)
    access_logs = AccessLog.objects.filter(door=door).order_by('-access_time')
    
    context = {
        'door': door,
        'access_logs': access_logs,
    }
    return render(request, 'access_control/door_detail.html', context)

@login_required
def user_detail(request, user_id):
    user = User.objects.get(id=user_id)
    biometric_data = BiometricData.objects.filter(user=user).first()
    access_logs = AccessLog.objects.filter(user=user).order_by('-access_time')
    
    context = {
        'user_profile': user,
        'biometric_data': biometric_data,
        'access_logs': access_logs,
    }
    return render(request, 'access_control/user_detail.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import PASystem, PAAnnouncement
from .forms import AnnouncementForm

@login_required
def pa_dashboard(request):
    systems = PASystem.objects.filter(is_active=True)
    recent_announcements = PAAnnouncement.objects.order_by('-created_at')[:10]
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            return redirect('pa_dashboard')
    else:
        form = AnnouncementForm()
    
    context = {
        'systems': systems,
        'recent_announcements': recent_announcements,
        'form': form,
    }
    return render(request, 'pa_system/dashboard.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Item, ItemLog
from .forms import ItemCheckInForm, ItemCheckOutForm

@login_required
def check_in_items(request, visitor_id=None, employee_id=None):
    visitor = get_object_or_404(Visitor, pk=visitor_id) if visitor_id else None
    employee = get_object_or_404(Employee, pk=employee_id) if employee_id else None
    
    if request.method == 'POST':
        form = ItemCheckInForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.visitor = visitor
            item.employee = employee
            item.security_guard = request.user.securityguard
            item.save()
            
            # Create log entry
            ItemLog.objects.create(
                item=item,
                action='check_in',
                security_guard=request.user.securityguard,
                notes=f"Checked in with {visitor or employee}"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'item_code': item.item_code,
                    'description': item.description
                })
            
            messages.success(request, f"Item {item.item_code} checked in successfully")
            return redirect('visitor_detail', pk=visitor_id) if visitor else redirect('employee_detail', pk=employee_id)
    else:
        form = ItemCheckInForm()
    
    context = {
        'form': form,
        'visitor': visitor,
        'employee': employee
    }
    return render(request, 'security/item_checkin.html', context)

@login_required
def check_out_items(request):
    if request.method == 'POST':
        form = ItemCheckOutForm(request.POST)
        if form.is_valid():
            item_code = form.cleaned_data['item_code']
            try:
                item = Item.objects.get(item_code=item_code, status='checked_in')
                item.status = 'checked_out'
                item.check_out_time = timezone.now()
                item.security_guard = request.user.securityguard
                item.save()
                
                # Create log entry
                ItemLog.objects.create(
                    item=item,
                    action='check_out',
                    security_guard=request.user.securityguard,
                    notes=form.cleaned_data['notes']
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'item': {
                            'code': item.item_code,
                            'type': item.item_type.name,
                            'owner': str(item.visitor or item.employee)
                        }
                    })
                
                messages.success(request, f"Item {item.item_code} checked out successfully")
                return redirect('security_dashboard')
            
            except Item.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Item not found or already checked out'
                    }, status=404)
                
                form.add_error('item_code', 'Item not found or already checked out')
    
    else:
        form = ItemCheckOutForm()
    
    return render(request, 'security/item_checkout.html', {'form': form})


from django.http import HttpResponse
from django.shortcuts import render
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.utils.timezone import localtime
from .models import VisitLog, Visitor
import datetime


def visitor_export_page(request):
    """
    Renders the visitor export interface page with optional preview data
    """
    # Get most recent visits for preview (limit to 5)
    recent_logs = VisitLog.objects.all().order_by('-check_in_time')[:5]
    
    context = {
        'recent_logs': recent_logs,
    }
    
    return render(request, 'visitors/export_page.html', context)


def export_visitors_excel(request):
    """
    Exports visitor log data to Excel based on date range parameters
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    
    # Parse dates
    try:
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            logs = VisitLog.objects.filter(check_in_time__range=(start_date, end_date))
        else:
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)
            logs = VisitLog.objects.filter(check_in_time__range=(today, tomorrow))
    except Exception as e:
        return HttpResponse(f"Error parsing date range: {e}")
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Visitor Records"
    
    # Header
    headers = [
        "Batch Number", "First Name", "Last Name", "Company", "Visitor Type", "ID Number",
        "Check-in Time", "Check-out Time", "Department", "Purpose", "Security Guard", "Badge Issued"
    ]
    ws.append(headers)
    
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data rows
    for log in logs:
        visitor = log.visitor
        ws.append([
            log.batch_number,
            visitor.first_name,
            visitor.last_name,
            visitor.company,
            visitor.visitor_type,
            visitor.id_number or "",
            localtime(log.check_in_time).strftime('%Y-%m-%d %H:%M:%S'),
            localtime(log.check_out_time).strftime('%Y-%m-%d %H:%M:%S') if log.check_out_time else "",
            str(log.department),
            log.purpose,
            str(log.security_guard) if log.security_guard else "",
            "Yes" if log.badge_issued else "No",
        ])
    
    # Response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    filename = f"visitor_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response


def preview_data(request):
    """
    Returns preview data for the selected date range via AJAX
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    
    try:
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            logs = VisitLog.objects.filter(check_in_time__range=(start_date, end_date))[:10]  # Limit to 10 records
        else:
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)
            logs = VisitLog.objects.filter(check_in_time__range=(today, tomorrow))[:10]
            
        preview_data = []
        for log in logs:
            visitor = log.visitor
            preview_data.append({
                'batch_number': log.batch_number,
                'name': f"{visitor.first_name} {visitor.last_name}",
                'company': visitor.company,
                'check_in': localtime(log.check_in_time).strftime('%Y-%m-%d %H:%M'),
                'department': str(log.department),
                'purpose': log.purpose
            })
            
        return render(request, 'visitors/preview_data.html', {'logs': preview_data})
    
    except Exception as e:
        return HttpResponse(f"Error retrieving preview data: {e}")