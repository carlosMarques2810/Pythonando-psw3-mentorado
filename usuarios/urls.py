from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('login/', views.LoginView.as_view(), name='login')
]