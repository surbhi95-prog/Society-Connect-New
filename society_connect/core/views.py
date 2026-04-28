from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Complaint,RuleCategory
from admin_panel.models import Service,Rule
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import logout,login,authenticate

#landing page view
def continue_as(request):
    return render(request, "core/continueAs.html")


# Registration page view
#accessing forms.py in core folder
from .forms import CustomUserCreationForm, UserProfileForm

@csrf_exempt
def register(request):
    user_form = CustomUserCreationForm(request.POST or None)
    profile_form = UserProfileForm(request.POST or None)

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = 'resident'   
            # profile.society remains NULL (assigned later by superuser)
            profile.save()

            return redirect('login')

    return render(request, 'core/registration.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })



# Login page view
from django.contrib.auth import authenticate, login
#this is Django's built-in authentication system

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        # Login only verifies existing user credentials using authenticate()
        #manages session using login()

        if user is not None:
            login(request, user)
            return redirect("home")  # index.html
        else:
            # optional: send error message
            return render(request, "core/login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "core/login.html")


# Home page view
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "core/index.html")


# complaints page
@login_required
@csrf_exempt
def complaint_form(request):
    

    if request.method == "POST":
        category = request.POST.get('category')
        description = request.POST.get('description')
        location = request.POST.get('location')
        attachment = request.FILES.get('fileUpload')

        Complaint.objects.create(
            user=request.user,
            category=category,
            description=description,
            location=location,
            attachment=attachment
        )

        return redirect('complaint_form')

    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'core/complaint_form.html', {
        'complaints': complaints
    })
   
# maintenance page
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def maintenance(request):
    return render(request, "core/maintenance.html", {
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
    })

# Payment History page
@login_required
def payment_history(request):
    # Fetch payments for the resident and order by newest first
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "core/payment_history.html", {
        "payments": payments
    })


# notice page
from admin_panel.models import Notice

@login_required
def notice(request):
    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/notice.html', {
        'notices': notices
    })


# rules & regulations page
def rules_regulations(request):
    return render(request, "core/rules_regulations.html")


# services page
def services(request):
    return render(request, "core/services.html")

def services(request):
    """Display all active services for residents"""
    services = Service.objects.filter(is_active=True).order_by('service_type')
    
    context = {
        'services': services,
    }
    return render(request, 'core/services.html', context)


# RULES VIEW
# views.py

def rules_regulations(request):
    rules = Rule.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/rules_regulations.html', {
        'rules': rules
    })

# LOGOUT FOR RESIDENT
# # LOGOUT VIEW IT IS
# @login_required
# def resident_logout(request):
#     logout(request)
#     return redirect('login')

from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
@csrf_exempt
def profile(request):
    user = request.user
    user_profile = user.userprofile
    
    if request.method == 'POST':
        # Update auth User model
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update UserProfile model
        user_profile.full_name = request.POST.get('full_name', user_profile.full_name)
        user_profile.phone = request.POST.get('phone', user_profile.phone)
        user_profile.wing = request.POST.get('wing', user_profile.wing)
        user_profile.flat_no = request.POST.get('flat_no', user_profile.flat_no)
        
        # Handle profile picture upload
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']
            
        user_profile.save()
        messages.success(request, 'Your profile was successfully updated!')
        return redirect('profile')
        
    return render(request, 'core/profile.html')

import razorpay
from django.conf import settings
from django.http import JsonResponse

@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    amount = data.get("amount")

    if not amount:
        return JsonResponse({"error": "Amount is required"}, status=400)

    amount = int(amount) * 100  # convert ₹ to paise

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return JsonResponse({
        "order_id": payment["id"],
        "amount": payment["amount"]
    })

# VIEW FOR PAYMENT MODEL
from .models import Payment

@csrf_exempt
@login_required
def save_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Payment.objects.create(
            user=request.user,
            amount=int(data.get("amount")),
            razorpay_order_id=data.get("order_id"),
            razorpay_payment_id=data.get("payment_id"),
            status="Success"
        )

        return JsonResponse({"message": "Payment saved successfully"})