from django import template

'''@register.filter
def model_type(value):
    return type(value).__name__
    '''

register = template.Library()

@register.simple_tag(takes_context=True)
def get_poster_display(context, user):
    if context['user'] == user:
        return 'Vous avez'
    return f'{user.username} a '