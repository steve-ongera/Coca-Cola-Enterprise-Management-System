# Core Models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from decimal import Decimal
from datetime import date


class User(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    # New fields
    USER_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='employee')

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('non_active', 'Non-Active'),
        ('retired', 'Retired'),
        ('fired', 'Fired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.username} ({self.employee_id}) - {self.get_user_type_display()} - {self.get_status_display()}"



class Permission(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    module = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_departments')
    cost_center = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return self.name


# Employee Management Models
class Employee(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='employee_profile', 
        null=True,  # Allowing user field to be blank
        blank=True  # Allowing user field to be blank
    )
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField( null=True, blank=True)
 
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=20, null=True, blank=True)
    hire_date = models.DateField()
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ]
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    
    education_records = models.JSONField(null=True, blank=True)
    skills = models.JSONField(null=True, blank=True)
    documents = models.JSONField(null=True, blank=True)

    working_id = models.CharField(max_length=20, null=True, blank=True)
    
    contract_type = models.CharField(
        max_length=50, 
        choices=[('permanent', 'Permanent'), ('contract', 'Contract')], 
        default='permanent'
    )

    # Employee's date of birth
    date_of_birth = models.DateField(null=True, blank=True)

    # Job position/role with predefined choices
    POSITION_CHOICES = [
        ('ceo', 'Chief Executive Officer'),
        ('coo', 'Chief Operating Officer'),
        ('cfo', 'Chief Financial Officer'),
        ('cto', 'Chief Technology Officer'),
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
        ('developer', 'Software Developer'),
        ('analyst', 'Business Analyst'),
        ('qa_analyst', 'Quality Assurance Analyst'),
        ('hr', 'Human Resources'),
        ('recruiter', 'Recruiter'),
        ('payroll_specialist', 'Payroll Specialist'),
        ('marketing', 'Marketing Specialist'),
        ('brand_manager', 'Brand Manager'),
        ('sales', 'Sales Executive'),
        ('account_manager', 'Account Manager'),
        ('engineer', 'Manufacturing Engineer'),
        ('maintenance_tech', 'Maintenance Technician'),
        ('logistics', 'Logistics Coordinator'),
        ('warehouse', 'Warehouse Operator'),
        ('forklift_operator', 'Forklift Operator'),
        ('supply_chain', 'Supply Chain Manager'),
        ('procurement', 'Procurement Officer'),
        ('legal', 'Legal Counsel'),
        ('support', 'IT Support'),
        ('it_admin', 'IT Administrator'),
        ('data_scientist', 'Data Scientist'),
        ('driver', 'Delivery Driver'),
        ('security', 'Security Officer'),
        ('cleaner', 'Cleaner'),
        ('intern', 'Intern'),
        ('consultant', 'Consultant'),
        ('admin', 'Administrative Assistant'),
    ]

    position = models.CharField(max_length=100, choices=POSITION_CHOICES, null=True, blank=True)

    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, null=True, blank=True)

    # Department the employee belongs to
    department = models.ForeignKey(
        'Department', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )
    
    # Performance review data (could include ratings, feedback, etc.)
    
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bank_account_number = models.CharField(max_length=30, null=True, blank=True)
    last_promotion_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user else "Employee without account"



class PositionHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='position_history')
    job_title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    reporting_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='subordinates')
    
    class Meta:
        verbose_name_plural = 'Position Histories'
        
    def __str__(self):
        return f"{self.employee} - {self.job_title} ({self.start_date})"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    class Meta:
        unique_together = ['employee', 'date']
        
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

class Task(models.Model):
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    completed = models.BooleanField(default=False)


class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    week_starting = models.DateField()
    hours_worked = models.CharField(max_length=20)
    tasks_completed = models.CharField(max_length=20)

