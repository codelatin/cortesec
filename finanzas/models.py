from django.db import models

# Create your models here.
# finanzas/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from proyectos.models import Project


class Ingreso(models.Model):
    """
    Ingresos del proyecto (anticipos, pagos del contratante, otros ingresos)
    """
    TIPO_INGRESO = [
        ('anticipo', 'Anticipo'),
        ('pago_avance', 'Pago por Avance'),
        ('pago_final', 'Pago Final'),
        ('ingreso_adicional', 'Ingreso Adicional'),
        ('ajuste_contractual', 'Ajuste Contractual'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('recibido', 'Recibido'),
        ('parcial', 'Parcial'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO = [
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
        ('efectivo', 'Efectivo'),
        ('otro', 'Otro'),
    ]
    
    # Relación con proyecto
    proyecto = models.ForeignKey(
        'proyectos.Project',
        on_delete=models.CASCADE,
        related_name='ingresos',
        verbose_name="Proyecto"
    )
    
    # Información básica
    concepto = models.CharField(
        max_length=200,
        verbose_name="Concepto"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción detallada"
    )
    tipo_ingreso = models.CharField(
        max_length=25,
        choices=TIPO_INGRESO,
        default='pago_avance',
        verbose_name="Tipo de ingreso"
    )
    
    # Montos
    monto_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto total"
    )
    monto_recibido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto recibido"
    )
    
    # Fechas
    fecha_esperada = models.DateField(
        verbose_name="Fecha esperada"
    )
    fecha_recepcion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de recepción"
    )
    
    # Estado y método de pago
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO,
        default='pendiente',
        verbose_name="Estado"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO,
        null=True,
        blank=True,
        verbose_name="Método de pago"
    )
    
    # Documentación
    numero_referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de referencia/factura"
    )
    cuenta_bancaria = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cuenta bancaria"
    )
    documento_soporte = models.FileField(
        upload_to='finanzas/ingresos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Documento de soporte"
    )
    
    # Relación con cortes de obra (opcional)
    relacionado_con_avance = models.BooleanField(
        default=False,
        verbose_name="Relacionado con avance de obra"
    )
    porcentaje_avance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Porcentaje de avance asociado"
    )
    
    # Notas y observaciones
    notas = models.TextField(
        blank=True,
        verbose_name="Notas adicionales"
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ingresos_creados',
        verbose_name="Registrado por"
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingresos_aprobados',
        verbose_name="Aprobado por"
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        db_table = 'finanzas_ingresos'
        ordering = ['-fecha_esperada', '-creado_en']
        indexes = [
            models.Index(fields=['proyecto', 'estado']),
            models.Index(fields=['fecha_esperada']),
            models.Index(fields=['fecha_recepcion']),
        ]
    
    def __str__(self):
        return f"{self.proyecto.code} - {self.concepto} - ${self.monto_total}"
    
    @property
    def monto_pendiente(self):
        """Monto pendiente de recibir"""
        return self.monto_total - self.monto_recibido
    
    @property
    def esta_completamente_recibido(self):
        """Verifica si el ingreso está completamente recibido"""
        return self.monto_recibido >= self.monto_total
    
    @property
    def esta_vencido(self):
        """Verifica si el ingreso está vencido"""
        if self.estado == 'recibido':
            return False
        if self.fecha_esperada is None:
            return False  # o None, pero False es más seguro para el admin
        return self.fecha_esperada < timezone.now().date()
        
    @property
    def dias_vencidos(self):
        """Días de retraso"""
        if not self.esta_vencido:
            return 0
        return (timezone.now().date() - self.fecha_esperada).days
    
    def marcar_como_recibido(self, monto=None, fecha=None, metodo_pago=None):
        """Marca el ingreso como recibido"""
        self.monto_recibido = monto or self.monto_total
        self.fecha_recepcion = fecha or timezone.now().date()
        
        if metodo_pago:
            self.metodo_pago = metodo_pago
        
        if self.esta_completamente_recibido:
            self.estado = 'recibido'
        elif self.monto_recibido > 0:
            self.estado = 'parcial'
        
        self.save()


class Presupuesto(models.Model):
    """
    Presupuesto detallado del proyecto por categorías
    """
    CATEGORIA_PRESUPUESTO = [
        ('materiales', 'Materiales'),
        ('mano_obra', 'Mano de Obra'),
        ('equipo', 'Equipo y Maquinaria'),
        ('subcontratos', 'Subcontratos'),
        ('administrativos', 'Gastos Administrativos'),
        ('indirectos', 'Costos Indirectos'),
        ('contingencia', 'Contingencia'),
        ('otros', 'Otros'),
    ]
    
    proyecto = models.ForeignKey(
        'proyectos.Project',
        on_delete=models.CASCADE,
        related_name='presupuestos',
        verbose_name="Proyecto"
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_PRESUPUESTO,
        verbose_name="Categoría"
    )
    subcategoria = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Subcategoría"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    # Montos
    monto_planeado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto planeado"
    )
    monto_comprometido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto comprometido"
    )
    monto_gastado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto gastado"
    )
    
    # Período
    periodo_inicio = models.DateField(verbose_name="Inicio del período")
    periodo_fin = models.DateField(verbose_name="Fin del período")
    
    # Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='presupuestos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        db_table = 'finanzas_presupuestos'
        ordering = ['categoria', 'periodo_inicio']
        indexes = [
            models.Index(fields=['proyecto', 'categoria']),
        ]
    
    def __str__(self):
        return f"{self.proyecto.code} - {self.get_categoria_display()}"
    
    @property
    def monto_disponible(self):
        planeado = self.monto_planeado or Decimal('0.00')
        comprometido = self.monto_comprometido or Decimal('0.00')
        gastado = self.monto_gastado or Decimal('0.00')
        return planeado - comprometido - gastado
    
    @property
    def porcentaje_uso(self):
        """Porcentaje de uso del presupuesto"""
        if not self.monto_planeado or self.monto_planeado == 0:
            return Decimal('0.00')
        gastado = self.monto_gastado or 0
        return (gastado / self.monto_planeado) * 100
        
    @property
    def esta_sobrepresupuestado(self):
        """Verifica si está sobre presupuesto"""
        return self.monto_gastado > self.monto_planeado


