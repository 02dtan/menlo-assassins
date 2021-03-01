from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.timezone import template_localtime
from jinja2 import Environment


def render_field(field, classes=None):
    if classes is None:
        classes = []
    widget = field.field.widget
    attrs = widget.attrs
    attrs['autocomplete'] = 'off'
    if hasattr(field.field.widget, 'input_type'):
        if widget.input_type != 'checkbox':
            classes.append('form-control')
    attrs['class'] = ' '.join(classes)
    return field


def render_date(time, style):
    local_time = template_localtime(time)
    return date(local_time, style)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'render_field': render_field,
        'render_date': render_date
    })
    return env
