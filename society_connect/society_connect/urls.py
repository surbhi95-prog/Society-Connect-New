from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),   
    path('admin_panel/', include(('admin_panel.urls','admin_panel'),namespace='admin_panel')),   
    
]
