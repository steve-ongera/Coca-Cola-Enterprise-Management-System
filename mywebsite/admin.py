from django.contrib import admin
from django.utils.html import format_html
from .models import (
    # Core Models
    User, Permission, Role, Department,
    # Employee Management Models
    Employee, PositionHistory, Attendance, Leave, Payroll, PerformanceReview,
    # Product Management Models
    ProductCategory, Product, ProductVariant, Supplier, Ingredient, ProductIngredient, QualityControl,
    # Inventory and Supply Chain Models
    Warehouse, InventoryItem
)

# Core Models Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'employee_id', 'email', 'first_name', 'last_name', 'user_type', 'status', 'is_staff', 'is_active']
    search_fields = ['username', 'employee_id', 'email', 'first_name', 'last_name', 'user_type', 'status']
    list_filter = ['is_staff', 'is_active', 'user_type', 'status']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'employee_id', 'contact_number', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type & Status', {'fields': ('user_type', 'status')}),  # Added section for user_type and status
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'module']
    search_fields = ['name', 'code', 'module']
    list_filter = ['module']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'get_permissions']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    
    def get_permissions(self, obj):
        return ", ".join([p.name for p in obj.permissions.all()[:5]])
    get_permissions.short_description = 'Permissions'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'cost_center']
    search_fields = ['name', 'cost_center']
    raw_id_fields = ['manager']


# Employee Management Models Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_employee_id', 'hire_date', 'employment_status', 'get_department']
    search_fields = ['user__first_name', 'user__last_name', 'user__employee_id']
    list_filter = ['employment_status', 'hire_date']
    raw_id_fields = ['user']
    
    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "No user assigned"

    get_full_name.short_description = 'Name'
    
    def get_employee_id(self, obj):
        if obj.user:
            return obj.working_id
        return "N/A"

    get_employee_id.short_description = 'Employee ID'

    
    def get_department(self, obj):
        current_position = obj.position_history.filter(end_date__isnull=True).first()
        if current_position:
            return current_position.department.name
        return '-'
    get_department.short_description = 'Department'


@admin.register(PositionHistory)
class PositionHistoryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'job_title', 'department', 'start_date', 'end_date', 'salary', 'reporting_to']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'job_title']
    list_filter = ['department', 'start_date']
    raw_id_fields = ['employee', 'reporting_to']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in_time', 'check_out_time', 'status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    list_filter = ['status', 'date']
    date_hierarchy = 'date'
    raw_id_fields = ['employee']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    list_filter = ['leave_type', 'status', 'start_date']
    date_hierarchy = 'start_date'
    raw_id_fields = ['employee', 'approved_by']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period_start', 'period_end', 'basic_salary', 'net_salary', 'payment_status', 'payment_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    list_filter = ['payment_status', 'payment_date', 'period_start']
    date_hierarchy = 'payment_date'
    raw_id_fields = ['employee']


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'reviewer', 'review_period', 'status', 'created_at', 'updated_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reviewer__user__first_name', 'reviewer__user__last_name']
    list_filter = ['status', 'review_period', 'created_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['employee', 'reviewer']


# Product Management Models Admin
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'parent_category']
    search_fields = ['name']
    list_filter = ['parent_category']
    raw_id_fields = ['parent_category']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_code', 'category', 'launch_date', 'status', 'created_at']
    search_fields = ['name', 'product_code']
    list_filter = ['status', 'category', 'launch_date']
    date_hierarchy = 'launch_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'size', 'packaging_type', 'barcode', 'status']
    search_fields = ['name', 'product__name', 'barcode']
    list_filter = ['status', 'packaging_type', 'product__category']
    raw_id_fields = ['product']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'status', 'performance_rating']
    search_fields = ['name', 'contact_person', 'email']
    list_filter = ['status']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'get_suppliers']
    search_fields = ['name']
    filter_horizontal = ['supplier_options']
    
    def get_suppliers(self, obj):
        return ", ".join([s.name for s in obj.supplier_options.all()[:3]])
    get_suppliers.short_description = 'Suppliers'


@admin.register(ProductIngredient)
class ProductIngredientAdmin(admin.ModelAdmin):
    list_display = ['product', 'ingredient', 'quantity', 'unit_of_measure']
    search_fields = ['product__name', 'ingredient__name']
    list_filter = ['unit_of_measure', 'product__category']
    raw_id_fields = ['product', 'ingredient']


