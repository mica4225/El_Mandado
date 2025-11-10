from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

@login_required
def switch_to_seller(request):
    if request.user.rol == 'cliente':
        request.user.rol = 'vendedor'
        request.user.save()
        messages.success(request, '¡Ahora eres vendedor! Ya podés publicar productos.')
    return redirect('profile')

@login_required
def delete_account(request):
    """Permite al usuario eliminar su propia cuenta"""
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        # Cerrar sesión y eliminar cuenta
        logout(request)
        user.delete()
        
        messages.success(request, f'Tu cuenta "{username}" ha sido eliminada correctamente')
        return redirect('home')
    
    return render(request, 'users/delete_account.html')
