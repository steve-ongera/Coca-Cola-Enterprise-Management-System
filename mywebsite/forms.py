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
import json

ALLOWANCE_OPTIONS = [
    ('house', 'House Allowance'),
    ('transport', 'Transport Allowance'),
    ('medical', 'Medical Allowance'),
]

DEDUCTION_OPTIONS = [
    ('tax', 'Tax'),
    ('pension', 'Pension'),
    ('loan', 'Loan'),
]

class PayrollForm(forms.ModelForm):
    # Dynamic fields for allowances
    house_allowance = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="House Allowance"
    )
    transport_allowance = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Transport Allowance"
    )
    medical_allowance = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Medical Allowance"
    )
    
    # Dynamic fields for deductions
    tax_deduction = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Tax"
    )
    pension_deduction = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Pension"
    )
    loan_deduction = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Loan"
    )
    
    class Meta:
        model = Payroll
        fields = [
            'employee', 'year', 'month', 
            'period_start', 'period_end', 
            'basic_salary',
            'payment_date',
            'payment_status', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If we're editing an existing instance, populate the allowance and deduction fields
        if self.instance.pk:
            # Load allowances values safely
            allowances = self.instance.get_allowances_dict()
            if allowances:
                if 'house' in allowances:
                    self.fields['house_allowance'].initial = allowances['house']
                if 'transport' in allowances:
                    self.fields['transport_allowance'].initial = allowances['transport']
                if 'medical' in allowances:
                    self.fields['medical_allowance'].initial = allowances['medical']
            
            # Load deductions values safely
            deductions = self.instance.get_deductions_dict()
            if deductions:
                if 'tax' in deductions:
                    self.fields['tax_deduction'].initial = deductions['tax']
                if 'pension' in deductions:
                    self.fields['pension_deduction'].initial = deductions['pension']
                if 'loan' in deductions:
                    self.fields['loan_deduction'].initial = deductions['loan']

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
            existing_query = Payroll.objects.filter(employee=employee, year=year, month=month)
            if self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)
            if existing_query.exists():
                raise ValidationError("Payroll record already exists for this employee in selected month/year")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Build allowances dict
        allowances = {}
        if self.cleaned_data.get('house_allowance'):
            allowances['house'] = float(self.cleaned_data['house_allowance'])
        if self.cleaned_data.get('transport_allowance'):
            allowances['transport'] = float(self.cleaned_data['transport_allowance'])
        if self.cleaned_data.get('medical_allowance'):
            allowances['medical'] = float(self.cleaned_data['medical_allowance'])
        
        # Build deductions dict
        deductions = {}
        if self.cleaned_data.get('tax_deduction'):
            deductions['tax'] = float(self.cleaned_data['tax_deduction'])
        if self.cleaned_data.get('pension_deduction'):
            deductions['pension'] = float(self.cleaned_data['pension_deduction'])
        if self.cleaned_data.get('loan_deduction'):
            deductions['loan'] = float(self.cleaned_data['loan_deduction'])
        
        # Set directly as dicts (JSONField handles serialization)
        instance.allowances = allowances
        instance.deductions = deductions
        
        if commit:
            instance.save()
        return instance
    


from django import forms
from .models import Product, ProductVariant, ProductCategory

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'description', 'parent_category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'parent_category': forms.Select(attrs={'class': 'select2'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'product_code', 'category', 'launch_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'launch_date': forms.DateInput(attrs={'type': 'date'}),
            'category': forms.Select(attrs={'class': 'select2'}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'size', 'packaging_type', 'barcode', 'status']
        widgets = {
            'barcode': forms.TextInput(attrs={'placeholder': 'Scan or enter barcode'}),
        }


from django import forms
from django.core.validators import FileExtensionValidator
from .models import Product
import magic

class ProductImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )
    update_existing = forms.BooleanField(
        label='Update existing products',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        # Verify file type using magic (actual content, not just extension)
        file_type = magic.from_buffer(csv_file.read(1024), mime=True)
        csv_file.seek(0)  # Reset file pointer
        
        if file_type not in ['text/csv', 'text/plain', 'application/vnd.ms-excel']:
            raise forms.ValidationError('Invalid file type. Please upload a CSV file.')
        
        # Verify file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File too large. Maximum size is 5MB.')
        
        return csv_file