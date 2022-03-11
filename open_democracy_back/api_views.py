from django.http import JsonResponse

from open_democracy_back.models import Assessment


def get_assessment_view(request):
    zip_code = request.GET.get("zip_code")
    assessments = Assessment.objects.filter(
        zip_codes__zip_code=zip_code
    ).prefetch_related("zip_codes")

    assessments = [
        {
            "id": assessment.id,
            "type": assessment.type,
            "type_display": assessment.get_type_display(),
            "zip_codes": [zip_code.zip_code for zip_code in assessment.zip_codes.all()],
        }
        for assessment in assessments
    ]

    return JsonResponse(data={"items": assessments})
