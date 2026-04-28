# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import logout

from django.db.models import Count
from django.db.models.functions import TruncMonth

from .models import Rule, Service, Notice

#admin_registration_view
from core.forms import AdminProfileForm, CustomUserCreationForm

def admin_register(request):
    user_form = CustomUserCreationForm(request.POST or None)
    profile_form = AdminProfileForm(request.POST or None)

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = 'admin'   # IMPORTANT
            profile.save()

            return redirect('admin_panel:admin_login')  # or admin login page later

    return render(request, 'admin_panel/adminRegister.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


#admin_login view

from django.contrib.auth import authenticate, login
from core.models import UserProfile, RuleCategory

def admin_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == 'admin':
                    login(request, user)
                    return redirect('admin_panel:admin_home')  # change later
                else:
                    error = "You are not authorized as admin."
            except UserProfile.DoesNotExist:
                error = "Profile not found."
        else:
            error = "Invalid username or password."

    return render(request, 'admin_panel/adminLogin.html', {'error': error})


#admin_home view
from django.contrib.auth.decorators import login_required
from core.models import UserProfile


@login_required   #this tells us that without login u cannot access this page
def admin_home(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('continue_as')  #if the user does not exists

    # allow only admin
    if profile.role != 'admin':
        return redirect('continue_as')  #if user's role is not admin

    return render(request, 'admin_panel/adminHome.html')


#admin residents view

from django.contrib.auth.decorators import login_required
from core.models import UserProfile

@login_required
def admin_residents(request):
    residents = UserProfile.objects.filter(role='resident').select_related('user')

    context = {
        'residents': residents,
        'total_residents': residents.count()
    }

    return render(request, 'admin_panel/adminResidents.html', context)

from django.shortcuts import get_object_or_404, redirect

#admin delete resident view
@login_required
def delete_residents(request, resident_id):
    resident = get_object_or_404(UserProfile, id=resident_id, role='resident')

    # This deletes the user AND the profile (CASCADE)
    resident.user.delete()

    return redirect('admin_panel:admin_residents')


#admin notices view

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notice

@login_required
def admin_notices(request):
    if request.method == "POST":
        Notice.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST['category'],
            created_by=request.user
        )
        return redirect('admin_panel:admin_notices')

    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'admin_panel/adminNotice.html', {
        'notices': notices
    })

#admin should be able to edit notice
# @login_required
# def admin_notices_edit(request, id):
#     notice = get_object_or_404(Notice, id=id)

#     if request.method == "POST":
#         notice.title = request.POST.get('title')
#         notice.description = request.POST.get('description')
#         notice.category = request.POST.get('category')
#         notice.save()
#         return redirect('admin_panel:admin_notices')

#     return render(request, 'admin_panel/adminNoticeEdit.html', {
#         'notice': notice
#     })


#admin should be able to delete notice
@login_required
def admin_notices_delete(request, id):
    notice = get_object_or_404(Notice, id=id)
    notice.is_active = False
    notice.save()
    return redirect('admin_panel:admin_notices')

# Admin Complaints View
from core.models import Complaint
@login_required
def admin_complaint(request):
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    # Base queryset for both page and chart data
    complaints = Complaint.objects.select_related('user').all().order_by('-created_at')
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    # If this is an AJAX request, return chart data JSON (used by dashboard filters)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Category data
        category_data = complaints.values('category').annotate(count=Count('id')).order_by('category')
        category_labels = [item['category'] for item in category_data]
        category_counts = [item['count'] for item in category_data]

        # Status data
        status_data = complaints.values('status').annotate(count=Count('id')).order_by('status')
        status_labels = [item['status'] for item in status_data]
        status_counts = [item['count'] for item in status_data]

        # Date data - group by month
        date_data = complaints.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
        date_labels = [item['month'].strftime('%B %Y') if item['month'] else '' for item in date_data]
        date_counts = [item['count'] for item in date_data]

        return JsonResponse({
            'category_labels': category_labels,
            'category_data': category_counts,
            'status_labels': status_labels,
            'status_data': status_counts,
            'date_labels': date_labels,
            'date_data': date_counts,
        })

    # Regular request (page load)
    all_categories = Complaint.objects.values_list('category', flat=True).distinct()
    all_statuses = [choice[0] for choice in Complaint.STATUS_CHOICES]

    return render(request, 'admin_panel/adminComplaint.html', {
        'complaints': complaints,
        'all_categories': all_categories,
        'all_statuses': all_statuses,
        'selected_category': category_filter,
        'selected_status': status_filter,
    })

