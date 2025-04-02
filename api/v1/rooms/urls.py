# api/urls.py
from django.urls import path
from .views import RoomListCreateView, RoomDetailView

app_name = "api_v1_rooms"  # ✅ Add this line here

urlpatterns = [
    path('', RoomListCreateView.as_view(), name='room-list-create'),
    path('<uuid:id>/', RoomDetailView.as_view(), name='room-detail'),
]