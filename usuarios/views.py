from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UsuarioForm, UsuarioEditForm, FuncionarioForm, RegistroFaltaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .models import Usuario, Funcionario, RegistroFalta
from django.utils import timezone

def is_superuser(user):
    return user.is_superuser

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        user = authenticate(request, cpf=cpf, password=senha)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'CPF ou senha inválidos.')
    
    return render(request, 'usuarios/login.html')

@user_passes_test(is_superuser)
def cadastro_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Apenas administradores podem cadastrar novos usuários.")
        
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    
    return render(request, 'usuarios/cadastro.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    if request.user.is_superuser:
        funcionarios = Funcionario.objects.all()
        
        # Prepara dados para os dashboards
        funcionarios_com_faltas = []
        for funcionario in funcionarios:
            faltas = funcionario.faltas.all()
            total_dias_justificadas = 0
            total_dias_nao_justificadas = 0
            total_dias_licenca = 0
            
            for falta in faltas:
                data_fim = falta.data_fim or falta.data_inicio
                dias = (data_fim - falta.data_inicio).days + 1
                
                if falta.tipo == 'JUS':
                    total_dias_justificadas += dias
                elif falta.tipo == 'NAO':
                    total_dias_nao_justificadas += dias
                elif falta.tipo == 'LIC':
                    total_dias_licenca += dias
            
            # Total de faltas agora exclui licenças
            total_faltas = total_dias_justificadas + total_dias_nao_justificadas
            
            if total_faltas > 0 or total_dias_licenca > 0:  # Inclui funcionários com faltas ou licenças
                funcionarios_com_faltas.append({
                    'funcionario': funcionario,
                    'total_faltas': total_faltas,  # Apenas faltas (sem licenças)
                    'faltas_justificadas': total_dias_justificadas,
                    'faltas_nao_justificadas': total_dias_nao_justificadas,
                    'licencas': total_dias_licenca
                })
        
        # Ordena os funcionários por total de faltas (excluindo licenças)
        funcionarios_com_faltas.sort(key=lambda x: x['total_faltas'], reverse=True)
        top_faltas = funcionarios_com_faltas[:5]
        
        # Ordena por faltas não justificadas
        funcionarios_com_faltas.sort(key=lambda x: x['faltas_nao_justificadas'], reverse=True)
        top_nao_justificadas = funcionarios_com_faltas[:5]
        
        # Ordena por faltas justificadas
        funcionarios_com_faltas.sort(key=lambda x: x['faltas_justificadas'], reverse=True)
        top_justificadas = funcionarios_com_faltas[:5]
        
        # Ordena por licenças
        funcionarios_com_faltas.sort(key=lambda x: x['licencas'], reverse=True)
        top_licencas = funcionarios_com_faltas[:5]

        # Busca os 5 funcionários mais antigos
        funcionarios_antigos = Funcionario.objects.filter(ativo=True).order_by('data_admissao')[:5]
        top_antigos = []
        for funcionario in funcionarios_antigos:
            tempo_servico = timezone.now().date() - funcionario.data_admissao
            anos = tempo_servico.days // 365
            meses = (tempo_servico.days % 365) // 30
            top_antigos.append({
                'funcionario': funcionario,
                'data_admissao': funcionario.data_admissao,
                'tempo_servico': f"{anos} anos e {meses} meses"
            })
        
        context = {
            'is_superuser': True,
            'top_faltas': top_faltas,
            'top_nao_justificadas': top_nao_justificadas,
            'top_justificadas': top_justificadas,
            'top_licencas': top_licencas,
            'top_antigos': top_antigos
        }
    else:
        funcionarios = Funcionario.objects.filter(usuario=request.user)
        context = {
            'is_superuser': False,
            'funcionarios': funcionarios
        }
    
    return render(request, 'usuarios/home.html', context)

@user_passes_test(is_superuser)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('nome_completo')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

@user_passes_test(is_superuser)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('lista_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario)
    
    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario': usuario
    })

@user_passes_test(is_superuser)
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        if usuario.is_superuser and Usuario.objects.filter(is_superuser=True).count() <= 1:
            messages.error(request, 'Não é possível excluir o último superusuário do sistema.')
            return redirect('lista_usuarios')
            
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('lista_usuarios')
        
    return render(request, 'usuarios/confirmar_exclusao.html', {'usuario': usuario})

@login_required
@user_passes_test(is_superuser)
def adicionar_funcionario(request, usuario_id=None):
    usuario = get_object_or_404(Usuario, id=usuario_id) if usuario_id else request.user
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            funcionario = form.save(commit=False)
            funcionario.usuario = usuario
            funcionario.save()
            messages.success(request, 'Funcionário adicionado com sucesso!')
            return redirect('lista_funcionarios', usuario_id=usuario.id)
    else:
        form = FuncionarioForm()
    
    return render(request, 'usuarios/funcionario_form.html', {
        'form': form,
        'usuario': usuario,
        'titulo': 'Adicionar Funcionário'
    })

