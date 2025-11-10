from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'stock', 'imagen_principal', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={
                'step': '1',           
                'min': '0',            
                'max': '9999999',     
                'placeholder': 'Ej: 1200'
            }),
            'stock': forms.NumberInput(attrs={
                'step': '1',
                'min': '0',
                'max': '999999'
            }),
        }
        labels = {
            'precio': 'Precio (en pesos)',
            'stock': 'Stock disponible',
            'imagen_principal': 'Imagen del producto',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['activo']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Agregar texto de ayuda
        self.fields['precio'].help_text = 'Ingresá el precio sin puntos ni comas. Ej: 1200 para $1.200'

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['imagen', 'orden']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['imagen'].required = False
        self.fields['orden'].required = False