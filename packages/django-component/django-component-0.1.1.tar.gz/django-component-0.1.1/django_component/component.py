from django import template
from django.forms.widgets import MediaDefiningClass
from django.template.loader import render_to_string

import typing as t


class Component(metaclass=MediaDefiningClass):
    template: str = ""
    css: t.List[str] = []
    js: t.List[str] = []

    def context(self, *args, **kwargs):
        return kwargs

    def render(self, children: str, slots: t.Dict[str, str], *args, **kwargs) -> str:
        context = self.context(*args, **kwargs)
        context.update({"children": children, "slots": slots})
        return render_to_string(self.template, context)
