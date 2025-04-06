from django.views import generic
from .form import CadastroForm, LoginForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from json import loads
from django.contrib.auth import login

class CadastroView(generic.CreateView):
    model = User
    form_class = CadastroForm
    template_name = 'cadastro.html'

    def get_success_url(self):
        messages.success(self.request, 'Usuário criado com sucesso.')
        return reverse('login')

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro_msg = valor['message']
                else:
                    erro_msg = f'Forneça um dado valido para o campo {k}.'
        
        if erro_msg:
            messages.error(self.request, erro_msg)
        return super().form_invalid(form)

class LoginView(generic.FormView):
    model = User
    form_class = LoginForm
    template_name = 'login.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Login realizado com sucesso.')
        return reverse('mentorados')

    def form_valid(self, form):
        print(form.user)
        login(self.request, form.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro_msg = valor['message']
                else:
                    erro_msg = f'Forneça um dado valido para o campo {k}.'
        
        if erro_msg:
            messages.error(self.request, erro_msg)
        return super().form_invalid(form)