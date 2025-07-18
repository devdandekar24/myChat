
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from a_home.views import *
from django.conf import settings
from a_users.views import profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('allauth.urls')),
    path('',include('a_rtchat.urls')),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name='profile'),
]

# only for development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
