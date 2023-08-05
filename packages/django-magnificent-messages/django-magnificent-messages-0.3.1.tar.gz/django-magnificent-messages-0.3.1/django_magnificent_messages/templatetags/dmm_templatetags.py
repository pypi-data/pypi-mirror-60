from django import template
from ..messages import update_last_checked as api_update_last_checked

register = template.Library()


@register.simple_tag(takes_context=True)
def update_last_checked(context):
    request = context.get("request")
    if request:
        api_update_last_checked(request)