class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual'),
        ('sick', 'Sick'),
        ('maternity', 'Maternity'),
        ('paternity', 'Paternity'),
        ('bereavement', 'Bereavement'),
        ('unpaid', 'Unpaid'),
    ]
    leave_type = models.CharField(max_length=15, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"

from django.db import models
from django.utils.functional import cached_property
from decimal import Decimal
from datetime import date

class Payroll(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='payroll_records')
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 13)], null=True, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.JSONField(default=dict, blank=True)
    deductions = models.JSONField(default=dict, blank=True)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, editable=False, null=True, blank=True)
    payment_date = models.DateField()
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month', 'employee__user__last_name']
    
    def __str__(self):
        return f"{self.employee} - {self.get_month_display()}/{self.year}"
    
    def get_allowances_dict(self):
        """Safely get allowances as a dictionary"""
        if isinstance(self.allowances, str):
            try:
                import json
                return json.loads(self.allowances)
            except (ValueError, TypeError):
                return {}
        return self.allowances or {}
    
    def get_deductions_dict(self):
        """Safely get deductions as a dictionary"""
        if isinstance(self.deductions, str):
            try:
                import json
                return json.loads(self.deductions)
            except (ValueError, TypeError):
                return {}
        return self.deductions or {}
    
    def save(self, *args, **kwargs):
        # Ensure allowances and deductions are dictionaries
        if not self.allowances or not isinstance(self.allowances, dict):
            self.allowances = {}
        
        if not self.deductions or not isinstance(self.deductions, dict):
            self.deductions = {}
            
        # Calculate allowances total - convert to Decimal
        allowances_total = Decimal('0.00')
        for value in self.get_allowances_dict().values():
            allowances_total += Decimal(str(value))
        
        # Calculate deductions total - convert to Decimal
        deductions_total = Decimal('0.00')
        for value in self.get_deductions_dict().values():
            deductions_total += Decimal(str(value))
        
        # Calculate gross salary
        self.gross_salary = self.basic_salary + allowances_total
        
        # Calculate tax (simplified tax calculation - 15%)
        self.tax_amount = self.gross_salary * Decimal('0.15')
        
        # Calculate net salary
        self.net_salary = self.gross_salary - self.tax_amount - deductions_total
        
        # Set year and month from period_start if not set
        if not self.year or not self.month:
            self.year = self.period_start.year
            self.month = self.period_start.month
        
        super().save(*args, **kwargs)
    
    def get_month_display(self):
        return date(1900, self.month, 1).strftime('%b')
    
    def get_pay_period_display(self):
        return f"{self.period_start.strftime('%b %d')} - {self.period_end.strftime('%b %d, %Y')}"
    
    @property
    def total_allowances(self):
        total = Decimal('0.00')
        for value in self.get_allowances_dict().values():
            total += Decimal(str(value))
        return total
    
    @property
    def total_deductions(self):
        total = Decimal('0.00')
        for value in self.get_deductions_dict().values():
            total += Decimal(str(value))
        return total

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews_given')
    review_period = models.CharField(max_length=50)  # e.g., "Q1 2025"
    ratings = models.JSONField()  # Store different metrics and their ratings
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals = models.TextField()
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee} - {self.review_period}"


# Product Management Models
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    
    class Meta:
        verbose_name_plural = 'Product Categories'
        
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    product_code = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    launch_date = models.DateField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.product_code})"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)  # e.g., "330ml", "1.5L"
    PACKAGING_CHOICES = [
        ('can', 'Can'),
        ('bottle', 'Bottle'),
        ('box', 'Box'),
    ]
    packaging_type = models.CharField(max_length=20, choices=PACKAGING_CHOICES)
    barcode = models.CharField(max_length=50, unique=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.size})"

import random
import string
from django.db import models

def generate_supplier_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ------------------------------------------------------------------------------
# Supplier Model
# ------------------------------------------------------------------------------
# This model represents external vendors who provide goods or services to
# Mount Kenya Bottlers (Coca-Cola franchise in Nyeri, Kenya). It tracks all
# relevant supplier information including contact details, tax identifiers,
# products/services supplied, contractual periods, and additional notes.
# It serves as the foundation for managing procurement, purchase orders,
# and inventory replenishment workflows within the system.
# ------------------------------------------------------------------------------


