from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Comment, Like, PersonalAPIToken, Post, User

@admin.register(User)
class VerityUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Forum", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Forum", {"fields": ("role",)}),)

admin.site.register([Category, Comment, Like, PersonalAPIToken, Post])

