from django.urls import path
from .views import UserProfileDetailView, UserMeUpdateView, UsersListView

urlpatterns = [
    path('', UsersListView.as_view(), name='users-list'),
    path('me/', UserMeUpdateView.as_view(), name='users-me'),
    path('<int:user_id>/', UserProfileDetailView.as_view(), name='user-detail'),
]
