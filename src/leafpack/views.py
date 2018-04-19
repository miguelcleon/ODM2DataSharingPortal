# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render
from dataloaderinterface.models import SiteRegistration
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .models import LeafPack
from .forms import LeafPackForm, BugCountForm, bugCountFormSetFactory


class LeafPackCreateView(CreateView):
    form_class = LeafPackForm
    template_name = 'leafpack/leafpack.html'
    slug_field = 'site_registration'

    def get_context_data(self, **kwargs):
        context = super(LeafPackCreateView, self).get_context_data(**kwargs)

        context['form'] = LeafPackForm(initial={
            'site_registration': SiteRegistration.objects.get(registration_token=self.kwargs.get(self.slug_field, None))
        })

        # context['bug_count_form'] = bugCountFormSetFactory()
        bug_count_form = bugCountFormSetFactory()
        context['bug_count_form'] = bug_count_form

        return context
