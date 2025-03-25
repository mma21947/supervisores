from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    
    # URLs para funcionários
    path('usuarios/<int:usuario_id>/funcionarios/', views.lista_funcionarios, name='lista_funcionarios'),
    path('usuarios/<int:usuario_id>/funcionarios/adicionar/', views.adicionar_funcionario, name='adicionar_funcionario'),
    path('funcionarios/editar/<int:funcionario_id>/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/excluir/<int:funcionario_id>/', views.excluir_funcionario, name='excluir_funcionario'),
    
    # URLs para faltas
    path('funcionarios/<int:funcionario_id>/faltas/', views.lista_faltas, name='lista_faltas'),
    path('funcionarios/<int:funcionario_id>/faltas/registrar/', views.registrar_falta, name='registrar_falta'),
    path('faltas/editar/<int:falta_id>/', views.editar_falta, name='editar_falta'),
    path('faltas/excluir/<int:falta_id>/', views.excluir_falta, name='excluir_falta'),
] 