class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, null=True ,  blank=True)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    performance_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    payment_terms = models.CharField(max_length=100, null=True, blank=True)

    contract_start = models.DateField(blank=True, null=True)
    contract_end = models.DateField(blank=True, null=True)

    products_services = models.TextField(blank=True,null=True,)
    notes = models.TextField(blank=True,null=True,default="N/A",)
    
    def save(self, *args, **kwargs):
        if not self.supplier_code:
            # Ensure uniqueness
            code = generate_supplier_code()
            while Supplier.objects.filter(supplier_code=code).exists():
                code = generate_supplier_code()
            self.supplier_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.supplier_code})"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    supplier_options = models.ManyToManyField(Supplier, related_name='ingredients')
    allergen_information = models.TextField(null=True, blank=True)
    nutritional_value = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='products')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_of_measure = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ['product', 'ingredient']
        
    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}"


class QualityControl(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='quality_checks')
    batch_number = models.CharField(max_length=50)
    production_date = models.DateField()
    inspector = models.ForeignKey(Employee, on_delete=models.CASCADE)
    parameters = models.JSONField()  # Store various quality metrics
    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - Batch {self.batch_number}"


# Inventory and Supply Chain Models
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField()
    capacity = models.DecimalField(max_digits=12, decimal_places=2)  # in square meters or similar unit
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_warehouses')
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_of_measure = models.CharField(max_length=20)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2)
    last_restocked = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['product_variant', 'warehouse']
        
    def __str__(self):
        return f"{self.product_variant.name} at {self.warehouse.name}"


class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('partially_received', 'Partially Received'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_purchase_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_purchase_orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"PO-{self.order_number} ({self.supplier.name})"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')  # Can link to Ingredient or ProductVariant
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.item}"


class StockMovement(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_movements')
    date = models.DateTimeField()
    quantity_change = models.DecimalField(max_digits=12, decimal_places=2)  # Positive for in, negative for out
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'In'),
        ('out', 'Out'),
        ('adjustment', 'Adjustment'),
    ]
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    reference = GenericForeignKey('content_type', 'object_id')  # Can link to PurchaseOrder, SalesOrder, etc.
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.inventory_item} - {self.movement_type} {self.quantity_change} on {self.date}"


# Sales and Distribution Models
class Customer(models.Model):
    name = models.CharField(max_length=100)
    CUSTOMER_TYPE_CHOICES = [
        ('distributor', 'Distributor'),
        ('retailer', 'Retailer'),
        ('direct', 'Direct Consumer'),
    ]
    customer_type = models.CharField(max_length=15, choices=CUSTOMER_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_terms = models.CharField(max_length=100, null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return self.name


class SalesOrder(models.Model):
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales_orders')
    order_date = models.DateField()
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    sales_representative = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='sales_orders')
    shipping_address = models.TextField()
    billing_address = models.TextField()
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"SO-{self.order_number} ({self.customer.name})"


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage discount
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product_variant.name}"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField()

    due_date = models.DateField()
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    payment_terms = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"INV-{self.invoice_number}"


class DeliveryVehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('pickup', 'Pickup'),
        ('bike', 'Bike'),
        ('trailer', 'Trailer'),
    ]
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPE_CHOICES ,  null=True)
    model = models.CharField(max_length=50 , null=True)  # e.g., Toyota Hiace
    year = models.PositiveIntegerField(null=True)     # e.g., 2021
    image = models.ImageField(
        upload_to='delivery_vehicles/',
        null=True,
        blank=True,
      
    )
    capacity = models.DecimalField(max_digits=10, decimal_places=2)  # in kilograms or similar unit
    driver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='assigned_vehicles')
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('maintenance', 'Maintenance'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')

    @property
    def active_deliveries(self):
        """Returns queryset of active deliveries for this vehicle"""
        return self.deliveries.filter(status__in=['scheduled', 'in_transit'])
    
    def __str__(self):
        return f"{self.vehicle_type} - {self.vehicle_number}"

from django.db import models
from django.core.validators import MinValueValidator


class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ('routine', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('other', 'Other'),
    ]
    
    vehicle = models.ForeignKey(DeliveryVehicle, on_delete=models.CASCADE,related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20,choices=MAINTENANCE_TYPES,default='routine')
    date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,validators=[MinValueValidator(0)])
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-date']
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'

    def __str__(self):
        return f"{self.get_maintenance_type_display()} on {self.date}"

