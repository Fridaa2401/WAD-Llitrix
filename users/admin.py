from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'date_joined', 'profile_picture')
    search_fields = ('username', 'email')
    list_filter = ('is_superuser', 'is_active')

    fieldsets = UserAdmin.fieldsets + (  # Adds fields to the UserAdmin form
        ('Additional Info', {'fields': ('profile_picture', 'bio')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (  # Adds fields to the User creation form
        ('Additional Info', {'fields': ('profile_picture', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)