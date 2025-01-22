from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,EmailVerificationModel

# Register your models here.
# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'age', 'is_staff', 'is_active', 'date_joined')
#     list_filter = ('is_staff', 'is_active', 'date_joined')
#     search_fields = ('username', 'email')
#     ordering = ('-date_joined',)

admin.site.register(EmailVerificationModel)
admin.site.register(CustomUser)