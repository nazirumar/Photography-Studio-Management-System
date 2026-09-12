from django.db import transaction

from apps.audit.models import AuditLog
from apps.packages.models import Package, PackageAddon, ServiceCategory


def create_package(studio, data, user):
    """Create a new package with optional addons."""
    addons_data = data.pop("addons", [])
    with transaction.atomic():
        package = Package.objects.create(studio=studio, **data)
        for addon in addons_data:
            PackageAddon.objects.create(package=package, **addon)
        AuditLog.objects.create(
            user=user,
            action="package_created",
            entity_type="Package",
            entity_id=str(package.id),
            after_values={"name": package.name, "price": str(package.price)},
        )
        return package


def update_package(package, data, user):
    """Update a package."""
    with transaction.atomic():
        before = {"name": package.name, "price": str(package.price)}
        addons_data = data.pop("addons", None)
        for key, value in data.items():
            setattr(package, key, value)
        package.save()
        if addons_data is not None:
            package.addons.all().delete()
            for addon in addons_data:
                PackageAddon.objects.create(package=package, **addon)
        AuditLog.objects.create(
            user=user,
            action="package_updated",
            entity_type="Package",
            entity_id=str(package.id),
            before_values=before,
            after_values={"name": package.name, "price": str(package.price)},
        )
        return package


def toggle_package_active(package, user):
    """Toggle package active status."""
    package.is_active = not package.is_active
    package.save(update_fields=["is_active", "updated_at"])
    AuditLog.objects.create(
        user=user,
        action="package_toggled",
        entity_type="Package",
        entity_id=str(package.id),
        after_values={"is_active": package.is_active},
    )
    return package


def get_package_addon_total(package, selected_addon_ids=None):
    """Calculate total price for a package with selected addons."""
    total = package.price
    if selected_addon_ids:
        addons = PackageAddon.objects.filter(
            package=package, id__in=selected_addon_ids
        )
        for addon in addons:
            total += addon.price
    return total


def create_service_category(studio, data, user):
    """Create a new service category."""
    category = ServiceCategory.objects.create(studio=studio, **data)
    AuditLog.objects.create(
        user=user,
        action="category_created",
        entity_type="ServiceCategory",
        entity_id=str(category.id),
        after_values={"name": category.name},
    )
    return category
