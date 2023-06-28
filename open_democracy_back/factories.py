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
)
from open_democracy_back.utils import QuestionObjectivity, QuestionMethod, InitiatorType


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    password: Optional[str] = factory.Faker("password")
    first_name: str = factory.Faker("first_name")
    last_name: str = factory.Faker("last_name")
    email: str = factory.Faker("email")
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True
    activation_key: Optional[bool] = False

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        self.set_password("password")
        self.save()


class PillarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pillar

    code: int = factory.LazyAttribute(lambda a: random.randint(1, 20))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")


class MarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Marker

    code: int = factory.LazyAttribute(lambda a: random.randint(1, 20))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")
    pillar = factory.SubFactory(PillarFactory)


class CriteriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Criteria

    code: int = factory.LazyAttribute(lambda a: random.randint(1, 20))
    name: str = factory.Faker("name")
    description: str = factory.Faker("text")
    marker = factory.SubFactory(MarkerFactory)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    code: int = factory.LazyAttribute(lambda a: random.randint(1, 20))
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


class AssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assessment

    initiated_by_user = factory.SubFactory(UserFactory)
    initiator_type = InitiatorType.INDIVIDUAL
    initialized_to_the_name_of: str = factory.Faker("name")
    initialization_date = factory.lazy_attribute(lambda o: datetime.date.today())

    @factory.post_generation
    def set_assessment_type(self, create, extracted, **kwargs):
        if create:
            if not extracted:
                self.assessment_type = AssessmentType.objects.first()
            else:
                self.assessment_type = extracted

    @factory.post_generation
    def set_municipality(self, create, extracted, **kwargs):
        if create:
            if not extracted:
                self.municipality = Municipality.objects.first()
            else:
                self.municipality = extracted


class ParticipationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participation

    user = factory.SubFactory(UserFactory)
    assessment = factory.SubFactory(AssessmentFactory)
    role = factory.SubFactory(RoleFactory)
    consent: bool = True


class ResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParticipationResponse

    question = factory.SubFactory(QuestionFactory)
    has_passed: bool = False
    participation = factory.SubFactory(ParticipationFactory)