class ProyeccionFlujoCaja(models.Model):
    """
    Proyección de flujo de caja mensual
    """
    proyecto = models.ForeignKey(
        'proyectos.Project',
        on_delete=models.CASCADE,
        related_name='proyecciones_flujo_caja',
        verbose_name="Proyecto"
    )
    
    # Período
    mes = models.IntegerField(
        validators=[MinValueValidator(1), MinValueValidator(12)],
        verbose_name="Mes"
    )
    año = models.IntegerField(verbose_name="Año")
    
    # Proyecciones
    ingresos_proyectados = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Ingresos proyectados"
    )
    egresos_proyectados = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Egresos proyectados"
    )
    
    # Valores reales
    ingresos_reales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Ingresos reales"
    )
    egresos_reales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Egresos reales"
    )
    
    # Saldos
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo inicial"
    )
    saldo_final = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Saldo final"
    )
    
    notas = models.TextField(blank=True, verbose_name="Notas")
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proyección de Flujo de Caja"
        verbose_name_plural = "Proyecciones de Flujo de Caja"
        db_table = 'finanzas_proyecciones_flujo_caja'
        unique_together = ['proyecto', 'mes', 'año']
        ordering = ['año', 'mes']
    
    def __str__(self):
        return f"{self.proyecto.code} - {self.mes}/{self.año}"
    
    @property
    def flujo_neto_proyectado(self):
        """Flujo neto proyectado"""
        return self.ingresos_proyectados - self.egresos_proyectados
    
    @property
    def flujo_neto_real(self):
        """Flujo neto real"""
        return self.ingresos_reales - self.egresos_reales
    
    @property
    def variacion(self):
        """Variación entre proyectado y real"""
        return self.flujo_neto_real - self.flujo_neto_proyectado