class StatusLog(models.Model):
    vehicle = models.ForeignKey(DeliveryVehicle, on_delete=models.CASCADE,related_name='status_logs')
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    from_status = models.CharField(max_length=50)
    to_status = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DeliveryRoute(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    regions_covered = models.JSONField()
    estimated_time = models.DurationField()  # e.g., 2 hours
    assigned_vehicle = models.ForeignKey(DeliveryVehicle, on_delete=models.SET_NULL, null=True, related_name='routes')
    
    
    def __str__(self):
        return self.name


class Delivery(models.Model):
    delivery_number = models.CharField(max_length=20, unique=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='deliveries')
    delivery_route = models.ForeignKey(DeliveryRoute, on_delete=models.SET_NULL, null=True)
    scheduled_date = models.DateTimeField()
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(null=True, blank=True)

    vehicle = models.ForeignKey(
        DeliveryVehicle, 
        on_delete=models.CASCADE,
        related_name='deliveries'  # This creates the reverse relationship
    )
    
    class Meta:
        verbose_name_plural = 'Deliveries'
        
    def __str__(self):
        return f"DEL-{self.delivery_number}"


# Finance and Accounting Models
class Account(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_accounts')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.account_number} - {self.name}"


class Transaction(models.Model):
    transaction_date = models.DateField()
    description = models.TextField()
    reference_number = models.CharField(max_length=50, unique=True)
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('voided', 'Voided'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transactions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transaction {self.reference_number} - {self.transaction_date}"


class TransactionEntry(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transaction_entries')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    ENTRY_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    entry_type = models.CharField(max_length=6, choices=ENTRY_TYPE_CHOICES)
    
    class Meta:
        verbose_name_plural = 'Transaction Entries'
        
    def __str__(self):
        return f"{self.transaction.reference_number} - {self.account.name} ({self.entry_type} {self.amount})"


class Budget(models.Model):
    fiscal_year = models.CharField(max_length=10)  # e.g., "2025"
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='budgets')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_budgets')
    
    class Meta:
        unique_together = ['fiscal_year', 'department', 'account', 'period']
        
    def __str__(self):
        return f"{self.department.name} - {self.account.name} ({self.fiscal_year})"


class Payment(models.Model):
    payment_number = models.CharField(max_length=20, unique=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
    ]
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    reference = GenericForeignKey('content_type', 'object_id')  # Can point to Invoice, etc.
    received_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_number} - {self.amount}"


class TaxRecord(models.Model):
    tax_type = models.CharField(max_length=50)
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    filing_date = models.DateField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    documents = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.tax_type} ({self.period_start} to {self.period_end})"


# Marketing Models
class MarketingCampaign(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    target_audience = models.TextField()
    region = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planning')
    manager = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='managed_campaigns')
    
    def __str__(self):
        return self.name


class CampaignAsset(models.Model):
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE, related_name='assets')
    ASSET_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPE_CHOICES)
    file = models.FileField(upload_to='campaign_assets/')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    upload_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.campaign.name} - {self.name}"


class PromotionalCode(models.Model):
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE, related_name='promo_codes')
    code = models.CharField(max_length=20, unique=True)
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_until = models.DateField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.code


class CampaignPerformance(models.Model):
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE, related_name='performance_metrics')
    metric_name = models.CharField(max_length=50)
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    actual_value = models.DecimalField(max_digits=12, decimal_places=2)
    date_recorded = models.DateField()
    
    def __str__(self):
        return f"{self.campaign.name} - {self.metric_name}"


