from django.urls import path
from . import views

urlpatterns = [
    path('', views.MentoradosView.as_view(), name='mentorados'),
    path('reunioes/', views.ReunioesView.as_view(), name='reunioes'),
    path('auth/', views.AuthView.as_view(), name="auth_mentorado"),
    path('escolher_dia/', views.EscolherDiaView.as_view(), name='escolher_dia'),
    path('agendar_reuniao/', views.AgendarReuniao.as_view(), name='agendar_reuniao'),
    path('tarefa/<int:id>', views.TarefasView.as_view(), name='tarefa'),
    path('upload/<int:id>', views.UploadView.as_view(), name='upload'),
    path('tarefa_mentorado/', views.TarefaMentoradoView.as_view(), name='tarefa_mentorado'),
    path('tarefa_alterar/<int:id>', views.TarefaAlterarView.as_view(), name="tarefa_alterar")
]