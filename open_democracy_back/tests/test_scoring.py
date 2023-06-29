from django.test import TestCase

from open_democracy_back.factories import (
    QuestionFactory,
    ParticipationResponseFactory,
    AssessmentFactory,
    AssessmentResponseFactory,
)
from open_democracy_back.models import (
    ParticipationResponse,
    SCORE_MAP,
    AssessmentResponse,
)
from open_democracy_back.scoring import get_score_of_boolean_question
from open_democracy_back.utils import QuestionType, QuestionObjectivity


class TestScoring(TestCase):
    def test_participation_response_queryset_works(self):
        question = QuestionFactory(type=QuestionType.BOOLEAN)
        profiling_question = QuestionFactory(
            type=QuestionType.BOOLEAN, profiling_question=True
        )
        assessment = AssessmentFactory()
        bad_responses = [
            ParticipationResponseFactory(
                boolean_response=True, assessment=assessment, question=question
            ),
            ParticipationResponseFactory(
                boolean_response=True,
                assessment=assessment,
                question=profiling_question,
            ),
            ParticipationResponseFactory(
                assessment=assessment, question=question, has_passed=True
            ),
        ]
        bad_responses[0].participation.user.is_unknown_user = True
        bad_responses[0].participation.user.save()

        valid_response = ParticipationResponseFactory(
            boolean_response=True, assessment=assessment, question=question
        )
        participation_responses = ParticipationResponse.objects.accounted_in_assessment(
            assessment.pk
        )
        self.assertEqual(len(participation_responses), 1)
        self.assertEqual(participation_responses[0].id, valid_response.id)

    def test_assessment_response_queryset_works(self):
        question_1 = QuestionFactory(
            type=QuestionType.BOOLEAN, objectivity=QuestionObjectivity.OBJECTIVE
        )
        question_2 = QuestionFactory(
            type=QuestionType.BOOLEAN, objectivity=QuestionObjectivity.OBJECTIVE
        )
        question_3 = QuestionFactory(
            type=QuestionType.BOOLEAN, objectivity=QuestionObjectivity.OBJECTIVE
        )
        assessment = AssessmentFactory()
        valid_assessment_response = AssessmentResponseFactory(
            boolean_response=True, assessment=assessment, question=question_1
        )
        bad_assessment_responses = [
            AssessmentResponseFactory(
                has_passed=True, assessment=assessment, question=question_2
            ),
            AssessmentResponseFactory(
                boolean_response=True, assessment=assessment, question=question_3
            ),
        ]
        bad_assessment_responses[1].answered_by.is_unknown_user = True
        bad_assessment_responses[1].answered_by.save()

        assessment_responses = AssessmentResponse.objects.accounted_in_assessment(
            assessment.pk
        )
        self.assertEqual(len(assessment_responses), 1)
        self.assertEqual(assessment_responses[0].id, valid_assessment_response.id)

    def test_get_score_of_boolean_question_works(self):
        question = QuestionFactory(type=QuestionType.BOOLEAN)
        assessment = AssessmentFactory()
        responses = [
            ParticipationResponseFactory(
                boolean_response=True, assessment=assessment, question=question
            ),
            ParticipationResponseFactory(
                boolean_response=True, assessment=assessment, question=question
            ),
            ParticipationResponseFactory(
                boolean_response=False, assessment=assessment, question=question
            ),
        ]

        score = get_score_of_boolean_question(
            ParticipationResponse.objects.accounted_in_assessment(assessment.pk)
        )
        self.assertEqual(
            score,
            [
                {
                    "question_id": question.id,
                    "question__criteria_id": question.criteria.id,
                    "question__criteria__marker_id": question.criteria.marker.id,
                    "question__criteria__marker__pillar_id": question.criteria.marker.pillar_id,
                    "avg": 0.6666666666666666,
                    "score": SCORE_MAP[2],
                }
            ],
        )
        responses[0].boolean_response = False
        responses[0].save()

        score = get_score_of_boolean_question(
            ParticipationResponse.objects.accounted_in_assessment(assessment.pk)
        )
        self.assertEqual(
            score,
            [
                {
                    "question_id": question.id,
                    "question__criteria_id": question.criteria.id,
                    "question__criteria__marker_id": question.criteria.marker.id,
                    "question__criteria__marker__pillar_id": question.criteria.marker.pillar_id,
                    "avg": 0.3333333333333333,
                    "score": SCORE_MAP[1],
                }
            ],
        )

    def test_get_score_of_unique_choice_question_works(self):
        pass
