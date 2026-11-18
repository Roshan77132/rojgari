from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST

from .emails import send_verification_email
from .forms import RegisterForm

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user)
            messages.success(
                request,
                "Account created. We sent a verification link to your email. Click it to verify.",
            )
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    error_message = None
    show_resend = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            error_message = 'Invalid username or password'
        elif not user.email_verified and not user.is_staff:
            error_message = 'Please verify your email first.'
            show_resend = True
        else:
            login(request, user)
            return redirect('dashboard:home')

    return render(request, 'accounts/login.html', {
        'error_message': error_message,
        'show_resend': show_resend,
    })


def verify_email(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        messages.success(request, "Email verified. You can now log in.")
    else:
        messages.error(request, "This link is invalid or has expired. Please request a new one.")
        return redirect('accounts:resend_verification')
    return redirect('accounts:login')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email__iexact=email, email_verified=False).first()
        if user:
            send_verification_email(request, user)
        # do not reveal whether the user exists (privacy)
        messages.info(request, "If an unverified account exists for this email, we sent a new verification link.")
        return redirect('accounts:login')
    return render(request, 'accounts/resend_verification.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('accounts:login')