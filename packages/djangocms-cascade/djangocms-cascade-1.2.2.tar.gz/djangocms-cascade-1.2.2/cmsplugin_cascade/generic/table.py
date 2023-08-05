from django.forms import widgets, CharField, ChoiceField
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase


class SimpleTablePlugin(EntangledModelFormMixin):
    caption = CharField(
        label=_("Table caption"),
        widget=widgets.TextInput(attrs={'style': 'width: 100%; padding-right: 0; font-weight: bold; font-size: 125%;'}),
    )

    class Meta:
        entangled_fields = {'glossary': ['tag_type', 'content']}


class SimpleTablePlugin(CascadePluginBase):
    name = _("Image in text")
    ring_plugin = 'SimpleTablePlugin'
    render_template = 'cascade/plugins/textimage.html'
    parent_classes = ['TextPlugin']
    allow_children = False
    require_parent = False
    form = SimpleTableFormMixin

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/simpletableplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        """
        Workaround for `PluginPool.get_all_plugins()`, otherwise TextImagePlugin is not allowed
        as a child of a `TextPlugin`.
        """
        return False

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(TextImagePlugin, cls).get_inline_styles(instance)
        alignement = instance.glossary.get('alignement')
        if alignement:
            inline_styles['float'] = alignement
        return inline_styles

    def render(self, context, instance, placeholder):
        context = self.super(TextImagePlugin, self).render(context, instance, placeholder)
        try:
            aspect_ratio = compute_aspect_ratio(instance.image)
        except Exception:
            # if accessing the image file fails, abort here
            return context
        resize_options = instance.glossary.get('resize_options', {})
        crop = 'crop' in resize_options
        upscale = 'upscale' in resize_options
        subject_location = instance.image.subject_location if 'subject_location' in resize_options else False
        high_resolution = 'high_resolution' in resize_options
        image_width = instance.glossary.get('image_width', '')
        if not image_width.endswith('px'):
            return context
        image_width = int(image_width.rstrip('px'))
        image_height = instance.glossary.get('image_height', '')
        if image_height.endswith('px'):
            image_height = int(image_height.rstrip('px'))
        else:
            image_height = int(round(image_width * aspect_ratio))
        context['src'] = {
            'size': (image_width, image_height),
            'size2x': (image_width * 2, image_height * 2),
            'crop': crop,
            'upscale': upscale,
            'subject_location': subject_location,
            'high_resolution': high_resolution,
        }
        link_attributes = LinkPluginBase.get_html_tag_attributes(instance)
        context['link_html_tag_attributes'] = format_html_join(' ', '{0}="{1}"',
            [(attr, val) for attr, val in link_attributes.items() if val]
        )
        return context

plugin_pool.register_plugin(TextImagePlugin)
