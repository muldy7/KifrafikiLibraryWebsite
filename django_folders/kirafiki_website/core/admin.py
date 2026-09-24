from django.contrib import admin
from .models import BugReport

# Register your models here.
#admin.site.register(BugReport) 
# Customize the admin interface text
admin.site.index_title = "Welcome to the Admin Zone"  # Changes the title text on the dashboard
admin.site.site_header = "Kirafiki Library Administration"       # Changes the main top header branding
admin.site.site_title = "The Kirafiki Library Admin Portal"    # Changes the browser tab title

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'submission_date')
    
    # This transforms the ManyToMany field interface for selecting related bugs
    filter_horizontal = ('related_bugs',)

    search_fields = ['title','status', 'severity']
    ordering = ['submission_date'] 