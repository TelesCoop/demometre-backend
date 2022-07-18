# from typing import Dict, Callable
#
# DATA_FN_BY_QUESTION_TYPE: Dict[str, Callable] = {
#     QuestionType.BOOLEAN.value: get_data_of_boolean_question,  # type: ignore
#     # QuestionType.UNIQUE_CHOICE.value: get_score_of_unique_choice_question,  # type: ignore
#     # QuestionType.MULTIPLE_CHOICE.value: get_score_of_multiple_choice_question,  # type: ignore
#     # QuestionType.PERCENTAGE.value: get_score_of_percentage_question,  # type: ignore
#     # QuestionType.CLOSED_WITH_SCALE.value: get_score_of_closed_with_scale_question,  # type: ignore
# }
#
#
# def get_data_of_boolean_question(queryset):
#     base_queryset = {
#         "participationresponses__participation__user__is_unknown_user": False,
#         "participationresponses__participation__assessment_id": assessment_pk,
#         "participationresponses__question__profiling_question": False,
#     }
