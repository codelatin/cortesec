# proyectos/forms.py
from django import forms
from django.conf import settings
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description', 'location',
            'client_name', 'client_company',
            'start_date', 'end_date',
            'contract_amount', 'contract_type', 'budget',
            'status', 'progress', 'project_manager'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la obra'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único (ej: OB-001)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción breve de la obra'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección o ubicación'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'client_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empresa del cliente (opcional)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': '0-100'
            }),
            'contract_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'project_manager': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar project_manager para que solo muestre usuarios activos
        if hasattr(settings, 'AUTH_USER_MODEL'):
            self.fields['project_manager'].queryset = (
                self.fields['project_manager'].queryset.filter(is_active=True)
            )
            
        # Si es una nueva obra, establecer created_by automáticamente (no se muestra en el formulario)
        if user and not self.instance.pk:
            self.instance.created_by = user

    def clean_code(self):
        """Validar que el código sea único (case-insensitive)"""
        code = self.cleaned_data['code']
        if Project.objects.filter(code__iexact=code).exists():
            if not self.instance.pk:  # Solo para nuevos
                raise forms.ValidationError("Ya existe una obra con este código.")
        return code

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("La fecha de finalización no puede ser anterior a la de inicio.")
        
        return cleaned_data