class Egreso(models.Model):
    """
    Egresos del proyecto (materiales, mano de obra, subcontratos, gastos administrativos)
    """
    TIPO_EGRESO = [
        ('material', 'Material'),
        ('mano_obra', 'Mano de Obra'),
        ('subcontrato', 'Subcontrato'),
        ('equipo', 'Equipo y Maquinaria'),
        ('administrativo', 'Gasto Administrativo'),
        ('servicio', 'Servicio'),
        ('transporte', 'Transporte'),
        ('impuesto', 'Impuesto'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('parcial', 'Parcial'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO = [
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de Crédito'),
        ('otro', 'Otro'),
    ]
    
    # Relación con proyecto
    proyecto = models.ForeignKey(
        'proyectos.Project',
        on_delete=models.CASCADE,
        related_name='egresos',
        verbose_name="Proyecto"
    )
    
    # Relación opcional con presupuesto
    presupuesto = models.ForeignKey(
        'Presupuesto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='egresos',
        verbose_name="Presupuesto asociado"
    )
    
    # Información básica
    concepto = models.CharField(
        max_length=200,
        verbose_name="Concepto"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción detallada"
    )
    tipo_egreso = models.CharField(
        max_length=20,
        choices=TIPO_EGRESO,
        verbose_name="Tipo de egreso"
    )
    
    # Proveedor/Beneficiario
    proveedor = models.CharField(
        max_length=200,
        verbose_name="Proveedor/Beneficiario"
    )
    nit_proveedor = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="NIT/RUT del proveedor"
    )
    
    # Montos
    monto_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto total"
    )
    monto_pagado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto pagado"
    )
    
    # Fechas
    fecha_emision = models.DateField(
        verbose_name="Fecha de emisión"
    )
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de vencimiento"
    )
    fecha_pago = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de pago"
    )
    
    # Estado y método de pago
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO,
        default='pendiente',
        verbose_name="Estado"
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO,
        null=True,
        blank=True,
        verbose_name="Método de pago"
    )
    
    # Documentación
    numero_factura = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de factura"
    )
    numero_orden_compra = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de orden de compra"
    )
    cuenta_bancaria = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cuenta bancaria destino"
    )
    documento_soporte = models.FileField(
        upload_to='finanzas/egresos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Documento de soporte"
    )
    
    # Retenciones e impuestos
    retencion_iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Retención IVA"
    )
    retencion_fuente = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Retención en la fuente"
    )
    
    # Notas y observaciones
    notas = models.TextField(
        blank=True,
        verbose_name="Notas adicionales"
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='egresos_creados',
        verbose_name="Registrado por"
    )
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='egresos_aprobados',
        verbose_name="Aprobado por"
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Egreso"
        verbose_name_plural = "Egresos"
        db_table = 'finanzas_egresos'
        ordering = ['-fecha_vencimiento', '-creado_en']
        indexes = [
            models.Index(fields=['proyecto', 'estado']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['fecha_pago']),
            models.Index(fields=['tipo_egreso']),
            models.Index(fields=['proveedor']),
        ]
    
    def __str__(self):
        return f"{self.proyecto.code} - {self.concepto} - ${self.monto_total}"
    
    @property
    def monto_pendiente(self):
        """Monto pendiente de pagar"""
        return self.monto_total - self.monto_pagado
    
    @property
    def monto_neto_pagar(self):
        """Monto neto a pagar (después de retenciones)"""
        return self.monto_total - self.retencion_iva - self.retencion_fuente
    
    @property
    def esta_completamente_pagado(self):
        """Verifica si el egreso está completamente pagado"""
        return self.monto_pagado >= self.monto_total
    
    @property
    def esta_vencido(self):
        """Verifica si el egreso está vencido"""
        if self.estado == 'pagado':
            return False
        if self.fecha_vencimiento is None:
            return False
        return self.fecha_vencimiento < timezone.now().date()
    
    @property
    def dias_vencidos(self):
        """Días de retraso en el pago"""
        if not self.esta_vencido:
            return 0
        return (timezone.now().date() - self.fecha_vencimiento).days
    
    def marcar_como_pagado(self, monto=None, fecha=None, metodo_pago=None):
        """Marca el egreso como pagado"""
        self.monto_pagado = monto or self.monto_total
        self.fecha_pago = fecha or timezone.now().date()
        
        if metodo_pago:
            self.metodo_pago = metodo_pago
        
        if self.esta_completamente_pagado:
            self.estado = 'pagado'
        elif self.monto_pagado > 0:
            self.estado = 'parcial'
        
        # Actualizar presupuesto si está asociado
        if self.presupuesto:
            self.presupuesto.monto_gastado += (monto or self.monto_total) - (self.monto_pagado - (monto or self.monto_total))
            self.presupuesto.save()
        
        self.save()