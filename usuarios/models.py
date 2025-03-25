from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, nome_completo, password=None, **extra_fields):
        if not cpf:
            raise ValueError('O CPF deve ser fornecido')
        if not nome_completo:
            raise ValueError('O nome completo deve ser fornecido')

        # Gerar username automaticamente se não fornecido
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = f"user_{cpf}"

        user = self.model(
            cpf=cpf,
            nome_completo=nome_completo,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, nome_completo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Gerar username automaticamente para superuser
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = f"admin_{cpf}"
            
        return self.create_user(cpf, nome_completo, password, **extra_fields)

class Usuario(AbstractUser):
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='CPF deve conter exatamente 11 dígitos numéricos.'
            )
        ]
    )
    nome_completo = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['nome_completo']
    
    objects = UsuarioManager()

    def __str__(self):
        return self.nome_completo

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"user_{self.cpf}"
        # Capitaliza cada palavra do nome
        self.nome_completo = ' '.join(word.capitalize() for word in self.nome_completo.split())
        super().save(*args, **kwargs)

class TipoFalta(models.TextChoices):
    JUSTIFICADA = 'JUS', 'Justificada'
    NAO_JUSTIFICADA = 'NAO', 'Não Justificada'
    LICENCA = 'LIC', 'Licença'

class TipoCategoria(models.TextChoices):
    TRABALHADOR = 'TRA', 'Trabalhador'
    ESTAGIARIO = 'EST', 'Estagiário'
    CONTRATO_DETERMINADO = 'CTD', 'Empregado sob contrato de trabalho por prazo determinado/intermitente - Lei n°. 9.601/98'

class Funcionario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='funcionarios')
    codigo = models.CharField('Código', max_length=20, unique=True, default='0000')
    nome_empresa = models.CharField('Nome da Empresa', max_length=255)
    nome_funcionario = models.CharField('Nome do Funcionário', max_length=255)
    departamento = models.CharField('Departamento', max_length=100)
    setor = models.CharField('Complemento/Setor', max_length=100)
    funcao = models.CharField('Função', max_length=100)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_admissao = models.DateField('Data de Admissão', default=timezone.now)
    codigo_categoria = models.CharField('Código da Categoria', max_length=20, default='000')
    categoria = models.CharField(
        'Categoria',
        max_length=3,
        choices=TipoCategoria.choices,
        default=TipoCategoria.TRABALHADOR
    )
    horario = models.CharField('Horário', max_length=100, help_text='Ex: 08:00 - 17:00', default='08:00 - 17:00')
    salario = models.DecimalField('Salário', max_digits=10, decimal_places=2, default=0)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['-data_criacao']

    def __str__(self):
        codigo_display = self.codigo if self.codigo else 'Sem código'
        return f"{codigo_display} - {self.nome_funcionario} - {self.nome_empresa}"

    def save(self, *args, **kwargs):
        # Capitaliza cada palavra do nome do funcionário e da empresa
        self.nome_funcionario = ' '.join(word.capitalize() for word in self.nome_funcionario.split())
        self.nome_empresa = ' '.join(word.capitalize() for word in self.nome_empresa.split())
        self.departamento = ' '.join(word.capitalize() for word in self.departamento.split())
        self.setor = ' '.join(word.capitalize() for word in self.setor.split())
        self.funcao = ' '.join(word.capitalize() for word in self.funcao.split())
        if self.categoria:
            self.categoria = ' '.join(word.capitalize() for word in self.categoria.split())
        super().save(*args, **kwargs)

class RegistroFalta(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='faltas')
    data_inicio = models.DateField('Data Inicial', default=timezone.now)
    data_fim = models.DateField('Data Final', null=True, blank=True)
    tipo = models.CharField(
        max_length=3,
        choices=TipoFalta.choices,
        default=TipoFalta.NAO_JUSTIFICADA
    )
    justificativa = models.TextField('Justificativa', blank=True, null=True)
    atestado = models.FileField(
        'Atestado', 
        upload_to='atestados/%Y/%m/',
        blank=True,
        null=True
    )
    data_registro = models.DateTimeField('Data do Registro', auto_now_add=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Registro de Falta'
        verbose_name_plural = 'Registros de Faltas'
        ordering = ['-data_inicio']

    def __str__(self):
        if not self.data_fim or self.data_inicio == self.data_fim:
            return f'Falta de {self.funcionario.nome_funcionario} em {self.data_inicio}'
        return f'Falta de {self.funcionario.nome_funcionario} de {self.data_inicio} até {self.data_fim}'

    def clean(self):
        if self.data_fim and self.data_inicio > self.data_fim:
            raise ValidationError('A data final não pode ser anterior à data inicial.')
        
        if not self.data_fim:
            self.data_fim = self.data_inicio

    def save(self, *args, **kwargs):
        if not self.data_fim:
            self.data_fim = self.data_inicio
        super().save(*args, **kwargs)
