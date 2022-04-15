# import datetime
# import factory
# import random
# from django.contrib.auth.models import User
# from typing import Optional

# factory.Faker._DEFAULT_LOCALE = "fr_FR"

# class UserFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = User

#     password: Optional[str] = factory.Faker("password")
#     first_name: str = factory.Faker("first_name")
#     last_name: str = factory.Faker("last_name")
#     email: str = factory.Faker("email")
#     is_admin: Optional[bool] = False
#     is_active: Optional[bool] = True

#     @factory.post_generation
#     def set_password(self, create, extracted, **kwargs):
#         self.set_password("password")
#         self.save()


# class AssessmentFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Assessment