@admin.register(QualityControl)
class QualityControlAdmin(admin.ModelAdmin):
    list_display = ['product', 'batch_number', 'production_date', 'inspector', 'status', 'created_at']
    search_fields = ['product__name', 'batch_number']
    list_filter = ['status', 'production_date']
    date_hierarchy = 'production_date'
    raw_id_fields = ['product', 'inspector']


# Inventory and Supply Chain Models Admin
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'manager', 'status']
    search_fields = ['name', 'location']
    list_filter = ['status']
    raw_id_fields = ['manager']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['product_variant', 'warehouse', 'quantity', 'unit_of_measure', 'reorder_level', 'last_restocked']
    search_fields = ['product_variant__name', 'warehouse__name']
    list_filter = ['warehouse', 'unit_of_measure']
    date_hierarchy = 'last_restocked'
    raw_id_fields = ['product_variant', 'warehouse']


from django.contrib import admin
from .models import (
    PurchaseOrder, PurchaseOrderItem, StockMovement,
    Customer, SalesOrder, SalesOrderItem, Invoice,
    DeliveryVehicle, DeliveryRoute, Delivery
)

# Inventory Management Admins
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    raw_id_fields = ['content_type']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'expected_delivery_date', 'status', 'total_amount']
    list_filter = ['status', 'order_date', 'expected_delivery_date']
    search_fields = ['order_number', 'supplier__name']
    date_hierarchy = 'order_date'
    raw_id_fields = ['supplier', 'created_by', 'approved_by']
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'item', 'quantity', 'unit_price', 'received_quantity']
    list_filter = ['purchase_order__status']
    search_fields = ['purchase_order__order_number']
    raw_id_fields = ['purchase_order', 'content_type']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'date', 'quantity_change', 'movement_type', 'reference', 'performed_by']
    list_filter = ['movement_type', 'date']
    search_fields = ['inventory_item__product_variant__name', 'inventory_item__warehouse__name']
    date_hierarchy = 'date'
    raw_id_fields = ['inventory_item', 'content_type', 'performed_by']


# Sales and Distribution Admins
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer_type', 'contact_person', 'email', 'phone', 'status', 'credit_limit']
    list_filter = ['customer_type', 'status']
    search_fields = ['name', 'contact_person', 'email', 'phone']


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    raw_id_fields = ['product_variant']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'status', 'payment_status', 'total_amount']
    list_filter = ['status', 'payment_status', 'order_date']
    search_fields = ['order_number', 'customer__name']
    date_hierarchy = 'order_date'
    raw_id_fields = ['customer', 'sales_representative']
    inlines = [SalesOrderItemInline]


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ['sales_order', 'product_variant', 'quantity', 'unit_price', 'discount', 'subtotal']
    list_filter = ['sales_order__status']
    search_fields = ['sales_order__order_number', 'product_variant__name']
    raw_id_fields = ['sales_order', 'product_variant']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'sales_order', 'invoice_date', 'due_date', 'status', 'total_amount']
    list_filter = ['status', 'invoice_date', 'due_date']
    search_fields = ['invoice_number', 'sales_order__order_number', 'sales_order__customer__name']
    date_hierarchy = 'invoice_date'
    raw_id_fields = ['sales_order']


@admin.register(DeliveryVehicle)
class DeliveryVehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'vehicle_type', 'capacity', 'driver', 'status']
    list_filter = ['status', 'vehicle_type']
    search_fields = ['vehicle_number', 'driver__user__first_name', 'driver__user__last_name']
    raw_id_fields = ['driver']


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'estimated_time', 'assigned_vehicle']
    search_fields = ['name', 'description']
    raw_id_fields = ['assigned_vehicle']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_number', 'sales_order', 'delivery_route', 'scheduled_date', 'actual_delivery_date', 'status']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['delivery_number', 'sales_order__order_number', 'sales_order__customer__name']
    date_hierarchy = 'scheduled_date'
    raw_id_fields = ['sales_order', 'delivery_route']



