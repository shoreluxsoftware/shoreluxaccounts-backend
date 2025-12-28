
# Register your models here.


############### admin.py ##############
from django.contrib import admin
from .models import LedgerEntry

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "source_type", "source_id", "debit", "credit", "created_at")
    list_filter = ("source_type", "date")
    search_fields = ("source_type", "source_id", "description")
