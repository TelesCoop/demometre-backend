import datetime
import random
from typing import Optional

import factory

from my_auth.models import User
from open_democracy_back.models import (
    Question,
    AssessmentType,
    Criteria,
    Marker,
    Pillar,
    ParticipationResponse,
    Participation,
    Assessment,
    Role,
    Municipality,
    Department,
    Region,
    Response,
    AssessmentResponse,
    ResponseChoice,
    Score,
    PercentageRange,
    Category,
    ClosedWithScaleCategoryResponse,
    NumberRange,
)
from open_democracy_back.utils import (
    QuestionObjectivity,
    QuestionMethod,
    InitiatorType,
    ManagedAssessmentType,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    password: Optional[str] = factory.Faker("password")
    first_name: str = factory.Faker("first_name")
    last_name: str = factory.Faker("last_name")
    email: str = factory.Faker("email")
    username: str = factory.LazyAttribute(lambda user: user.email)
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        self.set_password("password")
        self.save()


class PillarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pillar

    code: str = factory.LazyAttribute(lambda a: str(random.randint(1, 20)))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")


class MarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Marker

    code: str = factory.LazyAttribute(lambda a: str(random.randint(1, 20)))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")
    pillar = factory.SubFactory(PillarFactory)


class CriteriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Criteria

    code: str = factory.LazyAttribute(lambda a: str(random.randint(1, 20)))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")
    marker = factory.SubFactory(MarkerFactory)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    code: str = factory.LazyAttribute(lambda a: str(random.randint(1, 20)))
    name: str = factory.Faker("name")
    question_statement: str = factory.Faker("text")
    mandatory: bool = False
    description: str = factory.Faker("text")
    comments: str = factory.Faker("text")
    criteria = factory.SubFactory(CriteriaFactory)
    objectivity = QuestionObjectivity.SUBJECTIVE
    method = QuestionMethod.QUANTITATIVE
    profiling_question: bool = False

    @factory.post_generation
    def set_assessment_types(self, create, extracted, **kwargs):
        if create:
            if not extracted:
                self.assessment_types.set(AssessmentType.objects.all())
            else:
                self.assessment_types.set(extracted)


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    name: str = factory.Faker("name")
    description: str = factory.Faker("text")


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    name: str = factory.Faker("name")
    code: str = factory.Faker("zipcode")


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name: str = factory.Faker("name")
    code: str = factory.Faker("zipcode")
    region = factory.SubFactory(RegionFactory)


class MunicipalityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Municipality

    name: str = factory.Faker("name")
    code: str = factory.Faker("zipcode")
    department: str = factory.SubFactory(DepartmentFactory)

    population: int = factory.Faker("random_int")


class AssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assessment

    initiated_by_user = factory.SubFactory(UserFactory)
    municipality = factory.SubFactory(MunicipalityFactory)
    initiator_type = InitiatorType.INDIVIDUAL
    initialized_to_the_name_of: str = factory.Faker("name")
    initialization_date = factory.lazy_attribute(lambda o: datetime.date.today())

    calendar: str = factory.Faker("paragraph")
    context: str = factory.Faker("paragraph")
    objectives: str = factory.Faker("paragraph")
    stakeholders: str = factory.Faker("paragraph")

    @factory.post_generation
    def set_assessment_type(self, create, extracted, **kwargs):
        if create:
            if not extracted:
                self.assessment_type = AssessmentType.objects.first()
            else:
                self.assessment_type = extracted


class AssessmentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssessmentType

    assessment_type = ManagedAssessmentType.PARTICIPATIVE
    for_who = factory.Faker("text")
    what = factory.Faker("text")
    for_what = factory.Faker("text")
    results = factory.Faker("text")
    price = factory.Faker("random_int")


class ParticipationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participation

    user = factory.SubFactory(UserFactory)
    assessment = factory.SubFactory(AssessmentFactory)
    role = factory.SubFactory(RoleFactory)
    consent: bool = True


class ScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Score

    associated_score = factory.Faker("random_int", min=1, max=4)


class PercentageRangeFactory(ScoreFactory):
    class Meta:
        model = PercentageRange

    question = factory.SubFactory(QuestionFactory)
    lower_bound: int = factory.Faker("random_int", min=0, max=100)
    upper_bound: int = factory.Faker("random_int", min=0, max=100)


class NumberRangeFactory(ScoreFactory):
    class Meta:
        model = NumberRange

    question = factory.SubFactory(QuestionFactory)
    lower_bound: float = factory.Faker("random_float", min=0, max=100)
    upper_bound: float = factory.Faker("random_float", min=0, max=100)


class ResponseChoiceFactory(ScoreFactory):
    class Meta:
        model = ResponseChoice

    question = factory.SubFactory(QuestionFactory)
    response_choice = factory.Faker("text")
    description = factory.Faker("text")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    question = factory.SubFactory(QuestionFactory)
    category = factory.Faker("text")


class ResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Response

    question = factory.SubFactory(QuestionFactory)
    has_passed: bool = False


class ParticipationResponseFactory(ResponseFactory):
    class Meta:
        model = ParticipationResponse

    participation = factory.SubFactory(ParticipationFactory)

    @factory.post_generation
    def assessment(self, create, extracted, **kwargs):
        if create and extracted:
            participation = self.participation
            participation.assessment = extracted
            participation.save()

    @factory.post_generation
    def multiple_choice_response(self, create, extracted, **kwargs):
        if create and extracted:
            self.multiple_choice_response.set(extracted)


class ClosedWithScaleCategoryResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClosedWithScaleCategoryResponse

    category = factory.SubFactory(CategoryFactory)
    response_choice = factory.SubFactory(ResponseChoiceFactory)


class AssessmentResponseFactory(ResponseFactory):
    class Meta:
        model = AssessmentResponse

    assessment = factory.SubFactory(AssessmentFactory)
    answered_by = factory.SubFactory(UserFactory)
