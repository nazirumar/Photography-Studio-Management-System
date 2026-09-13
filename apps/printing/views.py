from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.services import get_user_studio
from apps.printing.forms import AlbumOrderForm, FrameOrderForm, PrintJobForm
from apps.printing.models import AlbumOrder, FrameOrder, PrintJob, PrintPriceList
from apps.printing.services import (
    approve_album,
    create_album_order,
    create_frame_order,
    create_print_job,
    get_printing_summary,
    update_album_order_status,
    update_frame_order_status,
    update_print_job_status,
)
from apps.projects.models import Project


@login_required
def printing_dashboard(request):
    studio = get_user_studio(request.user)
    summary = get_printing_summary(studio)
    active_prints = PrintJob.objects.filter(
        project__studio=studio
    ).exclude(status="delivered").select_related("project", "client")[:10]
    active_frames = FrameOrder.objects.filter(
        project__studio=studio
    ).exclude(status="delivered").select_related("project")[:10]
    active_albums = AlbumOrder.objects.filter(
        project__studio=studio
    ).exclude(design_status="delivered").select_related("project")[:10]
    return render(request, "printing/dashboard.html", {
        "summary": summary,
        "active_prints": active_prints,
        "active_frames": active_frames,
        "active_albums": active_albums,
    })


@login_required
def print_job_create(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    if request.method == "POST":
        form = PrintJobForm(request.POST)
        if form.is_valid():
            create_print_job(project, form.cleaned_data, user=request.user)
            messages.success(request, "Print job created.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = PrintJobForm()
    return render(request, "printing/print_job_form.html", {
        "form": form, "project": project, "title": "New Print Job",
    })


@login_required
def print_job_status(request, pk):
    studio = get_user_studio(request.user)
    print_job = get_object_or_404(PrintJob.objects.select_related("project"), pk=pk, project__studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            update_print_job_status(print_job, new_status, user=request.user)
            messages.success(request, f"Print job status updated to {new_status}.")
    return redirect("projects:detail", pk=print_job.project.pk)


@login_required
def frame_order_create(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    if request.method == "POST":
        form = FrameOrderForm(request.POST)
        if form.is_valid():
            create_frame_order(project, form.cleaned_data, user=request.user)
            messages.success(request, "Frame order created.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = FrameOrderForm()
    return render(request, "printing/frame_order_form.html", {
        "form": form, "project": project, "title": "New Frame Order",
    })


@login_required
def frame_order_status(request, pk):
    studio = get_user_studio(request.user)
    frame = get_object_or_404(FrameOrder.objects.select_related("project"), pk=pk, project__studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            update_frame_order_status(frame, new_status, user=request.user)
            messages.success(request, f"Frame order status updated to {new_status}.")
    return redirect("projects:detail", pk=frame.project.pk)


@login_required
def album_order_create(request, project_pk):
    studio = get_user_studio(request.user)
    project = get_object_or_404(Project, pk=project_pk, studio=studio)
    if request.method == "POST":
        form = AlbumOrderForm(request.POST)
        if form.is_valid():
            create_album_order(project, form.cleaned_data, user=request.user)
            messages.success(request, "Album order created.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = AlbumOrderForm()
    return render(request, "printing/album_order_form.html", {
        "form": form, "project": project, "title": "New Album Order",
    })


@login_required
def album_order_status(request, pk):
    studio = get_user_studio(request.user)
    album = get_object_or_404(AlbumOrder.objects.select_related("project"), pk=pk, project__studio=studio)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            update_album_order_status(album, new_status, user=request.user)
            messages.success(request, f"Album status updated to {new_status}.")
    return redirect("projects:detail", pk=album.project.pk)


@login_required
def album_approve(request, pk):
    studio = get_user_studio(request.user)
    album = get_object_or_404(AlbumOrder.objects.select_related("project"), pk=pk, project__studio=studio)
    if request.method == "POST":
        approve_album(album, user=request.user)
        messages.success(request, "Album approved and sent for production.")
    return redirect("projects:detail", pk=album.project.pk)


@login_required
def price_list(request):
    studio = get_user_studio(request.user)
    prices = PrintPriceList.objects.filter(studio=studio, is_active=True)
    by_type = {
        "print": prices.filter(product_type="print"),
        "frame": prices.filter(product_type="frame"),
        "album": prices.filter(product_type="album"),
    }
    return render(request, "printing/price_list.html", {"by_type": by_type})


@login_required
def price_list_add(request):
    studio = get_user_studio(request.user)
    if request.method == "POST":
        price = PrintPriceList.objects.create(
            studio=studio,
            product_type=request.POST.get("product_type", "print"),
            name=request.POST.get("name", ""),
            size=request.POST.get("size", ""),
            paper_type=request.POST.get("paper_type", ""),
            internal_cost=request.POST.get("internal_cost", 0),
            selling_price=request.POST.get("selling_price", 0),
            sort_order=request.POST.get("sort_order", 0),
        )
        messages.success(request, f"Price item '{price.name}' added.")
        return redirect("printing:price_list")
    return render(request, "printing/price_list_form.html", {"title": "Add Price Item"})


@login_required
def price_list_edit(request, pk):
    studio = get_user_studio(request.user)
    price = get_object_or_404(PrintPriceList, pk=pk, studio=studio)
    if request.method == "POST":
        price.product_type = request.POST.get("product_type", price.product_type)
        price.name = request.POST.get("name", price.name)
        price.size = request.POST.get("size", price.size)
        price.paper_type = request.POST.get("paper_type", price.paper_type)
        price.internal_cost = request.POST.get("internal_cost", price.internal_cost)
        price.selling_price = request.POST.get("selling_price", price.selling_price)
        price.sort_order = request.POST.get("sort_order", price.sort_order)
        price.save()
        messages.success(request, f"Price item '{price.name}' updated.")
        return redirect("printing:price_list")
    return render(request, "printing/price_list_form.html", {"title": "Edit Price Item", "price": price})


@login_required
def price_list_delete(request, pk):
    studio = get_user_studio(request.user)
    price = get_object_or_404(PrintPriceList, pk=pk, studio=studio)
    if request.method == "POST":
        name = price.name
        price.delete()
        messages.success(request, f"Price item '{name}' deleted.")
    return redirect("printing:price_list")
