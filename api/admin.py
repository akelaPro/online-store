from django.contrib import admin

from api.models import *
from api.models.review.models import Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'avatar')
    list_display_links = ('email',)
    list_editable = ('avatar',) if 'avatar' in list_display else ()
    list_per_page = 20
    ordering = ('created_at', 'email')
    search_fields = ('email',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'author', 'moderation', 'available')
    list_display_links = ('title',)
    list_editable = ('price', 'moderation', 'available')
    list_filter = ('moderation', 'available', 'categories')
    search_fields = ('title', 'description')
    list_per_page = 20
    filter_horizontal = ('categories',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_display_links = ('user',)
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    list_per_page = 20
    date_hierarchy = 'created_at'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'price')
    list_display_links = ('product',)
    list_filter = ('cart__user',)
    search_fields = ('product__title', 'cart__user__email')
    list_per_page = 20
    raw_id_fields = ('product', 'cart')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_display_links = ('id',)
    list_editable = ('status',)
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('user__email', 'shipping_address')
    date_hierarchy = 'created_at'
    list_per_page = 20
    raw_id_fields = ('user',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_display_links = ('order',)
    list_filter = ('order__status',)
    search_fields = ('product__title', 'order__user__email')
    list_per_page = 20
    raw_id_fields = ('order', 'product')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_display_links = ('product',)
    list_filter = ('rating', 'created_at')
    search_fields = ('product__title', 'user__email', 'comment')
    date_hierarchy = 'created_at'
    list_per_page = 20
    raw_id_fields = ('product', 'user')


@admin.register(ChatRoom)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'is_active', 'created_at')
    list_display_links = ('user',)
    list_filter = ('created_at', 'is_active')
    search_fields = ('user__email',)
    list_per_page = 20
    date_hierarchy = 'created_at'


@admin.register(Message)
class CartAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'content', 'timestamp', 'is_read')
    list_display_links = ('sender',)
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__email',)
    list_per_page = 20
    date_hierarchy = 'timestamp'