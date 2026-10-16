from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from ..models.usuario import Usuario


class AdminUsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'nome', 'telefone', 'is_active', 'is_staff')


class AdminUsuarioChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = '__all__'