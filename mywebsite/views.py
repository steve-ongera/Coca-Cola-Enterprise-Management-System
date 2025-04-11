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
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    Employee, Department, Attendance, 
    SalesOrder, PurchaseOrder, Payroll
)
import json

def admin_dashboard_view(request):
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
    # Get filter parameters from request
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    
    employees = Employee.objects.select_related('department', 'user').all()
    
    # Apply filters if provided
    if department_id:
        employees = employees.filter(department_id=department_id)
    if status:
        employees = employees.filter(employment_status=status)
    
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
        'current_department': int(department_id) if department_id else None,
        'current_status': status if status else None,
    }
    return render(request, 'employees/employee_list.html', context)

@login_required
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

@login_required
@permission_required('employees.view_employee', raise_exception=True)
def employee_detail(request, pk):
    employee = get_object_or_404(Employee.objects.select_related(
        'user', 'department', 'manager'
    ), pk=pk)
    
    # Get related data
    documents = employee.documents.all()[:5]
    training = employee.training_registrations.select_related('training')[:5]
    
    context = {
        'employee': employee,
        'documents': documents,
        'training': training,
    }
    return render(request, 'employees/employee_detail.html', context)

@login_required
@permission_required('employees.change_employee', raise_exception=True)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            updated_employee = form.save()
            messages.success(request, f'Employee {updated_employee.user.get_full_name()} updated successfully!')
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'title': f'Edit {employee.user.get_full_name()}',
        'employee': employee,
    }
    return render(request, 'employees/employee_form.html', context)

@login_required
@permission_required('employees.delete_employee', raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        full_name = employee.user.get_full_name()
        employee.delete()
        messages.success(request, f'Employee {full_name} deleted successfully!')
        return redirect('employee_list')
    
    context = {'employee': employee}
    return render(request, 'employees/employee_confirm_delete.html', context)

