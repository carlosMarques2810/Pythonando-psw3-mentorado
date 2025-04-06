from django import forms
from .models import Mentorados, Navigators, DisponibilidadeHorarios, Reuniao, Tarefa, Upload
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction

class MentoradosCadastroForm(forms.ModelForm):
    class Meta:
        model = Mentorados
        fields = ['nome', 'foto', 'estagio', 'navigator']
        widgets = {
            'nome': forms.TextInput(attrs={'name': 'nome', 'required': 'required', 'class': 'block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'}),
            'foto': forms.FileInput(attrs={'name': 'foto', 'id': 'foto', 'required': 'required', 'class': 'block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'}),
            'estagio': forms.Select(attrs={'name': 'estagio', 'class': '*:text-slate-900 block w-full rounded-md bg-white/5 px-3 py-2 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'}),
            'navigator': forms.Select(attrs={'name': 'navigator', 'class': '*:text-slate-900 block w-full rounded-md bg-white/5 px-3 py-2 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'})
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['navigator'].queryset = Navigators.objects.filter(user=user)

    def save(self, commit=True):
        mentorado = super().save(commit=False)
        mentorado.user = self.user
        mentorado.save()
        return mentorado
    
class DisponibilidadeHorarioForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadeHorarios
        fields = ['data_inicial']
        widgets = {
            'data_inicial': forms.DateTimeInput(attrs={'type': 'datetime-local', 'name': 'data_inicial', 'id': 'date', 'required': 'required', 'class': 'block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'})
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_data_inicial(self):
        data = self.cleaned_data.get('data_inicial')
        disponibilidade = DisponibilidadeHorarios.objects.filter(mentor=self.user).filter(
            data_inicial__gte=(data - timedelta(minutes=50)),
            data_inicial__lte=(data + timedelta(minutes=50))
        )

        if disponibilidade.exists():
            raise ValidationError('Você já possui uma reunião em aberto.')
        
        return data
        
    def save(self, commit=True):
        horario = super().save(commit=False)
        # adição de mentor
        horario.mentor = self.user
        horario.save()
        return horario

class AuthMentoradoForm(forms.Form):
    token = forms.CharField(label='token', required=True, widget=forms.TextInput(attrs={'name': 'token', 'required': 'required', 'class': 'w-full p-3 rounded-md bg-gray-300 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Digite seu token'}))

    def clean_token(self):
        token = self.cleaned_data.get('token')
        if not Mentorados.objects.filter(token=token).exists():
            raise ValidationError('Token inválido')
        return token
    
class ReuniaoForm(forms.ModelForm):
    class Meta:
        model = Reuniao
        fields = ['data', 'tag', 'descricao']
        widgets = {
            'data': forms.Select(attrs={'class': '*:text-slate-900 block  w-full rounded-md bg-white/5 px-3 py-2.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'}),
            'tag': forms.Select(attrs={'class': '*:text-slate-900 block w-full rounded-md bg-white/5 px-3 py-2.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'}),
            'descricao': forms.Textarea(attrs={'rows': '3', 'class': 'block w-full rounded-md bg-white/5 px-4 py-2 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'})
        }

    def __init__(self, mentorado, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentorado = mentorado

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if not data.mentor == self.mentorado.user:
            raise ValidationError('Selecione um horario válido.')
        return data

    def save(self, commit=True):
        reuniao = super().save(commit=False)
        reuniao.mentorado = self.mentorado
        with transaction.atomic():
            reuniao.data.agendado = True
            reuniao.data.save()
            reuniao.save()
        return reuniao
    
class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['tarefa']
        widgets = {
            'tarefa': forms.TextInput(attrs={'name': 'tarefa', 'autocomplete': 'email', 'required': 'required', 'class': 'block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6', 'placeholder':'Tarefas...'})
        }

    def __init__(self, mentorado, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mentorado = mentorado

    def save(self, commit=True):
        tarefa = super().save(commit=False)
        tarefa.mentorado = self.mentorado
        tarefa.save()
        return tarefa

class UploadsForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['video']
        widgets = {
            'video': forms.FileInput(attrs={'name': 'video', 'required': 'required', 'class': 'block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6'})
        }

    def save(self, mentorado, commit=True):
        upload = super().save(commit=False)
        upload.mentorado = mentorado
        upload.save()
        return upload