# CRM Models
class CustomerInteraction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_date = models.DateTimeField()
    INTERACTION_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
    ]
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPE_CHOICES)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='customer_interactions')
    notes = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.customer.name} - {self.interaction_type} on {self.interaction_date}"


class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_expiry_period = models.PositiveIntegerField()  # In days
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return self.name


class CustomerLoyalty(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty')
    loyalty_program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE)
    points_balance = models.PositiveIntegerField(default=0)
    tier_level = models.CharField(max_length=20, default='standard')
    enrollment_date = models.DateField()
    
    class Meta:
        verbose_name_plural = 'Customer Loyalties'
        unique_together = ['customer', 'loyalty_program']
        
    def __str__(self):
        return f"{self.customer.name} - {self.loyalty_program.name}"


class SupportTicket(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=100)
    description = models.TextField()
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='assigned_tickets')
    created_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.subject}"


# Production Line Models
class ProductionFacility(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField()
    capacity = models.DecimalField(max_digits=12, decimal_places=2)  # in liters per day or similar unit
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_facilities')
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        verbose_name_plural = 'Production Facilities'
        
    def __str__(self):
        return self.name

class FacilityChangeLog(models.Model):
    facility = models.ForeignKey(ProductionFacility, on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_fields = models.TextField()
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        
    def __str__(self):
        return f"{self.facility.name} updated by {self.user} at {self.changed_at}"

class ProductionLine(models.Model):
    facility = models.ForeignKey(ProductionFacility, on_delete=models.CASCADE, related_name='production_lines')
    name = models.CharField(max_length=100)
    product_types = models.ManyToManyField(Product, related_name='production_lines')
    capacity_per_hour = models.DecimalField(max_digits=10, decimal_places=2)  # in bottles/cans per hour
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Maintenance'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='operational')
    
    def __str__(self):
        return f"{self.facility.name} - {self.name}"


class ProductionBatch(models.Model):
    batch_number = models.CharField(max_length=20, unique=True)
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='batches')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_batches')
    quantity_produced = models.DecimalField(max_digits=12, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    QUALITY_CHECK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    quality_check_status = models.CharField(max_length=10, choices=QUALITY_CHECK_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.product.name} - Batch {self.batch_number}"


class MaintenanceSchedule(models.Model):
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.CharField(max_length=50)
    scheduled_date = models.DateTimeField()
    estimated_duration = models.DurationField()  # e.g., 2 hours
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    notes = models.TextField(blank=True, null=True, verbose_name="Work Description")
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True, null=True)
    assigned_technician = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='maintenance_assignments')
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')
    
    def __str__(self):
        return f"{self.production_line.name} - {self.maintenance_type} on {self.scheduled_date}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MaintenanceLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('started', 'Work Started'),
        ('completed', 'Work Completed'),
        ('cancelled', 'Cancelled'),
        ('updated', 'Updated'),
        ('part_replaced', 'Part Replaced'),
        ('note_added', 'Note Added'),
    ]

    maintenance = models.ForeignKey(
        'MaintenanceSchedule',
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action Type"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Performed By"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Additional Notes"
    )
    parts_used = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Parts Inventory Used",
        help_text="JSON of parts and quantities used"
    )

    class Meta:
        verbose_name = "Maintenance Log Entry"
        verbose_name_plural = "Maintenance Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['maintenance']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} at {self.timestamp}"

class DowntimeIncident(models.Model):
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE, related_name='downtime_incidents')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
    reported_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reported_downtimes')
    resolution = models.TextField(null=True, blank=True)
    impact_assessment = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.production_line.name} - Downtime on {self.start_time}"


