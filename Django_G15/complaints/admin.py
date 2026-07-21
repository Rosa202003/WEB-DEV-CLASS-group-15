from django.contrib import admin
from .models import Complaint, ComplaintComment, ComplaintHistory, Department, UserProfile

admin.site.register(Department)
admin.site.register(Complaint)
admin.site.register(ComplaintComment)
admin.site.register(ComplaintHistory)
admin.site.register(UserProfile)
