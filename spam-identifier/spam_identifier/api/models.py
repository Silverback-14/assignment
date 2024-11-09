from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128)  # Storing the hashed password
    is_active = models.BooleanField(default=True)

    # def save(self, *args, **kwargs):
    #     # Only hash the password if it’s not already hashed
    #     if not self.password.startswith("pbkdf2"):
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Contact(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    is_spam = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SpamReport(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} reported by {self.reporter.name}"
