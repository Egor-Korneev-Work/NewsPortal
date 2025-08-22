from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='censor')
def censor(value):
    bad_words = ['слово1', 'слово2', 'слово3']

    for word in bad_words:
        value = value.replace(word, '*' * len(word))

    return mark_safe(value)