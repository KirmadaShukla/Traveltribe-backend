import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    trips_completed = models.PositiveIntegerField(default=0)
    trips_cancelled = models.PositiveIntegerField(default=0)
    total_trips_joined = models.PositiveIntegerField(default=0)
    total_reviews_received = models.PositiveIntegerField(default=0)
    total_reviews_given = models.PositiveIntegerField(default=0)
    average_rating_received = models.FloatField(default=None, null=True, blank=True)
    points = models.PositiveIntegerField(default=0)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email