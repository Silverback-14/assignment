from django.urls import path
from .views import (
    UserRegistrationView, 
    UserListView, 
    ContactListView, 
    UserDetailView, 
    ContactDetailView, 
    MarkSpamView, 
    PhoneTokenObtainPairView,
    SearchByNameView,
    SearchByPhoneNumberView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # User-related API endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Contact-related API endpoints
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),

    # Spam reporting
    path('mark-spam/', MarkSpamView.as_view(), name='mark-spam'),

    # Search
    path('search/name/', SearchByNameView.as_view(), name='search-by-name'),
    path('search/phone/', SearchByPhoneNumberView.as_view(), name='search-by-phone'),

    # Token-based authentication
    path("token/", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]