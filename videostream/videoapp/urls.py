from django.urls import path
from .views import video_feed, index, process_image, custom_registration_view, logout_view, stopServerStream
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('video_feed/', video_feed, name='video_feed'),
    path('process_image/', process_image, name='process_image'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('registration/', custom_registration_view, name='registration'),
    path('logout/', logout_view, name='logout'),
    path('stop_server_stream/', stopServerStream, name='stop_server_stream'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)