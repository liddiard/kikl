from django.contrib import admin
from shortener.models import Adjective, Noun, Link


class AdjectiveAdmin(admin.ModelAdmin):
    pass


admin.site.register(Adjective, AdjectiveAdmin)


class NounAdmin(admin.ModelAdmin):
    pass


admin.site.register(Noun, NounAdmin)


class LinkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Link, LinkAdmin)
