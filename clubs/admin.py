from django.contrib import admin
from .models import Category, BookClub, Membership
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(BookClub)
class BookClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'is_private')
    list_filter = ('category', 'is_private')
    search_fields = ('name', 'owner__username')

@admin.register(Membership)
class MebershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')