from django.contrib import admin
from .models import (
    # Finance and Accounting Models
    Account, Transaction, TransactionEntry, Budget, Payment, TaxRecord,
    
    # Marketing Models
    MarketingCampaign, CampaignAsset, PromotionalCode, CampaignPerformance,
    
    # CRM Models
    CustomerInteraction, LoyaltyProgram, CustomerLoyalty, SupportTicket
)

# Finance and Accounting Admin
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'name', 'account_type', 'parent_account', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['account_number', 'name']
    raw_id_fields = ['parent_account']


class TransactionEntryInline(admin.TabularInline):
    model = TransactionEntry
    extra = 2
    raw_id_fields = ['account']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'transaction_date', 'description', 'status', 'created_by', 'approved_by']
    list_filter = ['status', 'transaction_date']
    search_fields = ['reference_number', 'description']
    date_hierarchy = 'transaction_date'
    raw_id_fields = ['created_by', 'approved_by']
    inlines = [TransactionEntryInline]


@admin.register(TransactionEntry)
class TransactionEntryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'account', 'amount', 'entry_type']
    list_filter = ['entry_type', 'transaction__status']
    search_fields = ['transaction__reference_number', 'account__name']
    raw_id_fields = ['transaction', 'account']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['department', 'account', 'fiscal_year', 'period', 'amount', 'approved_by']
    list_filter = ['fiscal_year', 'period', 'department']
    search_fields = ['department__name', 'account__name', 'fiscal_year']
    raw_id_fields = ['department', 'account', 'approved_by']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'payment_date', 'amount', 'payment_method', 'reference', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_number', 'notes']
    date_hierarchy = 'payment_date'
    raw_id_fields = ['content_type', 'received_by']


@admin.register(TaxRecord)
class TaxRecordAdmin(admin.ModelAdmin):
    list_display = ['tax_type', 'period_start', 'period_end', 'amount', 'filing_date', 'status']
    list_filter = ['tax_type', 'status', 'filing_date']
    search_fields = ['tax_type']
    date_hierarchy = 'filing_date'


# Marketing Admin
class CampaignAssetInline(admin.TabularInline):
    model = CampaignAsset
    extra = 1


class PromotionalCodeInline(admin.TabularInline):
    model = PromotionalCode
    extra = 1


class CampaignPerformanceInline(admin.TabularInline):
    model = CampaignPerformance
    extra = 1


@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'budget', 'region', 'status', 'manager']
    list_filter = ['status', 'region', 'start_date']
    search_fields = ['name', 'description', 'region']
    date_hierarchy = 'start_date'
    raw_id_fields = ['manager']
    inlines = [CampaignAssetInline, PromotionalCodeInline, CampaignPerformanceInline]


@admin.register(CampaignAsset)
class CampaignAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'asset_type', 'upload_date']
    list_filter = ['asset_type', 'upload_date']
    search_fields = ['name', 'campaign__name']
    date_hierarchy = 'upload_date'
    raw_id_fields = ['campaign']


@admin.register(PromotionalCode)
class PromotionalCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'campaign', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'usage_limit', 'times_used']
    list_filter = ['discount_type', 'valid_from', 'valid_until']
    search_fields = ['code', 'campaign__name']
    date_hierarchy = 'valid_from'
    raw_id_fields = ['campaign']


@admin.register(CampaignPerformance)
class CampaignPerformanceAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'metric_name', 'target_value', 'actual_value', 'date_recorded']
    list_filter = ['metric_name', 'date_recorded']
    search_fields = ['campaign__name', 'metric_name']
    date_hierarchy = 'date_recorded'
    raw_id_fields = ['campaign']


# CRM Admin
@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'interaction_type', 'interaction_date', 'employee', 'follow_up_date', 'follow_up_status']
    list_filter = ['interaction_type', 'follow_up_status', 'interaction_date']
    search_fields = ['customer__name', 'notes']
    date_hierarchy = 'interaction_date'
    raw_id_fields = ['customer', 'employee']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_expiry_period', 'status']
    list_filter = ['status']
    search_fields = ['name', 'description']


