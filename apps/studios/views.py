from django.shortcuts import render


def studio_list(request):
    return render(request, "studios/studio_list.html")
