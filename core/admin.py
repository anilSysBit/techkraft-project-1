from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Property, Favourite

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "role",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("full_name", "email")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        ("Account Information", {
            "fields": ("email", "password")
        }),
        ("Personal Information", {
            "fields": ("full_name", "role")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        ("Create User", {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
            ),
        }),
    )


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "location",
        "price",
        "discount",
        "actual_price",
        "is_deleted",
        "created_at",
        "created_by",
    )
    list_filter = (
        "is_deleted",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "title",
        "location",
        "description",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "actual_price",
        "created_at",
        "updated_at",
        "deleted_at",
        "last_restored_date",
    )
    autocomplete_fields = (
        "created_by",
        "deleted_by",
        "restored_by",
    )

    fieldsets = (
        ("Property Information", {
            "fields": (
                "title",
                "location",
                "description",
            )
        }),
        ("Pricing", {
            "fields": (
                "price",
                "discount",
                "actual_price",
            )
        }),
        ("Audit Information", {
            "fields": (
                "created_by",
                "created_at",
                "updated_at",
            )
        }),
        ("Soft Delete Information", {
            "fields": (
                "is_deleted",
                "deleted_at",
                "deleted_by",
                "last_restored_date",
                "restored_by",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "property",
        "is_deleted",
        "created_at",
        "created_by",
    )
    list_filter = (
        "is_deleted",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__email",
        "user__full_name",
        "property__title",
        "property__location",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "deleted_at",
        "last_restored_date",
    )
    autocomplete_fields = (
        "user",
        "property",
        "created_by",
        "deleted_by",
        "restored_by",
    )

    fieldsets = (
        ("Favourite Information", {
            "fields": (
                "user",
                "property",
            )
        }),
        ("Audit Information", {
            "fields": (
                "created_by",
                "created_at",
                "updated_at",
            )
        }),
        ("Soft Delete Information", {
            "fields": (
                "is_deleted",
                "deleted_at",
                "deleted_by",
                "last_restored_date",
                "restored_by",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)