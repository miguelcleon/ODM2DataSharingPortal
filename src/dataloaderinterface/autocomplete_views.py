from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from django import http
from django.utils import six
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView, ModelFormMixin
from django.views.generic.list import ListView

from dataloader.models import Method, Affiliation


class MethodAutocomplete(autocomplete.Select2QuerySetView):
    model = Method

    def get_queryset(self):
        queryset = Method.objects.all()
        queryset = queryset.filter(method_name__istartswith=self.q) if self.q else queryset
        return queryset

    def post(self, request):
        organization_name = request.POST['text']
        # organization_type = OrganizationType.objects.get(pk='Research organization')
        # organization = Organization.objects.get_or_create(
        #     organization_name=organization_name,
        #     organization_code=organization_name,
        #     organization_type=organization_type
        # )

        return http.JsonResponse({
            # 'id': organization[0].pk,
            'text': six.text_type(organization_name),
        })


class AffiliationAutocomplete(autocomplete.Select2QuerySetView):
    model = Affiliation

    def get_queryset(self):
        queryset = Affiliation.objects.all()
        queryset = queryset.filter(
            Q(person__person_first_name__contains=self.q) |
            Q(person__person_last_name__contains=self.q) |
            Q(organization__organization_name__contains=self.q)
        ) if self.q else queryset

        return queryset
