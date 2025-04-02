from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/rooms/', include('api.v1.rooms.urls', namespace='api_v1_rooms')),  # ✅ Now it works
]
