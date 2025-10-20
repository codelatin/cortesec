
# Create your models here.
# proyectos/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Project(models.Model):
    """
    Proyecto de construcción (Obra)
    """
    PROJECT_STATUS = [
        ('planning', 'En Planificación'),
        ('active', 'Activo'),
        ('on_hold', 'En Pausa'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    CONTRACT_TYPE = [
        ('fixed_price', 'Precio Fijo'),
        ('time_material', 'Tiempo y Material'),
        ('cost_plus', 'Costo Más Honorarios'),
    ]
    
    # Información básica
    name = models.CharField(max_length=200, verbose_name="Nombre del proyecto")
    description = models.TextField(blank=True, verbose_name="Descripción")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código del proyecto")
    
    # Cliente y ubicación (sin Company)
    client_name = models.CharField(max_length=200, verbose_name="Nombre del cliente")
    client_company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Empresa del cliente"
    )
    location = models.CharField(max_length=300, verbose_name="Ubicación")
    
    # Fechas
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(verbose_name="Fecha de finalización")
    actual_start_date = models.DateField(null=True, blank=True, verbose_name="Fecha real de inicio")
    actual_end_date = models.DateField(null=True, blank=True, verbose_name="Fecha real de fin")
    
    # Información financiera
    contract_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto del contrato"
    )
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE,
        default='fixed_price',
        verbose_name="Tipo de contrato"
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Presupuesto asignado"
    )
    
    # Estado y progreso
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS,
        default='planning',
        verbose_name="Estado"
    )
    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Progreso (%)"
    )
    
    # Responsables
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_projects',
        verbose_name="Gerente de proyecto"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name="Creado por"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        db_table = 'proyectos_projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def duration_days(self):
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days
        return (self.end_date - self.start_date).days
    
    @property
    def days_remaining(self):
        if self.status in ['completed', 'cancelled']:
            return 0
        remaining = (self.end_date - timezone.now().date()).days
        return max(0, remaining)


class ProjectTeam(models.Model):
    """
    Equipo de trabajo asignado a un proyecto
    """
    ROLE_CHOICES = [
        ('manager', 'Gerente'),
        ('supervisor', 'Supervisor'),
        ('engineer', 'Ingeniero'),
        ('foreman', 'Capataz'),
        ('accountant', 'Contador'),
        ('assistant', 'Asistente'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='team_members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Permisos específicos del proyecto
    can_approve_payments = models.BooleanField(default=False)
    can_manage_payroll = models.BooleanField(default=False)
    can_view_financials = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Miembro del equipo"
        verbose_name_plural = "Miembros del equipo"
        db_table = 'proyectos_project_team'
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


class Document(models.Model):
    """
    Documentos del proyecto
    """
    DOCUMENT_TYPES = [
        ('contract', 'Contrato'),
        ('blueprint', 'Plano'),
        ('permit', 'Permiso'),
        ('report', 'Reporte'),
        ('other', 'Otro'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    name = models.CharField(max_length=200, verbose_name="Nombre del documento")
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='other'
    )
    file = models.FileField(upload_to='proyectos/documents/%Y/%m/')
    description = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        db_table = 'proyectos_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.project.code}"