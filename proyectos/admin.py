from django.contrib import admin
from django.utils.html import format_html
from django.utils.formats import number_format
from .models import Project, ProjectTeam, Document

# Función auxiliar para formatear pesos colombianos
def format_cop(value):
    """Formatea un número como pesos colombianos: $1.250.000"""
    try:
        num = float(value)
        # Formato sin decimales (los contratos suelen ser en miles)
        formatted = number_format(num, decimal_pos=0, use_l10n=True, force_grouping=True)
        return f"${formatted}"
    except (TypeError, ValueError):
        return "$0"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
        'client_name',
        'client_company',
        'status',
        'status_badge',
        'contract_amount_colored',
        'budget_colored',
        'progress',
        'progress_bar',
        'days_remaining_display',
        'project_manager',
        'created_by',
        'start_date',
        'end_date'
    ]
    
    search_fields = [
        'code',
        'name',
        'client_name',
        'client_company',
        'description'
    ]
    
    list_filter = [
        'status',
        'contract_type',
        'start_date',
        'end_date',
        'created_by',
        'project_manager'
    ]
    
    list_editable = ['status', 'progress']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'description', 'location')
        }),
        ('Cliente', {
            'fields': ('client_name', 'client_company')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Finanzas', {
            'fields': ('contract_amount', 'contract_type', 'budget')
        }),
        ('Gestión', {
            'fields': ('status', 'progress', 'project_manager', 'created_by')
        }),
    )
    
    readonly_fields = ['created_by']
    ordering = ['-created_at']
    list_per_page = 20

    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'planning': 'info',
            'on_hold': 'warning',
            'completed': 'secondary',
            'cancelled': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'

    def contract_amount_colored(self, obj):
        """Monto del contrato en pesos colombianos"""
        return format_html('<strong>{}</strong>', format_cop(obj.contract_amount))
    contract_amount_colored.short_description = 'Monto Contrato'
    contract_amount_colored.admin_order_field = 'contract_amount'

    def budget_colored(self, obj):
        """Presupuesto en pesos colombianos"""
        return format_html('<span class="text-primary">{}</span>', format_cop(obj.budget))
    budget_colored.short_description = 'Presupuesto'
    budget_colored.admin_order_field = 'budget'

    def progress_bar(self, obj):
        """Barra de progreso visual"""
        try:
            progress = float(obj.progress)
            width = min(100, max(0, progress))
            color = 'success' if width >= 80 else 'warning' if width >= 50 else 'danger'
            return format_html(
                '''
                <div class="progress progress-sm" style="height: 8px;">
                    <div class="progress-bar bg-{}" role="progressbar" style="width: {}%"></div>
                </div>
                <small>{}%</small>
                ''',
                color,
                width,
                int(width)
            )
        except (TypeError, ValueError):
            return "0%"
    progress_bar.short_description = 'Progreso'

    def days_remaining_display(self, obj):
        """Días restantes con alertas"""
        try:
            days = obj.days_remaining
            if days <= 0 and obj.status == 'active':
                return format_html('<span class="text-danger font-weight-bold">Vencido</span>')
            elif days <= 7 and obj.status == 'active':
                return format_html('<span class="text-warning font-weight-bold">{} días</span>', days)
            else:
                return f"{days} días" if days > 0 else "Finalizado"
        except (TypeError, ValueError):
            return "–"
    days_remaining_display.short_description = 'Días Restantes'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectTeam)
class ProjectTeamAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'project',
        'role',
        'is_active',
        'can_approve_payments',
        'can_manage_payroll',
        'can_view_financials',
        'start_date',
        'end_date'
    ]
    
    list_filter = [
        'role',
        'is_active',
        'project',
        'start_date'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'project__name',
        'project__code'
    ]
    
    list_editable = ['is_active', 'role']
    autocomplete_fields = ['user', 'project']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'document_type_badge',
        'project',
        'file_link',
        'uploaded_by',
        'uploaded_at'
    ]
    
    list_filter = [
        'document_type',
        'project',
        'uploaded_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'project__name',
        'project__code'
    ]
    
    readonly_fields = ['uploaded_by', 'uploaded_at']

    def document_type_badge(self, obj):
        colors = {
            'contract': 'primary',
            'blueprint': 'info',
            'permit': 'warning',
            'report': 'success',
            'other': 'secondary', 
        }
        color = colors.get(obj.document_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_document_type_display()
        )
    document_type_badge.short_description = 'Tipo'

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank" class="btn btn-xs btn-default">Ver</a>', obj.file.url)
        return "Sin archivo"
    file_link.short_description = 'Archivo'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)