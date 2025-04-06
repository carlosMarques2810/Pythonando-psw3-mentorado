from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Mentorados, Estagios, DisponibilidadeHorarios, Reuniao, Tarefa, Upload
from .forms import MentoradosCadastroForm, DisponibilidadeHorarioForm, AuthMentoradoForm, ReuniaoForm, TarefaForm, UploadsForm
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from .auth import valida_token
from json import loads
from datetime import datetime
from django.utils.timezone import timedelta
from django.http import Http404
from django.utils.decorators import method_decorator

class MentoradosView(LoginRequiredMixin, generic.CreateView):
    model = Mentorados
    form_class = MentoradosCadastroForm
    template_name = 'mentorados.html'

    def get_success_url(self):
        messages.add_message(self.request, messages.constants.SUCCESS, 'Mentorado cadastrado com sucesso.')
        return reverse('mentorados')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        # Contexto mentorados
        mentorados = Mentorados.objects.filter(user=self.request.user)
        context = super().get_context_data(**kwargs)
        context['mentorados'] = mentorados

        # Contexto estágio
        estagios = [estagio[1] for estagio in Estagios.choices]
        qtd_estagio = []
        for i, j in Estagios.choices:
            x = Mentorados.objects.filter(estagio=i).filter(user=self.request.user).count()
            qtd_estagio.append(x)

        context['grafico'] = {
            'estagios': estagios,
            'qtd_estagio': qtd_estagio
        }

        return context
        
class ReunioesView(LoginRequiredMixin, generic.CreateView):
    model = DisponibilidadeHorarios
    form_class = DisponibilidadeHorarioForm
    template_name = 'reunioes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reunioes = Reuniao.objects.filter(data__mentor=self.request.user)
        context['reunioes'] = reunioes
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                erro_msg = valor['message']
        
        if erro_msg:
            messages.error(self.request, erro_msg)
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.add_message(self.request, messages.constants.SUCCESS, 'Horario disponibilizado com sucesso.')
        return reverse('reunioes')
    
class AuthView(generic.FormView):
    form_class = AuthMentoradoForm
    template_name = 'auth_mentorado.html'

    def get_success_url(self):
        messages.success(self.request, 'Autenticação realizada com sucesso.')
        return reverse('escolher_dia')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        response.set_cookie('auth_token', form.cleaned_data.get('token'), max_age=3600)
        return response

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                erro_msg = valor['message']
        
        if erro_msg:
            messages.error(self.request, erro_msg)
        return super().form_invalid(form)
    
class EscolherDiaView(generic.TemplateView):
    template_name = 'escolher_dia.html'

    def get(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().post(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Horarios
        mentorado =  valida_token(self.request.COOKIES.get('auth_token'))
        disponibilidades = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False,
            mentor=mentorado.user
        ).values_list('data_inicial', flat=True)
        datas = [i.date() for i in disponibilidades]
        context['datas'] = list(set(datas))

        return context
    
class AgendarReuniao(generic.CreateView):
    model = Reuniao
    form_class = ReuniaoForm
    template_name = 'agendar_reuniao.html'

    def get(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mentorado'] = valida_token(self.request.COOKIES.get('auth_token'))
        return kwargs
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.request.method == 'GET' and self.request.GET.get('data'):
            mentorado = valida_token(self.request.COOKIES.get('auth_token'))
            data = datetime.strptime(self.request.GET.get('data'), '%d-%m-%Y')
            horarios = DisponibilidadeHorarios.objects.filter(
                data_inicial__gte=data,
                data_inicial__lt=data + timedelta(days=1),
                agendado=False,
                mentor=mentorado.user
            )
            if horarios:
                form.fields['data'].initial = horarios[0]
            form.fields['data'].queryset = horarios

        return form
    
    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                erro_msg = valor['message']
        
        if erro_msg:
            messages.error(self.request, erro_msg)
            print(erro_msg)
        return super().form_invalid(form)
    
    def get_success_url(self):
        messages.add_message(self.request, messages.constants.SUCCESS, 'Horario agendado com sucesso.')
        return reverse('escolher_dia')
    
class TarefasView(generic.CreateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefa.html'
    
    def get_mentorado(self):
        try:
            return Mentorados.objects.get(id=self.kwargs.get('id'))
        except:
            raise Http404

    def get(self, request, *args, **kwargs):
        if self.get_mentorado().user != request.user:
            raise Http404
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if self.get_mentorado().user != request.user:
            raise Http404
        return super().get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mentorado'] = self.get_mentorado()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mentorado'] = self.get_mentorado()
        context['form2'] = kwargs.get('form2') or UploadsForm()
        context['tarefas'] = Tarefa.objects.filter(mentorado=self.get_mentorado())
        context['videos'] = Upload.objects.filter(mentorado=self.get_mentorado())
        return context
    
    def get_success_url(self):
        return reverse('tarefa', kwargs={'id': self.kwargs.get('id')})

class UploadView(View):
    def get_mentorado(self):
        try:
            return Mentorados.objects.get(id=self.kwargs.get('id'))
        except:
            raise Http404
        
    def get(self, request, *args, **kwargs):
        return redirect(reverse('tarefa', kwargs={'id': self.get_mentorado().id}))
    
    def post(self, request, *args, **kwargs):
        form = UploadsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(self.get_mentorado())
        return redirect(reverse('tarefa', kwargs={'id': self.get_mentorado().id}))

class TarefaMentoradoView(generic.TemplateView):
    template_name = 'tarefa_mentorado.html'

    def get(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if not valida_token(request.COOKIES.get('auth_token')):
            return redirect('auth_mentorado')
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mentorado'] = valida_token(self.request.COOKIES.get('auth_token'))
        context['videos'] = Upload.objects.filter(mentorado=context.get('mentorado'))
        context['tarefas'] = Tarefa.objects.filter(mentorado=context.get('mentorado'))
        return context

@method_decorator(csrf_exempt, name='dispatch')
class TarefaAlterarView(View):
    def get_mentorado(self):
        try:
            return Mentorados.objects.get(id=self.kwargs.get('id'))
        except:
            raise Http404
        
    def get(self, request, *args, **kwargs):
        return redirect(reverse('tarefa', kwargs={'id': self.get_mentorado().id}))

    def post(self, request, *args, **kwargs):
        tarefa = Tarefa.objects.get(id=self.kwargs.get('id'))  
        tarefa.realizada = not tarefa.realizada
        tarefa.save()
        return redirect(reverse('tarefa', kwargs={'id': self.get_mentorado().id}))
    