from django import template
from .component import Component
from .component_tag import make_component_tag

import typing as t


class Library(template.Library):
    def __init__(self):
        super().__init__()

    def component(self, self_closed: bool = False):
        def register_component(component: t.Type[Component]):
            component_name = component.__name__
            if self_closed:
                component_name += '/'
            self.tag(component_name, make_component_tag(component, self_closed=self_closed))
            return component
        return register_component
