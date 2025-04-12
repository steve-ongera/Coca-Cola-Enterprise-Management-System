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
    



# inventory/forms.py
from django import forms
from .models import *

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'capacity', 'manager', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import *

class StockMovementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit inventory items to active items
        self.fields['inventory_item'].queryset = InventoryItem.objects.select_related(
            'product_variant', 'warehouse'
        ).filter(product_variant__status='active')
        
        # Set current user as default performer
        if user:
            self.fields['performed_by'].initial = user

    class Meta:
        model = StockMovement
        fields = [
            'inventory_item', 
            'date', 
            'quantity_change', 
            'movement_type',
            'content_type',  # Add these two fields to handle the GenericForeignKey
            'object_id',     # relationship instead of directly using 'reference'
            'performed_by'
        ]
        widgets = {
            'inventory_item': forms.Select(attrs={
                'class': 'form-select',
                'data-live-search': 'true'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'quantity_change': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleReferenceField(this)'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'object_id': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'performed_by': forms.HiddenInput()
        }
        labels = {
            'quantity_change': 'Quantity',
            'movement_type': 'Movement Type',
            'content_type': 'Reference Type',
            'object_id': 'Reference ID'
        }

    def clean_quantity_change(self):
        quantity = self.cleaned_data['quantity_change']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be positive")
        return quantity

from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import PurchaseOrder, PurchaseOrderItem

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'expected_delivery_date', 'status']  # adjust based on your actual model fields
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_delivery_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get('order_date')
        delivery_date = cleaned_data.get('expected_delivery_date')
        
        if order_date and delivery_date and delivery_date <= order_date:
            raise forms.ValidationError(
                "Delivery date must be after order date"
            )
        return cleaned_data

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['content_type', 'object_id', 'quantity', 'unit_price', 'notes']
        widgets = {
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'object_id': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit content types to allowed models
        self.fields['content_type'].queryset = ContentType.objects.filter(
            model__in=['ingredient', 'productvariant']
        )
        
        # Set object_id choices based on initial content_type
        if self.initial.get('content_type'):
            model_class = self.initial['content_type'].model_class()
            self.fields['object_id'].queryset = model_class.objects.all()

PurchaseOrderItemFormSet = forms.inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'performance_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'credit_limit':
                field.widget.attrs['placeholder'] = '0.00'
            if field_name == 'payment_terms':
                field.widget.attrs['placeholder'] = 'e.g., Net 30'
            if field.required:
                field.widget.attrs['required'] = 'required'

    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter full address'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@domain.com'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+1234567890'
            })
        }
        labels = {
            'name': 'Customer Name',
            'contact_person': 'Primary Contact',
            'credit_limit': 'Credit Limit ($)'
        }
        help_texts = {
            'credit_limit': 'Enter the maximum credit amount allowed for this customer',
            'payment_terms': 'Specify payment terms like "Net 30" or "Due on receipt"'
        }

    def clean_credit_limit(self):
        credit_limit = self.cleaned_data.get('credit_limit')
        if credit_limit is not None and credit_limit < 0:
            raise forms.ValidationError("Credit limit cannot be negative")
        return credit_limit

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Add your phone validation logic here if needed
        return phone



from django import forms
from .models import DeliveryVehicle, Employee

class DeliveryVehicleForm(forms.ModelForm):
    class Meta:
        model = DeliveryVehicle
        fields = '__all__'
        widgets = {
            'vehicle_type': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select vehicle type'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'e.g. 5000 (kg)'
            }),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2100}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter driver field to show only employees with position "driver"
        self.fields['driver'].queryset = Employee.objects.filter(position='driver')

        for field in self.fields:
            if field not in ['status', 'driver']:
                self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].required:
                self.fields[field].widget.attrs['required'] = 'required'


from django import forms
from .models import *

class ProductionFacilityForm(forms.ModelForm):
    class Meta:
        model = ProductionFacility
        fields = '__all__'
        widgets = {
            'location': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }

from django import forms
from .models import ProductionLine

class ProductionLineForm(forms.ModelForm):
    class Meta:
        model = ProductionLine
        fields = ['name', 'facility', 'product_types', 'capacity_per_hour', 'status']
        widgets = {
            'product_types': forms.SelectMultiple(attrs={'class': 'select2'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

from django import forms
from .models import ProductionBatch

class ProductionBatchForm(forms.ModelForm):
    class Meta:
        model = ProductionBatch
        fields = [
            'production_line',
            'product',
            'quantity_produced',
            'start_time',
            'end_time',
            'quality_check_status'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'quality_check_status': forms.RadioSelect(choices=ProductionBatch.QUALITY_CHECK_STATUS_CHOICES),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['quality_check_status'].widget.attrs.update({'class': 'form-check-input'})

class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
        widgets = {
            'production_line': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_technician': forms.Select(attrs={'class': 'form-select'}),
        }

class DowntimeIncidentForm(forms.ModelForm):
    class Meta:
        model = DowntimeIncident
        fields = '__all__'
        widgets = {
            'production_line': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reported_by': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'resolution': forms.Textarea(attrs={'rows': 3}),
        }