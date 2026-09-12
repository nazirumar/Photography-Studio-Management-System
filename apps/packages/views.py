from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.packages.forms import PackageForm, PackageSearchForm, ServiceCategoryForm
from apps.packages.models import Package, ServiceCategory


@login_required
def package_list(request):
    studio = get_user_studio(request.user)
    form = PackageSearchForm(request.GET or None)
    form.fields["category"].queryset = ServiceCategory.objects.filter(studio=studio)
    queryset = Package.objects.filter(studio=studio)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        status = form.cleaned_data.get("status")
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category=category)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

    paginator = Paginator(queryset, 20)
    page = request.GET.get("page")
    packages = paginator.get_page(page)

    return render(request, "packages/list.html", {
        "packages": packages,
        "form": form,
        "total_count": queryset.count(),
    })


@login_required
def package_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = PackageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            from apps.packages.services import create_package
            package = create_package(studio=studio, data=data, user=request.user)
            messages.success(request, f"Package {package.name} created.")
            return redirect("packages:detail", pk=package.pk)
    else:
        form = PackageForm()
    return render(request, "packages/form.html", {"form": form, "title": "Add Package"})


@login_required
def package_detail(request, pk):
    studio = get_user_studio(request.user)
    package = get_object_or_404(Package, pk=pk, studio=studio)
    addons = package.addons.all()
    return render(request, "packages/detail.html", {
        "package": package,
        "addons": addons,
    })


@login_required
def package_edit(request, pk):
    studio = get_user_studio(request.user)
    package = get_object_or_404(Package, pk=pk, studio=studio)
    if request.method == "POST":
        form = PackageForm(request.POST, instance=package)
        if form.is_valid():
            from apps.packages.services import update_package
            update_package(package, form.cleaned_data, user=request.user)
            messages.success(request, f"Package {package.name} updated.")
            return redirect("packages:detail", pk=package.pk)
    else:
        form = PackageForm(instance=package)
    return render(request, "packages/form.html", {"form": form, "title": "Edit Package", "package": package})


@login_required
def package_toggle(request, pk):
    studio = get_user_studio(request.user)
    package = get_object_or_404(Package, pk=pk, studio=studio)
    if request.method == "POST":
        from apps.packages.services import toggle_package_active
        toggle_package_active(package, user=request.user)
        messages.success(request, f"Package {package.name} {'activated' if package.is_active else 'deactivated'}.")
    return redirect("packages:detail", pk=pk)


@login_required
def category_list(request):
    studio = get_user_studio(request.user)
    categories = ServiceCategory.objects.filter(studio=studio)
    return render(request, "packages/category_list.html", {"categories": categories})


@login_required
def category_create(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            from apps.packages.services import create_service_category
            create_service_category(studio=studio, data=form.cleaned_data, user=request.user)
            messages.success(request, "Category created.")
            return redirect("packages:categories")
    else:
        form = ServiceCategoryForm()
    return render(request, "packages/category_form.html", {"form": form, "title": "Add Category"})
