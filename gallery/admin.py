from django.contrib import admin
from .models import Image, Category, Tag, OfficialTag

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'moderated')
    list_filter = ('moderated', 'categories', 'tags')
    search_fields = ('title',)

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(OfficialTag)
