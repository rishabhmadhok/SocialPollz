from django.contrib import admin
from .models import UserProfile,Topic,Poll,Choice,Comment


# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Topic)
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Comment)