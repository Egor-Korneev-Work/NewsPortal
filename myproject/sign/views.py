from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.shortcuts import render, reverse, redirect
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from .models import BasicSignupForm


class Account(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context

class BaseRegisterView(CreateView):
    model = User
    form_class = BasicSignupForm
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        send_mail(
            subject=f'Добро пожаловать, {user.first_name}!',
            message='Приветствуем вас на нашем сервисе.',
            from_email='Egor-Fivegor@yandex.ru',
            recipient_list=[user.email],
        )
        return response

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')