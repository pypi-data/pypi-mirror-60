from django import template
from .component import Component
from .component_tag import make_component_tag

import typing as t


class Library(template.Library):
    def __init__(self):
        super().__init__()

    def component(self, component: t.Type[Component]):
        self.tag(component.__name__, make_component_tag(component))

    # TODO Wrap inclusion_tag to forward context['__django_component'] anyway
