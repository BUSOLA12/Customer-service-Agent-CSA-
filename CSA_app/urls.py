# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import whatsapp_webhook, PropertyListAPIView
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', whatsapp_webhook, name='whatsapp_webhook'),
    path('properties/', PropertyListAPIView.as_view(), name='property-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)