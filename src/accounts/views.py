# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView, CreateView

from accounts.forms import UserUpdateForm, UserRegistrationForm
from dataloaderinterface.forms import OrganizationForm


class UserUpdateView(UpdateView):
    form_class = UserUpdateForm
    template_name = 'registration/account.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_hydroshare_account(self):
        return self.request.user.hydroshare_account

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['hs_account'] = self.get_hydroshare_account()
        context['organization_form'] = OrganizationForm()
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(UserUpdateView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        if request.POST.get('disconnect-hydroshare-account'):
            request.user.hydroshare_account.delete()
            # odm2user = request.user.odm2user
            # hs_acct_id = odm2user.hydroshare_account.pk
            # odm2user.hydroshare_account = None
            # HydroShareAccount.objects.get(pk=hs_acct_id).delete()
            # odm2user.save()
            form = self.get_form_class()(request.POST, instance=request.user)

            context = {
                'form': form,
                'organization_form': OrganizationForm(),
                'hs_accounts': None
            }
            return render(request, self.template_name, context=context)
        else:
            # user = User.objects.get(pk=request.user.pk)
            # form = UserUpdateForm(request.POST, instance=user,
            #                       initial={'organization': user.odm2user.affiliation.organization})

            form = self.get_form_class()(request.POST, instance=request.user)

            if form.is_valid():
                form.save()
                messages.success(request, 'Your information has been updated successfully.')
                return HttpResponseRedirect(reverse('user_account'))
            else:
                messages.error(request, 'There were some errors in the form.')
                return render(request, self.template_name, {'form': form, 'organization_form': OrganizationForm()})


class UserRegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(UserRegistrationView, self).get_context_data(**kwargs)
        context['organization_form'] = OrganizationForm()
        return context

    def post(self, request, *args, **kwargs):
        response = super(UserRegistrationView, self).post(request, *args, **kwargs)
        form = self.get_form()

        if form.instance.id:
            login(request, form.instance)

        return response