# Sustainability Models
class ResourceConsumption(models.Model):
    facility = models.ForeignKey(ProductionFacility, on_delete=models.CASCADE, related_name='resource_consumption')
    RESOURCE_TYPE_CHOICES = [
        ('water', 'Water'),
        ('electricity', 'Electricity'),
        ('gas', 'Gas'),
    ]
    resource_type = models.CharField(max_length=15, choices=RESOURCE_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_of_measure = models.CharField(max_length=20)
    source = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.facility.name} - {self.resource_type} ({self.period_start} to {self.period_end})"


class CarbonEmission(models.Model):
    facility = models.ForeignKey(ProductionFacility, on_delete=models.CASCADE, related_name='carbon_emissions')
    emission_source = models.CharField(max_length=100)
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)  # in CO2 equivalent
    unit_of_measure = models.CharField(max_length=20)
    calculation_method = models.TextField()
    
    def __str__(self):
        return f"{self.facility.name} - {self.emission_source} ({self.period_start} to {self.period_end})"


class RecyclingRecord(models.Model):
    facility = models.ForeignKey(ProductionFacility, on_delete=models.CASCADE, related_name='recycling_records')
    material_type = models.CharField(max_length=50)
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    recycling_partner = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.facility.name} - {self.material_type} ({self.period_start} to {self.period_end})"


class ComplianceReport(models.Model):
    report_name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50)
    submission_date = models.DateField()
    submitted_to = models.CharField(max_length=100)
    period_covered = models.CharField(max_length=50)
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    prepared_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='prepared_reports')
    documents = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.report_name} ({self.submission_date})"


# Reporting and Dashboard Models
class Report(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    report_type = models.CharField(max_length=50)
    parameters = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    is_public = models.BooleanField(default=False)
    last_generated = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class SavedDashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    name = models.CharField(max_length=100)
    layout = models.JSONField(default=dict)  # Store widget positions
    is_default = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'name']
        
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DashboardWidget(models.Model):
    dashboard = models.ForeignKey(SavedDashboard, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=50)
    data_source = models.CharField(max_length=100)
    refresh_interval = models.PositiveIntegerField(default=0)  # in minutes, 0 means no auto-refresh
    position_x = models.PositiveIntegerField()
    position_y = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    configuration = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.widget_type}"


class ScheduledReport(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    SCHEDULE_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    schedule_type = models.CharField(max_length=10, choices=SCHEDULE_TYPE_CHOICES)
    recipients = models.JSONField()  # Store email addresses as a list
    next_run = models.DateTimeField()
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    format = models.CharField(max_length=5, choices=FORMAT_CHOICES, default='pdf')
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.report.name} - {self.schedule_type}"


# Notification and Communication Models
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type} at {self.created_at}"


class Announcement(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.PositiveIntegerField(default=0)  # Higher number = higher priority
    target_departments = models.ManyToManyField(Department, related_name='announcements')
    expiry_date = models.DateField()
    
    def __str__(self):
        return self.title


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50)
    object_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} on {self.object_type} at {self.timestamp}"


# System Configuration Models
class Setting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField()
    description = models.TextField()
    data_type = models.CharField(max_length=20)  # string, integer, boolean, json
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.key


