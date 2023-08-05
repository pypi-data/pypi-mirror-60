from django.template import Library
from .slot import slot
from .media import media_registry, css, js

register = Library()

register.tag("slot", slot)
register.tag("use_components", media_registry)
register.simple_tag(css, name="components_css", takes_context=True)
register.simple_tag(js, name="components_js", takes_context=True)