#to update complaint status
@login_required
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    new_status = request.POST.get('status')

    if new_status in dict(Complaint.STATUS_CHOICES):
        complaint.status = new_status
        complaint.save()

    # Preserve any filter query parameters when redirecting back
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)

    return redirect('admin_panel:admin_complaint')

@login_required
def admin_services(request):
    return render(request, 'admin_panel/adminServices.html')


from django.utils import timezone
from core.models import Payment, UserProfile
from django.db.models import Sum, Q

@login_required
def admin_maintenance(request):
    month_filter = request.GET.get('month', 'current')
    status_filter = request.GET.get('status', 'all')
    building_filter = request.GET.get('building', 'all')
    search_query = request.GET.get('search', '').strip()
    
    # Base queryset
    payments = Payment.objects.select_related('user', 'user__userprofile').all().order_by('-created_at')
    
    now = timezone.now()
    
    if month_filter == 'current':
        payments = payments.filter(created_at__month=now.month, created_at__year=now.year)
    elif month_filter.isdigit():
        payments = payments.filter(created_at__month=int(month_filter), created_at__year=now.year)
        
    if status_filter == 'paid':
        payments = payments.filter(status__iexact='Success')
    elif status_filter == 'pending':
        payments = payments.filter(status__iexact='Pending')
        
    if building_filter != 'all':
        payments = payments.filter(user__userprofile__wing=building_filter)
        
    if search_query:
        payments = payments.filter(
            Q(user__userprofile__full_name__icontains=search_query) | 
            Q(user__userprofile__flat_no__icontains=search_query)
        )
        
    # Generate Stats for Current Month
    cm_payments = Payment.objects.filter(created_at__month=now.month, created_at__year=now.year)
    total_collection = cm_payments.filter(status__iexact='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    total_flats = UserProfile.objects.filter(role='resident').count()
    paid_count = cm_payments.filter(status__iexact='Success').values('user').distinct().count()
    
    pending_count = total_flats - paid_count
    if pending_count < 0: pending_count = 0
    
    collection_rate = int((paid_count / total_flats * 100)) if total_flats > 0 else 0
    
    context = {
        'payments': payments,
        'total_collection': total_collection,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'overdue_count': 0, # Faux overdue count lacking deadline engine
        'total_flats': total_flats,
        'collection_rate': collection_rate,
        # Sync frontend state
        'month_filter': month_filter,
        'status_filter': status_filter,
        'building_filter': building_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/adminMaintenance.html', context)


@login_required
def admin_rules(request):
    return render(request, 'admin_panel/adminRules.html')


# VIEWS FOR SERVICES
# admin_panel/views.py
# from django.shortcuts import render, redirect, get_object_or_404

@login_required
def admin_services(request):
    """Main services page"""
    services = Service.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Handle form submission
        try:
            # Get form data
            service_type = request.POST.get('service_type')
            custom_service_name = request.POST.get('custom_service_name', '').strip()
            provider_name = request.POST.get('provider_name')
            contact_number = request.POST.get('contact_number')
            email_address = request.POST.get('email_address', '').strip()
            alternate_number = request.POST.get('alternate_number', '').strip()
            service_description = request.POST.get('service_description', '').strip()
            address = request.POST.get('address', '').strip()
            available_days = request.POST.get('available_days', '').strip()
            available_hours = request.POST.get('available_hours', '').strip()
            service_id = request.POST.get('service_id')  # For editing
            
            # # Validation
            # if not service_type or not provider_name or not contact_number:
            #     messages.error(request, 'Please fill in all required fields!')
            #     return redirect('admin_panel:admin_services')
            
            # if service_type == 'other' and not custom_service_name:
            #     messages.error(request, 'Custom service name is required when service type is "Other"!')
            #     return redirect('admin_panel:admin_services')
            
            # Create or update service
            if service_id:
                # Edit existing service
                service = get_object_or_404(Service, id=service_id, is_active=True)
                service.service_type = service_type
                service.custom_service_name = custom_service_name if custom_service_name else None
                service.provider_name = provider_name
                service.contact_number = contact_number
                service.email_address = email_address if email_address else None
                service.alternate_number = alternate_number if alternate_number else None
                service.service_description = service_description if service_description else None
                service.address = address if address else None
                service.available_days = available_days if available_days else None
                service.available_hours = available_hours if available_hours else None
                service.save()
                messages.success(request, f'Service "{service.get_service_name()}" updated successfully!')
            else:
                # Create new service
                service = Service.objects.create(
                    service_type=service_type,
                    custom_service_name=custom_service_name if custom_service_name else None,
                    provider_name=provider_name,
                    contact_number=contact_number,
                    email_address=email_address if email_address else None,
                    alternate_number=alternate_number if alternate_number else None,
                    service_description=service_description if service_description else None,
                    address=address if address else None,
                    available_days=available_days if available_days else None,
                    available_hours=available_hours if available_hours else None,
                )
                messages.success(request, f'Service "{service.get_service_name()}" added successfully!')
            
            return redirect('admin_panel:admin_services')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('admin_panel:admin_services')
    
    context = {
        'services': services,
    }
    return render(request, 'admin_panel/adminServices.html', context)

@login_required
def delete_service(request, service_id):
    """Delete service (soft delete)"""
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id, is_active=True)
        service_name = service.get_service_name()
        service.is_active = False
        service.save()
        messages.success(request, f'Service "{service_name}" deleted successfully!')
    
    return redirect('admin_panel:admin_services')

@login_required
def get_service_data(request, service_id):
    """Get service data as JSON for editing"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    data = {
        'id': service.id,
        'service_type': service.service_type,
        'custom_service_name': service.custom_service_name or '',
        'provider_name': service.provider_name,
        'contact_number': service.contact_number,
        'email_address': service.email_address or '',
        'alternate_number': service.alternate_number or '',
        'service_description': service.service_description or '',
        'address': service.address or '',
        'available_days': service.available_days or '',
        'available_hours': service.available_hours or '',
    }
    return JsonResponse(data)


# RULES VIEW
@login_required
def admin_rules(request):
    if request.method == "POST":
        category_val = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not all([category_val, title, description]):
            messages.error(request, 'All fields are required.')
        else:
            try:
                Rule.objects.create(
                    category=category_val,
                    title=title,
                    description=description
                )
                messages.success(request, 'Rule created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating rule: {str(e)}')

        return redirect('admin_panel:admin_rules')

    rules = Rule.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/adminRules.html', {
        'rules': rules,
    })


@login_required
def delete_rule(request, rule_id):
    rule = get_object_or_404(Rule, id=rule_id)
    rule.delete()
    return redirect('admin_panel:admin_rules')

# LOGOUT VIEW IT IS
def admin_logout(request):
    logout(request)
    return redirect('admin_panel:admin_login')


@login_required
@csrf_exempt
def admin_profile(request):
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
        messages.success(request, 'Your admin profile was successfully updated!')
        return redirect('admin_panel:admin_profile')
        
    return render(request, 'admin_panel/adminProfile.html')