from django.contrib import admin
from .models import CustomUser, Document, Vote_Document
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Document)
admin.site.register(Vote_Document)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'uuid', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('email', 'uuid')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'groups')}),
    )

# 文档模型Admin界面
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'upload_date', 'public')
    list_filter = ('public', 'upload_date')
    search_fields = ('name', 'user__username')

# 评价记录模型Admin界面
class VoteDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'fact_choice', 'style_choice', 'created_at')
    list_filter = ('fact_choice', 'style_choice', 'created_at')