from django.contrib import admin
from shortener.models import Adjective, Noun, Link

admin.site.register(Adjective)
admin.site.register(Noun)

class LinkAdmin(admin.ModelAdmin):
    list_display = ('path', 'target_truncated', 'time_added', 'is_active')
    list_filter = ('is_active',)
    ordering = ('-is_active',)
    readonly_fields = ('uuid', 'time_added')

    def target_truncated(self, obj):
        max_len = 40
        """Truncate the 'target' value to 40 characters if needed, appending an ellipsis."""
        return (obj.target[:max_len] + '…') if len(obj.target) > max_len else obj.target
    target_truncated.short_description = 'Target'

admin.site.register(Link, LinkAdmin)