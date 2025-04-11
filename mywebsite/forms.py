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