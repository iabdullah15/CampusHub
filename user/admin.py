from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm 
from .models import CustomUser

# Register your models here.


class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm #Create user form
    form = CustomUserChangeForm       #Update user form
    model = CustomUser
    list_display = ("email", "is_staff", "is_active", "department", "username")
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password", "department", "username")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
