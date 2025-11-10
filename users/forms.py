from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=20, required=False)
    
    rol = forms.ChoiceField(
        choices=[
            ('cliente', 'Cliente - Puedo comprar productos'),
            ('vendedor', 'Vendedor - Puedo vender y comprar'),
        ],
        widget=forms.RadioSelect,
        initial='cliente',
        label='¿Qué querés hacer?'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'rol', 'telefono')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'rol':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'telefono', 'direccion', 
                  'ciudad', 'codigo_postal', 'avatar', 'rol')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})