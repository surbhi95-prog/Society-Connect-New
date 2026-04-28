from django.db import models
from django.contrib.auth.models import User

class Society(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    wing = models.CharField(max_length=50)
    flat_no = models.CharField(max_length=10)
    address = models.TextField()
    
    # Profile Picture
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', null=True, blank=True)

#using foreign key to link UserProfile to Society
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=[('resident', 'Resident'), ('admin', 'Admin')],
        default='resident'
    )
    
    
    def __str__(self):
        return self.user.username


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    #here also linking Complaint to User using ForeignKey

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=200)
    attachment = models.FileField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.id} - {self.category}"

# RULES VIEW
# models.py
class RuleCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Rule(models.Model):
    category = models.ForeignKey(RuleCategory, on_delete=models.CASCADE, related_name='rules')
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


# PAYMENT MODEL
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status}"
