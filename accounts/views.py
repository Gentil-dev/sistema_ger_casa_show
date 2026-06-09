from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .forms import EmailRegisterForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import PasswordResetEmailForm


def register_view(request):
    if request.method == "POST":
        form = EmailRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = get_random_string(8)  # Ex: 'a9F2k8Xz'

            # Cria usuário com e-mail como username
            User.objects.create_user(username=email, email=email, password=senha)

            # Envia e-mail com a senha
            send_mail(
                subject='Sua senha de acesso',
                message=f'Sua senha é: {senha}',
                from_email='seu@email.com',  # Altere para seu e-mail de envio
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'Registro realizado! Verifique seu e-mail.')
            return redirect('login')
    else:
        form = EmailRegisterForm()

    return render(request, 'register.html', {'user_form': form})


def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('evento_list')  # Redireciona para a lista de eventos após login
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Dados de login inválidos.')
    else:
        login_form = AuthenticationForm()  # Inicializa o formulário em caso de GET

    return render(request, 'login.html', {'login_form': login_form})

def logout_view(request):
    logout(request)
    return redirect('home')



def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                nova_senha = get_random_string(8)
                user.set_password(nova_senha)
                user.save()

                send_mail(
                    subject='Nova senha de acesso',
                    message=f'Sua nova senha é: {nova_senha}',
                    from_email='DHsistemaevento@gmail.com',
                    recipient_list=[email],
                    fail_silently=False,
                )

                messages.success(request, 'Nova senha enviada! Verifique seu e-mail.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'E-mail não encontrado.')
    else:
        form = PasswordResetEmailForm()

    return render(request, 'password_reset.html', {'form': form})

