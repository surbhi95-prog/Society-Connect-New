from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('admin_register/', views.admin_register, name='admin_register'),
    path('admin_login/', views.admin_login, name='admin_login'),

    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_residents/', views.admin_residents, name='admin_residents'),
    path('admin_residents/delete/<int:id>/', views.delete_residents, name='delete_residents'),

    path('admin_notices/', views.admin_notices, name='admin_notices'),
    path('admin_notices/delete/<int:id>/', views.admin_notices_delete, name='admin_notices_delete'),

    path('admin_complaint/', views.admin_complaint, name='admin_complaint'),
    path('complaints/<int:complaint_id>/update-status/',
         views.update_complaint_status, name='update_complaint_status'),

    path('admin_services/', views.admin_services, name='admin_services'),
    path('services/get/<int:service_id>/',views.get_service_data,name='get_service_data'),
    path('services/delete/<int:service_id>/',views.delete_service, name='delete'),
    path('admin_maintenance/', views.admin_maintenance, name='admin_maintenance'),

    # RULES URLS
    path('admin_rules/', views.admin_rules, name='admin_rules'),
    path('admin_rules/delete/<int:rule_id>/', views.delete_rule, name='delete_rule'),

    # PROFILE URL
    path('profile/', views.admin_profile, name='admin_profile'),

    # LOGOUT URL
    path('logout/',views.admin_logout,name='admin_logout'),
]
