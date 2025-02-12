from django.contrib import admin
from .models import PriceTrack

@admin.register(PriceTrack)
class PriceTrackAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'url_link', 'target_price', 'last_checked_price', 'email', 'progress', 'created_at')
    list_filter = ('progress', 'created_at')
    search_fields = ('url_link', 'email', 'product_name')
    readonly_fields = ('created_at', 'last_checked_price', 'product_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product_name', 'url_link', 'target_price', 'last_checked_price')
        }),
        ('User Information', {
            'fields': ('email', 'progress')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
