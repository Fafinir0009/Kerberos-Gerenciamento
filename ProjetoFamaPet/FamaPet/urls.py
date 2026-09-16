from django.contrib import admin
from django.urls import path, include
from kerberos import views
from kerberos.views.ViewHome import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', home , name='home'),
    path('kerberos/', include('kerberos.urls')),
]
