from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.shortcuts import render, reverse, redirect

class Account(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'

    send_mail(
        subject=f'{User.username}',
        # имя клиента и дата записи будут в теме для удобства
        message='здраствуйте', # сообщение с кратким описанием проблемы
        from_email='Egor-Fivegor@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[]  # здесь список получателей. Например, секретарь, сам врач и т. д.
    )



@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')