@login_required
@user_passes_test(is_superuser)
def editar_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário atualizado com sucesso!')
            return redirect('lista_funcionarios', usuario_id=funcionario.usuario.id)
    else:
        form = FuncionarioForm(instance=funcionario)
    
    return render(request, 'usuarios/funcionario_form.html', {
        'form': form,
        'funcionario': funcionario,
        'titulo': 'Editar Funcionário'
    })

@login_required
@user_passes_test(is_superuser)
def excluir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    if request.method == 'POST':
        usuario_id = funcionario.usuario.id
        funcionario.delete()
        messages.success(request, 'Funcionário excluído com sucesso!')
        return redirect('lista_funcionarios', usuario_id=usuario_id)
    
    return render(request, 'usuarios/confirmar_exclusao_funcionario.html', {
        'funcionario': funcionario
    })

@login_required
def lista_funcionarios(request, usuario_id=None):
    if usuario_id and not request.user.is_superuser:
        raise PermissionDenied("Você não tem permissão para ver funcionários de outros usuários.")
        
    if usuario_id:
        usuario = get_object_or_404(Usuario, id=usuario_id)
        funcionarios = Funcionario.objects.filter(usuario=usuario)
    else:
        usuario = request.user
        funcionarios = Funcionario.objects.filter(usuario=request.user)
    
    # Adiciona contagens de faltas para cada funcionário
    for funcionario in funcionarios:
        faltas = funcionario.faltas.all()
        total_dias_justificadas = 0
        total_dias_nao_justificadas = 0
        total_dias_licenca = 0
        
        for falta in faltas:
            # Se data_fim não estiver definida, usa data_inicio
            data_fim = falta.data_fim or falta.data_inicio
            # Calcula a diferença em dias entre data_fim e data_inicio
            dias = (data_fim - falta.data_inicio).days + 1  # +1 para incluir o último dia
            
            if falta.tipo == 'JUS':
                total_dias_justificadas += dias
            elif falta.tipo == 'NAO':
                total_dias_nao_justificadas += dias
            elif falta.tipo == 'LIC':
                total_dias_licenca += dias
        
        funcionario.total_faltas = total_dias_justificadas + total_dias_nao_justificadas + total_dias_licenca
        funcionario.faltas_justificadas = total_dias_justificadas
        funcionario.faltas_nao_justificadas = total_dias_nao_justificadas
        funcionario.licencas = total_dias_licenca
    
    return render(request, 'usuarios/lista_funcionarios.html', {
        'funcionarios': funcionarios,
        'usuario': usuario,
        'is_superuser': request.user.is_superuser,
        'is_own_list': usuario.id == request.user.id
    })

@login_required
def registrar_falta(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    # Verifica se o usuário tem permissão para registrar faltas
    if not request.user.is_superuser and funcionario.usuario != request.user:
        raise PermissionDenied("Você não tem permissão para registrar faltas deste funcionário.")
    
    if request.method == 'POST':
        form = RegistroFaltaForm(request.POST, request.FILES)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.funcionario = funcionario
            registro.registrado_por = request.user
            registro.save()
            messages.success(request, 'Falta registrada com sucesso!')
            return redirect('lista_faltas', funcionario_id=funcionario.id)
    else:
        form = RegistroFaltaForm()
    
    return render(request, 'usuarios/registro_falta.html', {
        'form': form,
        'funcionario': funcionario,
        'is_superuser': request.user.is_superuser
    })

@login_required
def lista_faltas(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    
    if not request.user.is_superuser and funcionario.usuario != request.user:
        raise PermissionDenied("Você não tem permissão para ver as faltas deste funcionário.")
    
    faltas = RegistroFalta.objects.filter(funcionario=funcionario)
    
    return render(request, 'usuarios/lista_faltas.html', {
        'funcionario': funcionario,
        'faltas': faltas
    })

@login_required
def editar_falta(request, falta_id):
    falta = get_object_or_404(RegistroFalta, id=falta_id)
    funcionario = falta.funcionario
    
    if not request.user.is_superuser and funcionario.usuario != request.user:
        raise PermissionDenied("Você não tem permissão para editar esta falta.")
    
    if request.method == 'POST':
        form = RegistroFaltaForm(request.POST, request.FILES, instance=falta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Falta atualizada com sucesso!')
            return redirect('lista_faltas', funcionario_id=funcionario.id)
    else:
        form = RegistroFaltaForm(instance=falta)
    
    return render(request, 'usuarios/registro_falta.html', {
        'form': form,
        'funcionario': funcionario,
        'titulo': 'Editar Falta',
        'is_edit': True
    })

@login_required
def excluir_falta(request, falta_id):
    falta = get_object_or_404(RegistroFalta, id=falta_id)
    funcionario = falta.funcionario
    
    if not request.user.is_superuser and funcionario.usuario != request.user:
        raise PermissionDenied("Você não tem permissão para excluir esta falta.")
    
    if request.method == 'POST':
        falta.delete()
        messages.success(request, 'Falta excluída com sucesso!')
        return redirect('lista_faltas', funcionario_id=funcionario.id)
    
    return render(request, 'usuarios/confirmar_exclusao_falta.html', {
        'falta': falta,
        'funcionario': funcionario
    })
