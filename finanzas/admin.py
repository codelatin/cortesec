# finanzas/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Ingreso, Presupuesto, ProyeccionFlujoCaja


# === Filtros personalizados ===

class IngresoVencidoFilter(admin.SimpleListFilter):
    title = '¿Está vencido?'
    parameter_name = 'vencido'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'si':
            return queryset.filter(
                estado__in=['pendiente', 'parcial'],
                fecha_esperada__lt=today
            )
        if self.value() == 'no':
            return queryset.exclude(
                estado__in=['pendiente', 'parcial'],
                fecha_esperada__lt=today
            )
        return queryset


class PresupuestoSobrepasadoFilter(admin.SimpleListFilter):
    title = '¿Sobrepresupuestado?'
    parameter_name = 'sobrepresupuestado'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Sí'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.extra(where=["monto_gastado > monto_planeado"])
        if self.value() == 'no':
            return queryset.extra(where=["monto_gastado <= monto_planeado"])
        return queryset


# === Registros en el Admin ===

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = [
        'proyecto',
        'concepto',
        'tipo_ingreso',
        'monto_total',
        'monto_recibido',
        'estado',
        'fecha_esperada',
        'fecha_recepcion',
        'esta_vencido',
        'creado_por',
    ]
    list_filter = [
        'estado',
        'tipo_ingreso',
        'metodo_pago',
        'fecha_esperada',
        'fecha_recepcion',
        'proyecto__status',
        IngresoVencidoFilter,  # ✅ Filtro personalizado
    ]
    search_fields = [
        'proyecto__name',
        'proyecto__code',
        'concepto',
        'descripcion',
        'numero_referencia',
        'creado_por__username',
        'aprobado_por__username',
    ]
    date_hierarchy = 'fecha_esperada'
    ordering = ['-fecha_esperada', '-creado_en']
    readonly_fields = ['creado_en', 'actualizado_en', 'dias_vencidos']
    autocomplete_fields = ['proyecto', 'creado_por', 'aprobado_por']

    fieldsets = (
        ('Información General', {
            'fields': ('proyecto', 'concepto', 'descripcion', 'tipo_ingreso', 'notas')
        }),
        ('Montos y Fechas', {
            'fields': ('monto_total', 'monto_recibido', 'fecha_esperada', 'fecha_recepcion')
        }),
        ('Estado y Pago', {
            'fields': ('estado', 'metodo_pago', 'relacionado_con_avance', 'porcentaje_avance')
        }),
        ('Documentación', {
            'fields': ('numero_referencia', 'cuenta_bancaria', 'documento_soporte'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'aprobado_por', 'creado_en', 'actualizado_en', 'dias_vencidos'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = [
        'proyecto',
        'categoria',
        'monto_planeado',
        'monto_comprometido',
        'monto_gastado',
        'porcentaje_uso',
        'esta_sobrepresupuestado',
    ]
    list_filter = [
        'categoria',
        'proyecto__status',
        PresupuestoSobrepasadoFilter,  # ✅ Filtro personalizado
    ]
    search_fields = [
        'proyecto__name',
        'proyecto__code',
        'subcategoria',
        'descripcion',
    ]
    ordering = ['proyecto', 'categoria']
    readonly_fields = ['creado_en', 'actualizado_en', 'porcentaje_uso', 'monto_disponible']
    autocomplete_fields = ['proyecto', 'creado_por']

    fieldsets = (
        ('Proyecto y Categoría', {
            'fields': ('proyecto', 'categoria', 'subcategoria', 'descripcion')
        }),
        ('Montos', {
            'fields': ('monto_planeado', 'monto_comprometido', 'monto_gastado', 'monto_disponible', 'porcentaje_uso')
        }),
        ('Período', {
            'fields': ('periodo_inicio', 'periodo_fin')
        }),
        ('Auditoría', {
            'fields': ('creado_por', 'creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProyeccionFlujoCaja)
class ProyeccionFlujoCajaAdmin(admin.ModelAdmin):
    list_display = [
        'proyecto',
        'mes',
        'año',
        'ingresos_proyectados',
        'ingresos_reales',
        'egresos_proyectados',
        'egresos_reales',
        'saldo_final',
        'variacion',
    ]
    list_filter = [
        'año',
        'proyecto__status',
    ]
    search_fields = [
        'proyecto__name',
        'proyecto__code',
    ]
    ordering = ['-año', '-mes', 'proyecto']
    readonly_fields = [
        'creado_en',
        'actualizado_en',
        'flujo_neto_proyectado',
        'flujo_neto_real',
        'variacion'
    ]
    autocomplete_fields = ['proyecto']

    fieldsets = (
        ('Proyecto y Período', {
            'fields': ('proyecto', 'mes', 'año')
        }),
        ('Ingresos', {
            'fields': ('ingresos_proyectados', 'ingresos_reales')
        }),
        ('Egresos', {
            'fields': ('egresos_proyectados', 'egresos_reales')
        }),
        ('Saldos y Análisis', {
            'fields': ('saldo_inicial', 'saldo_final', 'flujo_neto_proyectado', 'flujo_neto_real', 'variacion')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )