from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Funcionario, RegistroFalta, TipoCategoria

class UsuarioForm(UserCreationForm):
    cpf = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu CPF'})
    )
    nome_completo = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'})
    )

    class Meta:
        model = Usuario
        fields = ('nome_completo', 'cpf', 'password1', 'password2')

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf.isdigit() or len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
        
        # Verifica se o CPF já existe
        if Usuario.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
        return cpf

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        # Gera um username único baseado no CPF
        user.username = f"user_{self.cleaned_data.get('cpf')}"
        if commit:
            user.save()
        return user

class UsuarioEditForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cpf = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label='Ativo',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_superuser = forms.BooleanField(
        label='Administrador',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    nova_senha = forms.CharField(
        label='Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ('nome_completo', 'cpf', 'is_active', 'is_superuser')

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf.isdigit() or len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
        
        # Verifica se o CPF já existe para outro usuário
        if Usuario.objects.exclude(id=self.instance.id).filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está em uso.')
        return cpf

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if nova_senha and nova_senha != confirmar_senha:
            raise forms.ValidationError('As senhas não coincidem.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')
        
        if nova_senha:
            user.set_password(nova_senha)
            
        if commit:
            user.save()
        return user

class FuncionarioForm(forms.ModelForm):
    codigo = forms.CharField(
        label='Código',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o código do funcionário'
        })
    )
    nome_empresa = forms.CharField(
        label='Nome da Empresa',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nome_funcionario = forms.CharField(
        label='Nome do Funcionário',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departamento = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    setor = forms.CharField(
        label='Complemento/Setor',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    funcao = forms.CharField(
        label='Função',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    data_admissao = forms.DateField(
        label='Data de Admissão',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    codigo_categoria = forms.CharField(
        label='Código da Categoria',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    categoria = forms.ChoiceField(
        label='Categoria',
        choices=[('', '-- Selecione uma categoria --')] + list(TipoCategoria.choices),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    horario = forms.CharField(
        label='Horário',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 08:00 - 17:00'
        })
    )
    salario = forms.DecimalField(
        label='Salário',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'R$ 0,00'
        })
    )
    ativo = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Funcionario
        fields = (
            'codigo', 'nome_empresa', 'nome_funcionario', 'departamento', 
            'setor', 'funcao', 'data_admissao', 'codigo_categoria', 
            'categoria', 'horario', 'salario', 'ativo'
        )

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if not codigo:
            raise forms.ValidationError('O código é obrigatório.')
        # Verifica se o código já existe para outro funcionário
        if Funcionario.objects.exclude(id=self.instance.id if self.instance else None).filter(codigo=codigo).exists():
            raise forms.ValidationError('Este código já está em uso.')
        return codigo

    def clean_categoria(self):
        categoria = self.cleaned_data.get('categoria')
        if not categoria:
            raise forms.ValidationError('Por favor, selecione uma categoria.')
        return categoria

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if salario is not None and salario <= 0:
            raise forms.ValidationError('O salário deve ser maior que zero.')
        return salario

class RegistroFaltaForm(forms.ModelForm):
    data_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data Inicial'
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data Final'
    )
    
    class Meta:
        model = RegistroFalta
        fields = ['data_inicio', 'data_fim', 'tipo', 'justificativa', 'atestado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'atestado': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError('A data final não pode ser anterior à data inicial.')

        return cleaned_data 