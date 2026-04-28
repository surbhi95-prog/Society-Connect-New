from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Notice(models.Model):

    CATEGORY_CHOICES = [
        ('urgent', 'Urgent'),
        ('event', 'Event'),
        ('general', 'General'),
        ('maintenance', 'Maintenance'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Service(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('carpenter', 'Carpenter'),
        ('painter', 'Painter'),
        ('cleaner', 'Cleaner'),
        ('gardener', 'Gardener'),
        ('security', 'Security'),
        ('pest-control', 'Pest Control'),
        ('ac-repair', 'AC Repair'),
        ('other', 'Other'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Required fields
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    custom_service_name = models.CharField(max_length=100, blank=True, null=True)
    provider_name = models.CharField(max_length=200)
    contact_number = models.CharField(validators=[phone_regex], max_length=17)
    
    # Optional fields
    email_address = models.EmailField(blank=True, null=True)
    alternate_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    service_description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    available_days = models.CharField(max_length=100, blank=True, null=True)
    available_hours = models.CharField(max_length=100, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.service_type == 'other' and self.custom_service_name:
            return f"{self.custom_service_name} - {self.provider_name}"
        return f"{self.get_service_type_display()} - {self.provider_name}"
    
    def get_service_name(self):
        if self.service_type == 'other' and self.custom_service_name:
            return self.custom_service_name
        return self.get_service_type_display()
    
    def get_icon_class(self):
        icon_map = {
            'plumber': 'fa-wrench',
            'electrician': 'fa-bolt',
            'carpenter': 'fa-hammer',
            'painter': 'fa-paint-roller',
            'cleaner': 'fa-broom',
            'gardener': 'fa-seedling',
            'security': 'fa-shield-halved',
            'pest-control': 'fa-bug',
            'ac-repair': 'fa-fan',
            'other': 'fa-circle-info',
        }
        return icon_map.get(self.service_type, 'fa-wrench')
    
# RULES MODEL

class Rule(models.Model):
    CATEGORY_CHOICES = [
        ('parking', 'Parking & Vehicle Management'),
        ('rental', 'Rental & Tenants'),
        ('noise', 'Noise & Community Behaviour'),
        ('waste', 'Waste Management'),
        ('facilities', 'Facilities Usage'),
        ('security', 'Security & Visitors'),
        ('fire', 'Fire Safety'),
        ('pets', 'Pets Policy'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
