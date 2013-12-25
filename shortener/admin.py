from django.contrib import admin
from shortener.models import Cursor, Adjective, Noun, Link


class CursorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Cursor, CursorAdmin)


class AdjectiveAdmin(admin.ModelAdmin):
    pass


admin.site.register(Adjective, AdjectiveAdmin)


class NounAdmin(admin.ModelAdmin):
    pass


admin.site.register(Noun, NounAdmin)


class LinkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Link, LinkAdmin)
