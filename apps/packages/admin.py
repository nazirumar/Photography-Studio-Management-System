from django.contrib import admin
from .models import ServiceCategory, Package, PackageAddon


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "studio", "is_active")
    list_filter = ("is_active", "studio")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "is_featured", "studio")
    list_filter = ("is_active", "is_featured", "category", "studio")
    search_fields = ("name",)


@admin.register(PackageAddon)
class PackageAddonAdmin(admin.ModelAdmin):
    list_display = ("name", "package", "price")
    search_fields = ("name",)
