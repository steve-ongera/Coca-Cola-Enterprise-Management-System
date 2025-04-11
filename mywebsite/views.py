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

from django.shortcuts import render, get_object_or_404
from datetime import date
from .models import Employee, PositionHistory, Attendance, Leave, Payroll, PerformanceReview

def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    # Get related data
    position_history = PositionHistory.objects.filter(employee=employee).order_by('-start_date')
    attendance_records = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    leave_requests = Leave.objects.filter(employee=employee).order_by('-start_date')[:10]
    payroll_records = Payroll.objects.filter(employee=employee).order_by('-period_start')[:12]
    performance_reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_period')
    
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
        'position_history': position_history,
        'attendance_records': attendance_records,
        'leave_requests': leave_requests,
        'payroll_records': payroll_records,
        'performance_reviews': performance_reviews,
        'tenure_years': tenure_years,
        'tenure_months': tenure_months,
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

@login_required
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
    
    monthly_data = Attendance.objects.filter(
        employee=attendance.employee,
        date__gte=six_months_ago,
        date__lte=today
    ).values('date__month', 'status').annotate(count=Count('status'))
    
    # Process data for Chart.js
    months = []
    present_data = []
    absent_data = []
    half_day_data = []
    
    for month in range(1, 13):
        month_name = date(1900, month, 1).strftime('%b')
        months.append(month_name)
        
        present = next((item['count'] for item in monthly_data 
                       if item['date__month'] == month and item['status'] == 'present'), 0)
        absent = next((item['count'] for item in monthly_data 
                      if item['date__month'] == month and item['status'] == 'absent'), 0)
        half_day = next((item['count'] for item in monthly_data 
                        if item['date__month'] == month and item['status'] == 'half_day'), 0)
        
        present_data.append(present)
        absent_data.append(absent)
        half_day_data.append(half_day)
    
    chart_data = {
        'months': json.dumps(months),
        'present': json.dumps(present_data),
        'absent': json.dumps(absent_data),
        'half_day': json.dumps(half_day_data),
    }
    
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

# List View
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
    
    employees = Employee.objects.all()
    
    return render(request, 'attendance/attendance_list.html', {
        'attendances': attendances,
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
    
    employees = Employee.objects.all()
    
    return render(request, 'leave/leave_list.html', {
        'leaves': leaves,
        'employees': employees,
        'status_choices': Leave.STATUS_CHOICES,
        'leave_type_choices': Leave.LEAVE_TYPE_CHOICES
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
                if item_form.cleaned_data:
                    item = item_form.save(commit=False)
                    item.purchase_order = order
                    item.save()
            
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
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



# views.py
def low_stock_alerts(request):
    low_stock_items = InventoryItem.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).select_related('product_variant', 'warehouse')
    
    context = {
        'low_stock_items': low_stock_items,
    }
    return render(request, 'inventory/low_stock_alerts.html', context)

