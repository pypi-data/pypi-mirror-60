from django import template


class IllegalSlotParentException(Exception):
    pass


class SlotAlreadyDefinedException(Exception):
    pass


def slot(parser, token):
    [slot_name] = token.split_contents()[1:]
    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return SlotNode(slot_name, nodelist)


class SlotNode(template.Node):
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render_slot(self, context):
        output = self.nodelist.render(context)
        return output

    def render(self, context):
        raise IllegalSlotParentException(
            "A slot can only appear as a direct child of a component"
        )
