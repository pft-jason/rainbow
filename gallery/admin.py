from django.contrib import admin
from .models import Image, Category, Tag, OfficialTag

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'moderated')
    list_filter = ('moderated', 'categories', 'tags')
    search_fields = ('title',)

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(OfficialTag)
