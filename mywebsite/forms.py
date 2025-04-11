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

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user', 'department', 'position', 'employment_status',
            'hire_date', 'contract_type', 'salary', 
            'emergency_contact_name', 'emergency_contact_number',
            
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'user': forms.Select(attrs={'class': 'select2'}),
            'department': forms.Select(attrs={'class': 'select2'}),
            'manager': forms.Select(attrs={'class': 'select2'}),
        }

