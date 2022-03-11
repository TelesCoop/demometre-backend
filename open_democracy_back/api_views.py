from django.http import JsonResponse

from open_democracy_back.models import Assessment
from open_democracy_back.data.communes import COMMUNES


def get_assessment_view(request):
    zip_code = request.GET.get("zip_code")
    assessments = Assessment.objects.filter(
        zip_codes__zip_code=zip_code
    ).prefetch_related("zip_codes")

    commune = next(
        commune for commune in COMMUNES if zip_code in commune.get("codesPostaux", [])
    )

    assessments = [
        {
            "id": assessment.id,
            "type": assessment.type,
            "type_display": assessment.get_type_display(),
            "zip_codes": [zip_code.zip_code for zip_code in assessment.zip_codes.all()],
            "department": commune.get("departement"),
            "population": commune.get("population"),
        }
        for assessment in assessments
    ]

    return JsonResponse(data={"items": assessments})
