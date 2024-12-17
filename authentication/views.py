from django.shortcuts import render, redirect,  get_object_or_404
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
import json
from authentication.models import Task
from django.views.decorators.csrf import csrf_exempt


def edit_task(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        title = request.GET.get('title')  # The original title
        try:
            task = Task.objects.get(title=title)
            task.title = data.get('title', task.title)
            task.start_date = data.get('start_date', task.start_date)
            task.due_date = data.get('due_date', task.due_date)
            task.priority = data.get('priority', task.priority)
            task.status = data.get('status', task.status)
            task.save()
            return JsonResponse({'message': 'Task updated successfully.'})
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def edit_task_member(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        title = request.GET.get('title')  # The original title

        try:
            # Fetch the task by its title
            task = Task.objects.get(title=title)
            
            # Update only the status field
            new_status = data.get('status')
            if new_status:  # Check if status is provided
                task.status = new_status
                task.save()
                return JsonResponse({'message': 'Task status updated successfully.'})
            else:
                return JsonResponse({'error': 'No status provided.'}, status=400)

        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
        
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def create_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        start_date = data.get('start_date')
        due_date = data.get('due_date')
        priority = data.get('priority')
        status = data.get('status')
        assign_users = data.get('assign_users', [])  # List of usernames

        try:
            # Create a new task
            task = Task.objects.create(
                title=title,
                start_date=start_date,
                due_date=due_date,
                priority=priority,
                status=status
            )
            # Assign users to the task
            users = User.objects.filter(username__in=assign_users)
            task.assign_users.set(users)  # Set ManyToMany relationship
            task.save()

            return JsonResponse({'message': 'Task created successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

# Create your views here.
def home(request):
    return render(request,"authentication/index.html")

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
            subject = "Welcome to runtask Login!!"
            message = f"Hello {leader.first_name}!! \nWelcome to runtask \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\nruntask Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]  # Use myuser.email for email
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email at runtask Login!!"
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
            subject = "Welcome to runtask Login!!"
            message = f"Hello {member.first_name}!! \nWelcome to runtask \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You\nruntask Team"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]  # Use myuser.email for email
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email at runtask Login!!"
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
    tasks = Task.objects.all()
    members = Member.objects.all()

    # Pre-fetch assigned users for all tasks
    task_assigned_users = {
        task.title: list(task.assign_users.values_list('username', flat=True))
        for task in tasks
    }

    context = {
        'tasks': tasks,
        'members': members,
        'task_assigned_users': task_assigned_users
    }
    return render(request, 'authentication/dashboard_leader.html', {'members': members, 'tasks':tasks})

def view_user_leader(request):
    # Fetch all leaders
    leaders = Leader.objects.all()
    
    # Fetch all members
    members = Member.objects.all()
    
    # Fetch all tasks
    tasks = Task.objects.all()
    
    # Pass leaders, members, and tasks to the template
    return render(request, 'authentication/view_user_leader.html', {'members': members, 'leaders': leaders, 'tasks': tasks})

@login_required
def dashboard(request):
    # Fetch tasks assigned to the currently logged-in user
    tasks = Task.objects.filter(assign_users=request.user)
    
    return render(request, 'authentication/dashboard.html', {'tasks': tasks})

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

@csrf_exempt  # Only for testing. Use CSRF tokens in production.
def add_task(request):
    if request.method == 'POST':
        try:
            # Parse form data from the request
            title = request.POST.get('title')
            start_date = request.POST.get('start_date')
            due_date = request.POST.get('due_date')
            priority = request.POST.get('priority')
            status = request.POST.get('status')
            assign_users = json.loads(request.POST.get('assign_users', '[]'))  # JSON for multiple selection
            
            # Debug: Print form values
            print("Received Data:", title, start_date, due_date, priority, status, assign_users)
            
            # Save task in the database
            task = Task.objects.create(
                title=title,
                start_date=start_date,
                due_date=due_date,
                priority=priority,
                status=status,
            )
            
            # Save assign_users logic (if needed)
            # Example: Assuming assign_users are emails, you can add logic to associate them
            
            return JsonResponse({'success': True, 'message': 'Task added successfully!'})
        except Exception as e:
            print("Error occurred:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def delete_task(request):
    if request.method == 'DELETE':
        task_title = request.GET.get('title')
        task = get_object_or_404(Task, title=task_title)
        task.delete()
        return JsonResponse({'status': 'success', 'message': 'Task deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
