from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    # ✅ NUEVO: Campo para elegir tipo de entrega
    tipo_entrega = forms.ChoiceField(
        choices=Order.DELIVERY_CHOICES,
        widget=forms.RadioSelect,
        initial='retiro',
        label='¿Cómo querés recibir tu pedido?'
    )
    
    class Meta:
        model = Order
        fields = ['tipo_entrega', 'direccion_envio', 'ciudad', 'codigo_postal', 'telefono', 'notas']
        widgets = {
            'direccion_envio': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'direccion_envio': 'Dirección de entrega',
            'ciudad': 'Ciudad/Localidad',
            'codigo_postal': 'Código Postal',
            'telefono': 'Teléfono de contacto',
            'notas': 'Notas adicionales (opcional)',
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
        
        # Hacer campos opcionales inicialmente
        self.fields['direccion_envio'].required = False
        self.fields['ciudad'].required = False
        self.fields['codigo_postal'].required = False
        self.fields['telefono'].required = False
        
        # Aplicar Bootstrap
        for field in self.fields:
            if field != 'tipo_entrega':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get('tipo_entrega')
        
        # Si eligió envío, los campos son obligatorios
        if tipo_entrega == 'envio':
            required_fields = ['direccion_envio', 'ciudad', 'codigo_postal', 'telefono']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Este campo es obligatorio para envío a domicilio')
        
        return cleaned_data

