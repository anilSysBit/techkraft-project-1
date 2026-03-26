from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
# Create your models here.



class UserRoleChoices(models.TextChoices):
    """
    Choices for User Roles
    We can add new fields here
    Make sure you apply migration after the changes.

    """
    BUYER = 'buyer', 'Buyer'
    ADMIN = 'admin', 'Admin'


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