class Region(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)
    language = models.CharField(max_length=50)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ProductionTarget(models.Model):
    PRODUCT_CHOICES = [
        ('cola_330ml', 'Coca-Cola 330ml'),
        ('cola_500ml', 'Coca-Cola 500ml'),
        ('cola_1l', 'Coca-Cola 1L'),
        ('sprite_330ml', 'Sprite 330ml'),
        ('fanta_500ml', 'Fanta Orange 500ml'),
        ('schweppes_1l', 'Schweppes 1L'),
    ]
    
    SHIFT_CHOICES = [
        ('morning', 'Morning Shift (8AM-4PM)'),
        ('afternoon', 'Afternoon Shift (12PM-8PM)'),
        ('night', 'Night Shift (8PM-4AM)'),
    ]
    
    product = models.CharField(max_length=50, choices=PRODUCT_CHOICES)
    production_line = models.ForeignKey('ProductionLine', on_delete=models.CASCADE)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    target_quantity = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)
    team = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'production_line', 'shift', 'date')
        ordering = ['date', 'shift']
    
    def __str__(self):
        return f"{self.get_product_display()} - {self.shift} - {self.date}"
    
    @property
    def completed_quantity(self):
        from .models import ProductionLog
        return ProductionLog.objects.filter(
            production_target=self
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    @property
    def percent_complete(self):
        if self.target_quantity == 0:
            return 0
        return min(round((self.completed_quantity / self.target_quantity) * 100, 100))



class QualityCheck(models.Model):
    CHECK_TYPE_CHOICES = [
        ('bottle_seal', 'Bottle Seal Integrity'),
        ('fill_level', 'Fill Level'),
        ('label_placement', 'Label Placement'),
        ('sugar_content', 'Sugar Content'),
        ('carbonation', 'Carbonation Level'),
        ('packaging', 'Packaging Quality'),
    ]
    
    check_type = models.CharField(max_length=50, choices=CHECK_TYPE_CHOICES)
    production_line = models.ForeignKey(ProductionLine, on_delete=models.CASCADE)
    checked_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ], default='pending')
    notes = models.TextField(blank=True)
    checked_at = models.DateTimeField(default=timezone.now)
    next_check_due = models.DateTimeField()
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.get_check_type_display()} - {self.production_line} - {self.checked_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.next_check_due and self.status != 'passed'

class TrainingSession(models.Model):
    TRAINING_TYPE_CHOICES = [
        ('safety', 'Safety Training'),
        ('quality', 'Quality Control'),
        ('equipment', 'Equipment Operation'),
        ('hygiene', 'Hygiene Practices'),
        ('soft_skills', 'Soft Skills'),
    ]
    
    title = models.CharField(max_length=200)
    training_type = models.CharField(max_length=50, choices=TRAINING_TYPE_CHOICES)
    description = models.TextField()
    trainer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='trainings_conducted')
    date = models.DateField()
    time = models.TimeField()
    duration = models.DurationField(help_text="Duration in hours")
    location = models.CharField(max_length=100)
    max_participants = models.PositiveIntegerField()
    target_groups = models.ManyToManyField(Department, help_text="Which departments should attend")
    is_mandatory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"
    
    @property
    def registered_count(self):
        return self.registrations.count()
    
    @property
    def available_slots(self):
        return self.max_participants - self.registered_count
    
    @property
    def is_full(self):
        return self.registered_count >= self.max_participants

class TrainingRegistration(models.Model):
    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='registrations')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='training_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('training', 'employee')
    
    def __str__(self):
        return f"{self.employee} - {self.training}"

class SafetyAlert(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    affected_areas = models.ManyToManyField(ProductionLine)
    issued_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
    
    @property
    def is_resolved(self):
        return self.resolved_at is not None
    
    def resolve(self):
        self.resolved_at = timezone.now()
        self.is_active = False
        self.save()

class SafetyChecklist(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    frequency = models.CharField(max_length=50, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class SafetyChecklistItem(models.Model):
    checklist = models.ForeignKey(SafetyChecklist, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    is_critical = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.checklist.name} - Item {self.id}"

class SafetyChecklistCompletion(models.Model):
    checklist = models.ForeignKey(SafetyChecklist, on_delete=models.CASCADE)
    completed_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.checklist} completed by {self.completed_by}"

class IncidentReport(models.Model):
    INCIDENT_TYPE_CHOICES = [
        ('injury', 'Personal Injury'),
        ('equipment', 'Equipment Failure'),
        ('spill', 'Chemical Spill'),
        ('near_miss', 'Near Miss'),
        ('security', 'Security Breach'),
    ]
    
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    
    reported_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    location = models.ForeignKey(ProductionLine, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    action_taken = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_time']
    
    def __str__(self):
        return f"{self.get_incident_type_display()} at {self.location} - {self.date_time.strftime('%Y-%m-%d')}"
    


