from django.contrib import admin
from .models import Contractor


# Register your models here.
@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'phone', 'email')
    ordering = ('-created_dt',)
    search_fields = ('name', 'company', 'phone', 'email')
