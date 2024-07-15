from django.contrib import admin
from shortener.models import Adjective, Noun, Link

admin.site.register(Adjective)
admin.site.register(Noun)

class LinkAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid',)

admin.site.register(Link, LinkAdmin)