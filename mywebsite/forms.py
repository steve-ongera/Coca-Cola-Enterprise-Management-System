from django import forms
from .models import Leave, Timesheet

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['week_starting', 'hours_worked', 'tasks_completed']
        widgets = {
            'week_starting': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Employee

from django import forms
from .models import Employee, Department, User

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user', 'first_name', 'last_name', 'email', 'phone_number', 'address',
            'department', 'position', 'role', 'employment_status',
            'hire_date', 'contract_type', 'contract_end_date',
            'salary', 'bank_account_number', 'date_of_birth',
            'emergency_contact_name', 'emergency_contact_number',
            'working_id'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-select select2'}),
            'department': forms.Select(attrs={'class': 'form-select select2'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'working_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields automatically
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            
            # Add placeholders
            if field_name not in ['user', 'department', 'position', 'role', 
                                'employment_status', 'contract_type']:
                field.widget.attrs['placeholder'] = field.label
        
        # Custom labels if needed
        self.fields['date_of_birth'].label = "Date of Birth"
        self.fields['contract_end_date'].label = "Contract End Date"
        self.fields['working_id'].label = "Employee ID"
        
        # Make certain fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['hire_date'].required = True
        self.fields['employment_status'].required = True



from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in_time', 'check_out_time', 'status']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_in_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


from django import forms
from .models import Leave
from django.core.exceptions import ValidationError
from datetime import date

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['employee','leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("End date must be after start date")
            if start_date < date.today():
                raise ValidationError("Cannot request leave for past dates")
        
        return cleaned_data
    

from django import forms
from .models import Payroll
from django.core.exceptions import ValidationError
from datetime import date

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'year', 'month', 
            'period_start', 'period_end', 
            'basic_salary', 'allowances', 
            'deductions', 'payment_date',
            'payment_status', 'notes'
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'allowances': forms.Textarea(attrs={'rows': 3, 'placeholder': '{"housing": 1000, "transport": 500}'}),
            'deductions': forms.Textarea(attrs={'rows': 3, 'placeholder': '{"loan": 200, "insurance": 150}'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        payment_date = cleaned_data.get('payment_date')
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')
        employee = cleaned_data.get('employee')
        
        if period_start and period_end:
            if period_start > period_end:
                raise ValidationError("Period end date must be after start date")
            
            if year and month:
                if period_start.year != year or period_start.month != month:
                    raise ValidationError("Period start date must match selected year and month")
        
        if payment_date and period_end:
            if payment_date < period_end:
                raise ValidationError("Payment date cannot be before period end date")
        
        if employee and year and month:
            if Payroll.objects.filter(employee=employee, year=year, month=month).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Payroll record already exists for this employee in selected month/year")
        
        return cleaned_data