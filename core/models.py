from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from utils.helper import upload_to_model_folder
# Create your models here.



class UserRoleChoices(models.TextChoices):
    """
    Choices for User Roles
    We can add new fields here
    Make sure you apply migration after the changes.

    """
    BUYER = 'buyer', 'Buyer'
    ADMIN = 'admin', 'Admin'

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            **extra_fields
        )


class User(AbstractUser):
    """
    We are overriding the AbstractUser model and add some of our required fields
    """
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRoleChoices.choices, default=UserRoleChoices.BUYER)
    full_name = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted"
    )

    # restore tracking
    last_restored_date = models.DateTimeField(null=True, blank=True)
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_restored"
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Mark object as deleted instead of actually deleting"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self, user=None):
        """Restore a soft-deleted object"""
        self.is_deleted = False
        self.last_restored_date = timezone.now()
        self.restored_by = user

        # optional cleanup
        self.deleted_at = None
        self.deleted_by = None

        self.save()



class Property(BaseModel):
    """
    Represents a real estate property listed in the system.
    Includes pricing with optional discount calculation.
    """

    title = models.CharField(
        max_length=255,
        help_text="Title or short name of the property."
    )

    location = models.CharField(
        max_length=255,
        help_text="Geographical location or address of the property."
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Original listing price."
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Discount amount applied to the property."
    )

    actual_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text="Final price after applying discount."
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional detailed description of the property."
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def save(self, *args, **kwargs):
        """
        Override save to calculate actual price.
        """
        # Prevent negative final price
        if self.discount > self.price:
            self.discount = self.price  # small safeguard (human-like fix)

        self.actual_price = self.price - self.discount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.location}) - Rs.{self.actual_price}"



class PropertyImage(BaseModel):
    """
    Stores images associated with a property.

    Supports multiple images per property with optional metadata such as
    ordering, primary image flag, and alt text.
    """

    property = models.ForeignKey(
        "Property",
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Property to which this image belongs."
    )

    image = models.ImageField(
        upload_to=upload_to_model_folder,
        help_text="Uploaded image file for the property."
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional alt text for accessibility and SEO."
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Indicates if this image is the main display image."
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Controls the order in which images are displayed."
    )

    class Meta:
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"
        ordering = ["display_order", "-created_at"]
        indexes = [
            models.Index(fields=["property"]),
        ]

    def __str__(self):
        return f"{self.property.title} - Image {self.id}"



class Favourite(BaseModel):
    """
    Represents a user's favourite (liked) property.

    Ensures that a user cannot favourite the same property multiple times.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favourites",
        help_text="User who marked this property as favourite."
    )

    property = models.ForeignKey(
        "Property",
        on_delete=models.CASCADE,
        related_name="favourited_by",
        help_text="Property that has been favourited."
    )

    class Meta:
        verbose_name = "Favourite"
        verbose_name_plural = "Favourites"
        unique_together = ("user", "property")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["property"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.property.title}"