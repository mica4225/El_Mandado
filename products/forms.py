from django import forms
from .models import Product, ProductImage, Category

class ProductForm(forms.ModelForm):
    # Campo para crear nueva categoría
    nueva_categoria = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de la nueva categoría'
        }),
        label='O crear una nueva categoría',
        help_text='Si la categoría no existe, podés crearla aquí'
    )
    
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
            'categoria': 'Categoría existente (opcional si creás una nueva)',
            'precio': 'Precio (en pesos)',
            'stock': 'Stock disponible',
            'imagen_principal': 'Imagen del producto',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer categoría opcional si se va a crear una nueva
        self.fields['categoria'].required = False
        
        for field in self.fields:
            if field not in ['activo']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['precio'].help_text = 'Ingresá el precio sin puntos ni comas. Ej: 1200 para $1.200'
    
    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        nueva_categoria = cleaned_data.get('nueva_categoria')
        
        # Validar que al menos una opción esté seleccionada
        if not categoria and not nueva_categoria:
            raise forms.ValidationError('Debés seleccionar una categoría o crear una nueva')
        
        # Si hay nueva categoría, crearla
        if nueva_categoria:
            categoria, created = Category.objects.get_or_create(
                nombre=nueva_categoria.strip(),
                defaults={'icono': 'bi-tag'}
            )
            cleaned_data['categoria'] = categoria
        
        return cleaned_data


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
        self.fields['orden'].initial = 0