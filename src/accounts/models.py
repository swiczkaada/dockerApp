from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
from django.db import models



# Create your models here.
#Abstract base class for common fields , role admin, super admin et users

'''
Email 
Username
first_name
last_name
password
permission
is_active
is_staff
is_superuser
date_joined
'''
class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and return a user with an email, username and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.date_joined = timezone.now()
        user.save()
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and return a superuser with an email, username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('permission', 3)

        return self.create_user(email, username, password, **extra_fields)

    def create_admin(self, email, username, password=None, **extra_fields):
        """
        Create and return an admin user with an email, username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('permission', 2)

        return self.create_user(email, username, password, **extra_fields)

    def delete_user(self, user):
        """
        Supprime un utilisateur sauf s'il est super admin ou s'il n'est pas une instance du modèle CustomUser.
        """
        if not isinstance(user, self.model):
            raise ValueError("L'objet fourni n'est pas un utilisateur valide.")
        if user.is_superuser:
            raise ValueError("Impossible de supprimer un superutilisateur.")

        user.delete()

class CustomUser(AbstractUser, PermissionsMixin):
    PERMISSION_CHOICES = (
        (0, 'Aucun accès'),
        (1, 'User'),
        (2, 'Admin'),
        (3, 'Super Admin'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128, unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    permission = models.IntegerField(choices=PERMISSION_CHOICES, default=1)

    def is_user(self):
        return self.permission == 1

    def is_admin(self):
        return self.permission == 2

    def is_super_admin(self):
        return self.permission == 3

    def has_permission(self, permission_level):
        return self.permission >= permission_level

    objects = UserManager()
    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email' # Use email as the identifier for authentication. Replace 'username' with 'email'




'''class CYJE(AbstractUser):
    pass
'''