# finanzas/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import Ingreso


class IngresoForm(forms.ModelForm):
    """
    Formulario para crear y editar ingresos
    """
    
    class Meta:
        model = Ingreso
        fields = [
            'proyecto',
            'concepto',
            'descripcion',
            'tipo_ingreso',
            'monto_total',
            'monto_recibido',
            'fecha_esperada',
            'fecha_recepcion',
            'estado',
            'metodo_pago',
            'numero_referencia',
            'cuenta_bancaria',
            'documento_soporte',
            'relacionado_con_avance',
            'porcentaje_avance',
            'notas',
        ]
        
        widgets = {
            'proyecto': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'concepto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pago de Avance - Corte Mayo 2024',
                'maxlength': 200,
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada del ingreso...',
                'rows': 3,
            }),
            'tipo_ingreso': forms.Select(attrs={
                'class': 'form-control',
            }),
            'monto_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'monto_recibido': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'fecha_esperada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_recepcion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control',
            }),
            'numero_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: FAC-2024-001',
                'maxlength': 100,
            }),
            'cuenta_bancaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bancolombia - Cta. Ahorros 123456789',
                'maxlength': 100,
            }),
            'documento_soporte': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            }),
            'relacionado_con_avance': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'porcentaje_avance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'max': '100',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas adicionales u observaciones...',
                'rows': 3,
            }),
        }
        
        labels = {
            'proyecto': 'Proyecto *',
            'concepto': 'Concepto *',
            'descripcion': 'Descripción',
            'tipo_ingreso': 'Tipo de Ingreso *',
            'monto_total': 'Monto Total ($) *',
            'monto_recibido': 'Monto Recibido ($)',
            'fecha_esperada': 'Fecha Esperada *',
            'fecha_recepcion': 'Fecha de Recepción',
            'estado': 'Estado *',
            'metodo_pago': 'Método de Pago',
            'numero_referencia': 'Número de Referencia/Factura',
            'cuenta_bancaria': 'Cuenta Bancaria',
            'documento_soporte': 'Documento de Soporte',
            'relacionado_con_avance': '¿Relacionado con avance de obra?',
            'porcentaje_avance': 'Porcentaje de Avance (%)',
            'notas': 'Notas Adicionales',
        }
        
        help_texts = {
            'monto_recibido': 'Dejar en 0 si aún no se ha recibido el pago',
            'fecha_recepcion': 'Solo llenar cuando se reciba el pago',
            'porcentaje_avance': 'Solo aplica si está relacionado con avance de obra',
            'documento_soporte': 'Formatos permitidos: PDF, JPG, PNG, DOC, DOCX',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hacer que algunos campos sean opcionales en creación
        if not self.instance.pk:
            self.fields['monto_recibido'].initial = 0
            self.fields['estado'].initial = 'pendiente'
        
        # Si el usuario tiene proyectos específicos, filtrar
        if self.user and hasattr(self.user, 'project_assignments'):
            self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(
                team_members__user=self.user,
                team_members__is_active=True
            ).distinct()
    
    def clean_monto_total(self):
        """Validar que el monto total sea positivo"""
        monto = self.cleaned_data.get('monto_total')
        if monto is not None and monto <= 0:
            raise ValidationError('El monto total debe ser mayor a 0')
        return monto
    
    def clean_monto_recibido(self):
        """Validar que el monto recibido no sea mayor al total"""
        monto_recibido = self.cleaned_data.get('monto_recibido')
        monto_total = self.cleaned_data.get('monto_total')
        
        if monto_recibido is not None and monto_recibido < 0:
            raise ValidationError('El monto recibido no puede ser negativo')
        
        if monto_total and monto_recibido and monto_recibido > monto_total:
            raise ValidationError(
                f'El monto recibido (${monto_recibido}) no puede ser mayor '
                f'al monto total (${monto_total})'
            )
        
        return monto_recibido
    
    def clean_fecha_recepcion(self):
        """Validar fecha de recepción"""
        fecha_recepcion = self.cleaned_data.get('fecha_recepcion')
        fecha_esperada = self.cleaned_data.get('fecha_esperada')
        estado = self.cleaned_data.get('estado')
        
        # Si el estado es recibido o parcial, debe tener fecha de recepción
        if estado in ['recibido', 'parcial'] and not fecha_recepcion:
            raise ValidationError(
                'Debe especificar la fecha de recepción cuando el estado es "Recibido" o "Parcial"'
            )
        
        # La fecha de recepción no puede ser anterior a la fecha esperada
        if fecha_recepcion and fecha_esperada and fecha_recepcion < fecha_esperada:
            # Esto es solo una advertencia, no un error crítico
            pass  # Puedes agregar un warning si lo deseas
        
        return fecha_recepcion
    
    def clean_porcentaje_avance(self):
        """Validar porcentaje de avance"""
        porcentaje = self.cleaned_data.get('porcentaje_avance')
        relacionado = self.cleaned_data.get('relacionado_con_avance')
        
        if relacionado and not porcentaje:
            raise ValidationError(
                'Debe especificar el porcentaje de avance cuando está relacionado con avance de obra'
            )
        
        if porcentaje is not None:
            if porcentaje < 0 or porcentaje > 100:
                raise ValidationError('El porcentaje debe estar entre 0 y 100')
        
        return porcentaje
    
    def clean_metodo_pago(self):
        """Validar método de pago"""
        metodo = self.cleaned_data.get('metodo_pago')
        estado = self.cleaned_data.get('estado')
        
        # Si está recibido, debe tener método de pago
        if estado == 'recibido' and not metodo:
            raise ValidationError(
                'Debe especificar el método de pago cuando el estado es "Recibido"'
            )
        
        return metodo
    
    def clean(self):
        """Validaciones generales del formulario"""
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        monto_recibido = cleaned_data.get('monto_recibido', 0)
        monto_total = cleaned_data.get('monto_total', 0)
        
        # Validar consistencia entre estado y montos
        if estado == 'recibido' and monto_recibido < monto_total:
            raise ValidationError(
                'El estado no puede ser "Recibido" si el monto recibido es menor al total. '
                'Use "Parcial" en su lugar.'
            )
        
        if estado == 'parcial' and (monto_recibido == 0 or monto_recibido >= monto_total):
            raise ValidationError(
                'El estado "Parcial" requiere que el monto recibido sea mayor a 0 '
                'y menor al monto total.'
            )
        
        if estado == 'pendiente' and monto_recibido > 0:
            raise ValidationError(
                'El estado no puede ser "Pendiente" si ya se recibió algún monto. '
                'Use "Parcial" en su lugar.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Guardar el ingreso y asignar el usuario que lo creó"""
        ingreso = super().save(commit=False)
        
        # Asignar el usuario que crea el registro
        if not ingreso.pk and self.user:
            ingreso.creado_por = self.user
        
        if commit:
            ingreso.save()
        
        return ingreso


class IngresoRecepcionForm(forms.ModelForm):
    """
    Formulario simplificado para marcar un ingreso como recibido
    """
    
    class Meta:
        model = Ingreso
        fields = [
            'monto_recibido',
            'fecha_recepcion',
            'metodo_pago',
            'numero_referencia',
            'cuenta_bancaria',
            'documento_soporte',
            'notas',
        ]
        
        widgets = {
            'monto_recibido': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'fecha_recepcion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'numero_referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de transacción/referencia',
            }),
            'cuenta_bancaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cuenta donde se recibió el pago',
            }),
            'documento_soporte': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre el pago recibido...',
            }),
        }
        
        labels = {
            'monto_recibido': 'Monto Recibido ($) *',
            'fecha_recepcion': 'Fecha de Recepción *',
            'metodo_pago': 'Método de Pago *',
            'numero_referencia': 'Número de Referencia',
            'cuenta_bancaria': 'Cuenta Bancaria',
            'documento_soporte': 'Comprobante de Pago',
            'notas': 'Notas',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer valores por defecto
        if not self.instance.fecha_recepcion:
            self.fields['fecha_recepcion'].initial = timezone.now().date()
        
        # Mostrar el monto pendiente como sugerencia
        if self.instance.pk:
            monto_pendiente = self.instance.monto_pendiente
            self.fields['monto_recibido'].help_text = (
                f'Monto pendiente: ${monto_pendiente:,.2f}'
            )
    
    def clean_monto_recibido(self):
        """Validar que el monto no exceda el pendiente"""
        monto_nuevo = self.cleaned_data.get('monto_recibido')
        if not monto_nuevo:
            raise ValidationError('Debe ingresar el monto recibido')
        
        if self.instance.pk:
            # Calcular el total que se habría recibido
            total_recibido = self.instance.monto_recibido + monto_nuevo
            
            if total_recibido > self.instance.monto_total:
                raise ValidationError(
                    f'El monto ingresado (${monto_nuevo:,.2f}) excede el monto pendiente '
                    f'(${self.instance.monto_pendiente:,.2f}). '
                    f'Ya se han recibido ${self.instance.monto_recibido:,.2f} de '
                    f'${self.instance.monto_total:,.2f}'
                )
        
        return monto_nuevo
    
    def save(self, commit=True):
        """Guardar y actualizar el estado automáticamente"""
        ingreso = super().save(commit=False)
        
        # Actualizar el monto recibido acumulado
        if self.instance.pk:
            monto_nuevo = self.cleaned_data.get('monto_recibido')
            ingreso.monto_recibido = self.instance.monto_recibido + monto_nuevo
        
        # Actualizar el estado basado en el monto
        if ingreso.esta_completamente_recibido:
            ingreso.estado = 'recibido'
        elif ingreso.monto_recibido > 0:
            ingreso.estado = 'parcial'
        
        # Asignar quien aprobó
        if self.user:
            ingreso.aprobado_por = self.user
        
        if commit:
            ingreso.save()
        
        return ingreso


class IngresoFilterForm(forms.Form):
    """
    Formulario para filtrar ingresos
    """
    proyecto = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todos los proyectos",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tipo_ingreso = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Ingreso.TIPO_INGRESO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Ingreso.ESTADO_PAGO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Desde'
        }),
        label='Fecha desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Hasta'
        }),
        label='Fecha hasta'
    )
    
    solo_vencidos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo mostrar vencidos'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar queryset de proyectos
        from proyectos.models import Project
        if user and hasattr(user, 'project_assignments'):
            self.fields['proyecto'].queryset = Project.objects.filter(
                team_members__user=user,
                team_members__is_active=True
            ).distinct()
        else:
            self.fields['proyecto'].queryset = Project.objects.all()