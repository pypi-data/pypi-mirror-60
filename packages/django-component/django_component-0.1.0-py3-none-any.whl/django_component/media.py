from django import template
from django.forms.widgets import Media
from django.utils.safestring import mark_safe

from secrets import token_hex

CSS_TAG = "<__django_component__CSS__{media_secret}>"
JS_TAG = "<__django_component__JS__{media_secret}>"


class MissingUseComponentMediaException(Exception):
    pass


def media_registry(parser, token):
    nodelist = parser.parse()

    return MediaRegistryNode(nodelist)


def css(context):
    if not "__django_component" in context:
        raise MissingUseComponentMediaException(
            "'components_css' can only appear after 'use_components'"
        )
    return mark_safe(
        CSS_TAG.format(media_secret=context["__django_component"]["secret"])
    )


def js(context):
    if not "__django_component" in context:
        raise MissingUseComponentMediaException(
            "'components_js' can only appear after 'use_components'"
        )
    return mark_safe(
        JS_TAG.format(media_secret=context["__django_component"]["secret"])
    )


class MediaRegistryNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # A new secret is generated for each rendering, preventing a user to inject CSS_TAG or JS_TAG
        media_secret = token_hex()
        context["__django_component"] = {"media": Media(), "secret": media_secret}
        # Render all child nodes
        rendered = self.nodelist.render(context)
        # Replace django components media tags with the actual dependencies
        rendered = self.replace_media_tags(
            rendered, media_secret, context["__django_component"]["media"]
        )
        # TODO Add warning in case there is any media tag look alike left, we don't wan't to raise an exception because:
        # 1) A media_secret can't be reused once the rendering is done
        # 2) A user could inject a fake media tag to trigger the exception
        return rendered

    def replace_media_tags(self, rendered, media_secret, media):
        rendered = rendered.replace(
            CSS_TAG.format(media_secret=media_secret), "\n".join(media.render_css())
        )
        rendered = rendered.replace(
            JS_TAG.format(media_secret=media_secret), "\n".join(media.render_js())
        )
        return rendered
