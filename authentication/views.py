from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from djproj import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .tokens import generate_token
from .models import CSVFile
from django.contrib.auth import login
from .models import Member, Leader
from .forms import CSVFileForm
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Task
from .forms import TaskForm

def create_task(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('taskTitle')
        start_date = request.POST.get('startDate')
        due_date = request.POST.get('dueDate')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        duration = request.POST.get('duration')
        assigned_user_emails = request.POST.getlist('assignUsers')

        # Create the task
        task = Task.objects.create(
            title=title,
            start_date=start_date,
            due_date=due_date,
            priority=priority,
            status=status,
            duration=duration,
            created_by=request.user
        )

        # Assign users to the task
        for email in assigned_user_emails:
            try:
                member = Member.objects.get(user__email=email)
                task.assigned_users.add(member)
            except Member.DoesNotExist:
                # Handle case where member is not found
                pass

        # Redirect or return a response
        return redirect('dashboard_leader')  # Adjust the redirect as needed

    # If not a POST request, render the form (or handle differently)
    return render(request, 'your_template.html')
# Create your views here.
def home(request):
    return render(request,"authentication/index.html")


from django.contrib.auth.models import Group

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        user_type = request.POST.get("user_type")  # Safely get user_type

        if not user_type:  # Ensure user_type is present
            messages.error(request, "User type is required!")
            return redirect('home')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try some other username.")
            return redirect('home')
        
        # if User.objects.filter(email=email).exists():
        #     messages.error(request, "Email Already Registered!!")
        #     return redirect('home')
        
        # # Check email existence in Member model via the related User
        # if Member.objects.filter(user__email=email).exists():
        #     messages.error(request, "Email Already Registered!!")
        #     return redirect('home')

        # # Check email existence in Leader model via the related User
        # if Leader.objects.filter(user__email=email).exists():
        #     messages.error(request, "Email Already Registered!!")
        #     return redirect('home')
        
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')
        
        # Link the user with the appropriate model instance based on user_type
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        # Based on user type, create the appropriate model instance
        if user_type == 'leader':
            leader = Leader(user=myuser)  # Link the user instance
            leader.save()
            leader.first_name = fname
            leader.last_name = lname
            leader.is_active = False
            leader.save()

            messages.success(request, "Your Account has been created successfully! Please check your email to confirm your email address in order to activate your account.")
            
            # Send Welcome Email
            subject = "Welcome to Insightify Login!!"
            message = f"Hello {leader.first_name}!! \nWelcome to Insightify \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\nInsightify Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]  # Use myuser.email for email
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email at Insightify Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': leader.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(leader.pk)),
                'token': generate_token.make_token(leader)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email],  # Use myuser.email for email
            )
            send_mail(email_subject, message2, from_email, to_list, fail_silently=True)

        elif user_type == 'member':
            member = Member(user=myuser)  # Link the user instance
            member.save()
            member.first_name = fname
            member.last_name = lname
            member.is_active = False
            member.save()

            messages.success(request, "Your Account has been created successfully! Please check your email to confirm your email address in order to activate your account.")
            
            # Send Welcome Email
            subject = "Welcome to Insightify Login!!"
            message = f"Hello {member.first_name}!! \nWelcome to Insightify \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\nInsightify Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]  # Use myuser.email for email
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email at Insightify Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': member.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(member.pk)),
                'token': generate_token.make_token(member)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email],  # Use myuser.email for email
            )
            send_mail(email_subject, message2, from_email, to_list, fail_silently=True)

        return redirect('signin')
    
    return render(request, "authentication/signup.html")

@login_required
def dashboard_leader(request):
    # Fetch all members
    members = Member.objects.all()
    return render(request, 'authentication/dashboard_leader.html', {'members': members})

@login_required
def dashboard(request):
    return render(request, 'authentication/dashboard.html')

from django.contrib.auth import get_user_model

User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        messages.success(request, "Your Account has been activated!")
    else:
        messages.error(request, "Activation failed. Please try again or contact support.")

    return redirect('signin')

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        pass1 = request.POST["pass1"]
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)

            # Check if user belongs to Leader or Member model
            if Leader.objects.filter(user=user).exists():
                return redirect("dashboard_leader")  # Redirect to leader dashboard
            elif Member.objects.filter(user=user).exists():
                return redirect("dashboard")  # Redirect to member dashboard
            else:
                messages.info(request, "Role not assigned.")
                return redirect("home")
        else:
            messages.error(request, "Bad Credentials!")
            return redirect("signin")
    
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")

@csrf_exempt  # Temporarily disable CSRF for AJAX (handle it carefully in production)
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Save the uploaded file directly to the database
        new_file = CSVFile(file=uploaded_file)
        new_file.save()

        # Fetch all the files in the database
        files = CSVFile.objects.all()
        file_names = [file.file.name for file in files]  # List of all file names

        # Return a JSON response indicating success and the list of files
        return JsonResponse({
            'message': 'File uploaded successfully!',
            'status': 'success',
            'files': file_names  # Return the list of files
        })
    
    # Return an error response if no file was uploaded
    return JsonResponse({'message': 'No file uploaded.', 'status': 'error'}, status=400)