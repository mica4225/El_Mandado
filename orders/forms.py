from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['direccion_envio', 'ciudad', 'codigo_postal', 'telefono', 'notas']
        widgets = {
            'direccion_envio': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-llenar con datos del usuario
        if user:
            self.fields['direccion_envio'].initial = user.direccion
            self.fields['ciudad'].initial = user.ciudad
            self.fields['codigo_postal'].initial = user.codigo_postal
            self.fields['telefono'].initial = user.telefono
        
        # Aplicar Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})