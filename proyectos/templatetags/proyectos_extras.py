from django import template

register = template.Library()

@register.filter
def progress_color(value):
    """
    Devuelve un color Bootstrap según el progreso del proyecto.
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return 'secondary'  # color neutro si el valor no es válido

    if value < 30:
        return 'danger'
    elif value < 70:
        return 'warning'
    else:
        return 'success'
