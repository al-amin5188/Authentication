from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login, logout
from authuser.models import PasswordResetTable
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse



# Create your views here.

def register_view(request):

    if request.method=='POST':
        #Get user data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # user data Validation
        user_data_has_error=False

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request,'Invalid username')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request,'Invalid Email')

        if len(password)<5:
            user_data_has_error=True
            messages.error(request,'Password must be at last 5 charachter')


        if not user_data_has_error:
            new_user=User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )

            messages.success(request,'Account created Successfully')
            return redirect('login')
        
        else:
            return redirect ('register')


    return render(request,'authuser/register.html')

def login_view(request):

    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user=authenticate(
            request=request, username=username, password=password
        )

        if user is not None:
            login(request,user)
            return redirect('')

        else:
            messages.error(request,'Invalid username or password')
            return redirect ('login')

    return render (request,'authuser/login.html')

def logout_view(request):
    logout(request)

    return redirect ('login')

def forget_pass(request):

    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordResetTable(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}  '
        
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('send_pass', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot')


    return render(request, 'authuser/forget_password.html')



def PasswordResetSent(request, reset_id):

    if PasswordResetTable.objects.filter(reset_id=reset_id).exists():
        return render(request, 'authuser/password_reset_send.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot')


def reset_pass(request, reset_id):
    try:
        password_reset_id = PasswordResetTable.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_time + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset', reset_id=reset_id)

    
    except PasswordResetTable.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot')



    return render (request,'authuser/reset_password.html')