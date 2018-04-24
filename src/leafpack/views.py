# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render
from dataloaderinterface.models import SiteRegistration
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .models import LeafPack, Macroinvertebrate
from .forms import LeafPackForm, BugCountForm, BugCountFormFactory
from django.core.management import call_command


class LeafPackCreateView(CreateView):
    form_class = LeafPackForm
    template_name = 'leafpack/leafpack.html'
    slug_field = 'sampling_feature_code'

    def get_context_data(self, **kwargs):

        # TODO: Probably get rid of this eventually...
        if not len(Macroinvertebrate.objects.all()):
            # If there are no macroinvertebrates in the database, run 'set_leafpackdb_defaults' command to populate
            # database with default macroinvertebrate and leaf pack types.
            call_command('set_leafpackdb_defaults')

        context = super(LeafPackCreateView, self).get_context_data(**kwargs)

        context['form'] = LeafPackForm(initial={
            'site_registration': SiteRegistration.objects.get(sampling_feature_code=self.kwargs.get(self.slug_field, None))
        })

        context['bug_count_form_list'] = BugCountFormFactory.formset_factory()

        return context
