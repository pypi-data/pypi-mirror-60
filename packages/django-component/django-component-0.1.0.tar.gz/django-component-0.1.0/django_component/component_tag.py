from inspect import getfullargspec, unwrap

from django import template
from django.template.library import parse_bits
from django.template.base import NodeList

from .component import Component
from .slot import SlotNode, SlotAlreadyDefinedException

import typing as t


def make_component_tag(component_cls: t.Type[Component]) -> t.Callable:
    component = component_cls()
    [_, *params], varargs, varkw, defaults, kwonly, kwonly_defaults, _ = getfullargspec(
        unwrap(component.context)
    )

    def parse_component(parser, token) -> ComponentNode:
        component_name, *bits = token.split_contents()

        args, kwargs = parse_bits(
            parser,
            bits,
            params,
            varargs,
            varkw,
            defaults,
            kwonly,
            kwonly_defaults,
            False,
            component_name,
        )

        nodelist = parser.parse((f"end_{component_name}",))
        parser.delete_first_token()

        return ComponentNode(component, nodelist, args, kwargs)

    return parse_component


class ComponentNode(template.Node):
    def __init__(
        self,
        component: Component,
        nodelist: template.NodeList,
        args: t.List,
        kwargs: t.Dict,
    ):
        self.component = component
        self.args = args
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context: t.Dict) -> str:
        self.register_media(context)
        args, kwargs = self.get_resolved_arguments(context)
        children, slots = self.get_children_and_slots(context)
        return self.component.render(children, slots, *args, **kwargs)

    def register_media(self, context):
        if "__django_component" in context:
            context["__django_component"]["media"] += self.component.media

    def get_resolved_arguments(self, context):
        resolved_args = [var.resolve(context) for var in self.args]
        resolved_kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
        return resolved_args, resolved_kwargs

    def get_children_and_slots(self, context):
        child_nodes = NodeList()
        slots = {}
        for node in self.nodelist:
            if isinstance(node, SlotNode):
                slot_name = node.name
                if slot_name in slots.keys():
                    raise SlotAlreadyDefinedException(
                        f"A slot named {slot_name} is already defined in {self.component.__class__.__name__}"
                    )
                slots[slot_name] = node.render_slot(context)
            else:
                child_nodes.append(node)
        children = child_nodes.render(context)
        return children, slots
