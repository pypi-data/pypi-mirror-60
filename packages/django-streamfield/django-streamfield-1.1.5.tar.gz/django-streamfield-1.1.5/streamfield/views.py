# -*- coding: utf-8 -*-
from django.template import loader
from django.views.generic import DetailView, TemplateView
from .forms import get_form_class

def admin_instance_class(model, base=DetailView):

    tmpl = loader.select_template([
        'streamblocks/admin/%s.html' % model.__name__.lower(),
        'streamfield/admin/change_form_render_template.html'
        ])

    # will be removed in future. use above approach to override admin template.
    if hasattr(model, 'custom_admin_template'):
        tmpl_name = model.custom_admin_template
        import warnings
        warnings.warn(
            "'custom_admin_template' will be removed in future. "
            "Use override admin template approach instead", 
            DeprecationWarning, stacklevel=2)
    else:
        tmpl_name = tmpl.template.name
        
    def get_context_data(self, **kwargs):
        context = base.get_context_data(self, **kwargs)
        
        # forms
        obj = super(self.__class__, self).get_object()
        context['form'] = get_form_class(model)(instance=obj)

        return context

    attrs = dict(
        model = model,
        template_name = tmpl_name,
        get_context_data = get_context_data
        )

    return type(str(model.__name__ + 'DetailView'), (base, ), attrs )
