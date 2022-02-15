from django.shortcuts import render


def modal_filter_view(request):

    return render(
        request,
        "admin/modal_filter.html",  # html template
        {"trigger": request.GET.get("question_id")},  # html template vars
    )
