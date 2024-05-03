from django.contrib import admin

from chronicle.models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass
