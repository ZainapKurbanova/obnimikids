from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"Looking for sw.js in: {os.path.join(settings.BASE_DIR, 'sw.js')}")
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('favorites/', include('favorites.urls')),
    path('notifications/', include('notifications.urls')),
    path('sw.js', serve, {'document_root': settings.BASE_DIR, 'path': 'sw.js'}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)