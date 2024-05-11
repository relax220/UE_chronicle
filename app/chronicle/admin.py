from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from chronicle.models import Record, Comment


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdminPage(DraggableMPTTAdmin):
    """
    Админ-панель модели комментариев
    """
    list_display = ('tree_actions', 'indented_title', 'record', 'author', 'time_create', 'status')
    mptt_level_indent = 2
    list_display_links = ('record',)
    list_filter = ('time_create', 'time_update', 'author')
    list_editable = ('status',)
