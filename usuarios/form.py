from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

styleInputForm = "block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline outline-1 -outline-offset-1 outline-white/10 placeholder:text-gray-500 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-500 sm:text-sm/6"

class CadastroForm(forms.ModelForm):
    passwordConfirm = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput(attrs={'name': 'passwordConfirm', 'class': styleInputForm, 'required': 'required', 'minlength': '6'}))
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'name': 'username', 'class': styleInputForm, 'required': 'required'}),
            'password': forms.PasswordInput(attrs={'name': 'password', 'class': styleInputForm, 'required': 'required', 'minlength': '6'})
        }

    def clean_password(self):
        password = self.data.get('password')
        if len(password) < 6:
            raise ValidationError('A senha deve ter 6 ou mais caracteres.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        passwordConfirm = cleaned_data.get('passwordConfirm')

        if password != passwordConfirm:
            raise ValidationError('Senha e confirmar senha devem ser iguais.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário', widget=forms.TextInput(attrs={'name': 'username', 'class': styleInputForm, 'required': 'required'}))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'name': 'passwordConfirm', 'class': styleInputForm, 'required': 'required', 'minlength': '6'}))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        self.user = authenticate(username=username, password=password)
        if self.user is None:
            raise ValidationError('Usuario ou senha incorreta.')

        return cleaned_data