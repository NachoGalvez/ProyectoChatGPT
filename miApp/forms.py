from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'alias', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.alias = self.cleaned_data['alias']
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import AuthenticationForm

from django import forms
from .models import Preferencia

class PreferenciaForm(forms.ModelForm):
    class Meta:
        model = Preferencia
        fields = [
            'horario_estudio', 
            'tiempo_llegada_uni', 
            'tiempo_preparacion', 
            'lugar_estudio', 
            'tiempo_antes_dormir',
            'preferencias_personalizadas'
        ]
        widgets = {
            'horario_estudio': forms.RadioSelect(choices=[
                ('mañana', 'Mañana'),
                ('tarde', 'Tarde'),
                ('noche', 'Noche')
            ]),
            'preferencias_personalizadas': forms.Textarea(attrs={'rows': 3}),
        }
