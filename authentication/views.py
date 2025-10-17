from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.core.mail import send_mail
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())  # simpler!
        return redirect('authentication:home')

    return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:home')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        login(request, user)

        # Try to send welcome email, but don't fail if it doesn't work
        try:
            send_mail(
                'Welcome to Lite WORK ERP',
                'Thank you for registering!',
                None,  #change email to litework main email
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log the error but continue with registration
            print(f"Failed to send welcome email: {e}")

        messages.success(request, 'Account created successfully! Welcome to Lite WORK ERP.')
        return redirect('authentication:home')

    return render(request, 'authentication/register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('authentication:login')


def home_view(request):
    return render(request, 'authentication/home.html')
