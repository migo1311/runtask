from django.contrib import admin
from .models import CSVFile, Member, Leader
from .models import Task

admin.site.register(Task)

@admin.register(CSVFile)
class CSVFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
    search_fields = ('file',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name')
    
    def username(self, obj):
        return obj.user.username
    
    def email(self, obj):
        return obj.user.email
    
    def full_name(self, obj):
        return obj.user.get_full_name()

@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name')
    
    def username(self, obj):
        return obj.user.username
    
    def email(self, obj):
        return obj.user.email
    
    def full_name(self, obj):
        return obj.user.get_full_name()