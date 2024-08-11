from django.contrib import admin
from .models import JobApp


# Register your models here.
@admin.register(JobApp)
class JobAppAdmin(admin.ModelAdmin):
    fields = ('title', 'job_status', 'job_number', 'description', 'company', 'payrate',
              'location_type', 'city', 'state', 'contractor_name', 'job_source', 'job_url', 'user')
    list_display = ('title', 'applied_dt', 'job_status', 'job_number', 'company', 'location_type', 'city', 'state')
    list_filter = ('applied_dt', 'job_status', 'location_type', 'job_source', 'user')
    ordering = ('-applied_dt',)
    search_fields = ('title', 'company', 'description', 'job_number', 'city', 'state')