@admin.register(CustomerLoyalty)
class CustomerLoyaltyAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loyalty_program', 'points_balance', 'tier_level', 'enrollment_date']
    list_filter = ['tier_level', 'enrollment_date', 'loyalty_program']
    search_fields = ['customer__name', 'loyalty_program__name']
    date_hierarchy = 'enrollment_date'
    raw_id_fields = ['customer', 'loyalty_program']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'customer', 'subject', 'priority', 'status', 'assigned_to', 'created_date', 'resolved_date']
    list_filter = ['priority', 'status', 'created_date']
    search_fields = ['ticket_number', 'subject', 'description', 'customer__name']
    date_hierarchy = 'created_date'
    raw_id_fields = ['customer', 'assigned_to']



from django.contrib import admin
from .models import (
    ProductionFacility, ProductionLine, ProductionBatch, MaintenanceSchedule,
    DowntimeIncident, ResourceConsumption, CarbonEmission, RecyclingRecord,
    ComplianceReport, Report
)

@admin.register(ProductionFacility)
class ProductionFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'manager', 'status')
    search_fields = ('name', 'location')
    list_filter = ('status',)

@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'facility', 'capacity_per_hour', 'status')
    list_filter = ('status', 'facility')
    search_fields = ('name',)

@admin.register(ProductionBatch)
class ProductionBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'product', 'production_line', 'quantity_produced', 'start_time', 'end_time', 'quality_check_status')
    list_filter = ('quality_check_status', 'product')
    search_fields = ('batch_number',)

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('production_line', 'maintenance_type', 'scheduled_date', 'assigned_technician', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('maintenance_type',)

@admin.register(DowntimeIncident)
class DowntimeIncidentAdmin(admin.ModelAdmin):
    list_display = ('production_line', 'start_time', 'end_time', 'reported_by')
    list_filter = ('production_line', 'start_time')
    search_fields = ('reason', 'reported_by__first_name', 'reported_by__last_name')

@admin.register(ResourceConsumption)
class ResourceConsumptionAdmin(admin.ModelAdmin):
    list_display = ('facility', 'resource_type', 'period_start', 'period_end', 'quantity', 'unit_of_measure')
    list_filter = ('resource_type',)
    search_fields = ('facility__name',)

@admin.register(CarbonEmission)
class CarbonEmissionAdmin(admin.ModelAdmin):
    list_display = ('facility', 'emission_source', 'period_start', 'period_end', 'quantity', 'unit_of_measure')
    list_filter = ('facility',)
    search_fields = ('emission_source',)

@admin.register(RecyclingRecord)
class RecyclingRecordAdmin(admin.ModelAdmin):
    list_display = ('facility', 'material_type', 'period_start', 'period_end', 'quantity', 'recycling_partner', 'certificate_number')
    list_filter = ('material_type',)
    search_fields = ('recycling_partner',)

@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ('report_name', 'report_type', 'submission_date', 'submitted_to', 'period_covered', 'status', 'prepared_by')
    list_filter = ('status',)
    search_fields = ('report_name', 'submitted_to')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'is_public', 'last_generated')
    list_filter = ('report_type', 'is_public')
    search_fields = ('name', 'description')


from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    SavedDashboard, DashboardWidget, ScheduledReport,
    Notification, Announcement, ActivityLog,
    Setting, Region
)

@admin.register(SavedDashboard)
class SavedDashboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_default')
    search_fields = ('name', 'user__username')
    list_filter = ('is_default',)

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('dashboard', 'widget_type', 'data_source', 'refresh_interval')
    list_filter = ('widget_type', 'refresh_interval')
    search_fields = ('widget_type', 'data_source')

@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('report', 'schedule_type', 'next_run', 'format', 'active')
    list_filter = ('schedule_type', 'format', 'active')
    search_fields = ('report__name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'created_at', 'read_at')
    search_fields = ('user__username', 'notification_type', 'message')
    list_filter = ('notification_type', 'created_at', 'read_at')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'priority', 'created_at', 'expiry_date')
    search_fields = ('title', 'message')
    list_filter = ('priority', 'expiry_date')
    filter_horizontal = ('target_departments',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object_type', 'object_id', 'ip_address', 'timestamp')
    search_fields = ('user__username', 'action', 'object_type')
    list_filter = ('action', 'object_type', 'timestamp')

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'data_type', 'is_public')
    search_fields = ('key', 'description')
    list_filter = ('data_type', 'is_public')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'currency', 'language', 'tax_rate')
    search_fields = ('name', 'country')
    list_filter = ('country', 'currency')
