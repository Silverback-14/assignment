# api/views.py
from .serializers import PhoneTokenObtainPairSerializer, SpamNumberSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework import generics, status
from rest_framework.response import Response
from .models import SpamReport, User, Contact
from .serializers import UserSerializer, ContactSerializer, UserRegistrationSerializer
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

# List and Create Users


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned users to the currently authenticated user,
        by filtering against a `user_id` query parameter in the URL.
        """
        user = self.request.user  # This is the authenticated user
        print(f"Authenticated user: {user}")  #
        # You could restrict the query to only show users related to the authenticated user
        # Or if you want to return all users, keep it as `User.objects.all()`
        if user.is_authenticated:
            return User.objects.all()  # Or customize it based on permissions
        return User.objects.none()  # This returns no users if the user is not authenticated


# Retrieve, Update, Delete a User


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

# List and Create Contacts


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data

        # Check if phone number already exists
        if User.objects.filter(phone_number=data['phone_number']).exists():
            return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user (serializer will handle password hashing)
        user_serializer = self.get_serializer(data=data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactListView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]


# Retrieve, Update, Delete a Contact


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]


class MarkSpamView(generics.CreateAPIView):
    serializer_class = SpamNumberSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a spam report
        SpamReport.objects.create(
            reporter=request.user,
            phone_number=phone_number
        )

        return Response({"message": "Number marked as spam."}, status=status.HTTP_201_CREATED)

# api/views.py


class PhoneTokenObtainPairView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer


class SearchByNameView(generics.ListAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        # First, names starting with the query
        starts_with = Contact.objects.filter(name__istartswith=query)
        # Then, names containing the query but not starting with it
        contains = Contact.objects.filter(
            name__icontains=query).exclude(id__in=starts_with)
        return starts_with.union(contains)


class SearchByPhoneNumberView(generics.ListAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        phone_number = self.request.query_params.get('q', '')
        # Check if a registered user has this phone number
        if User.objects.filter(phone_number=phone_number).exists():
            user = User.objects.get(phone_number=phone_number)
            # Return only that user's info
            return Contact.objects.filter(user=user)
        else:
            # Return all contacts matching the phone number
            return Contact.objects.filter(phone_number=phone_number)
