// Drawer questions: display the answer rules for the corresponding question types
if (
    (window.location.href).indexOf('question/add') != -1
    || (window.location.href).indexOf('question/edit') != -1
    || (window.location.href).indexOf('question/create') != -1) {
    const typeQuestionOptions = document.getElementById("id_type");
    var rulesForResponseChoiceQuestions = document.querySelector("#id_response_choices-FORMS").closest(".object")
    var rulesForMultipleChoiceQuestion = document.querySelector("#id_max_multiple_choices").closest(".object")
    var rulesForClosedWithScaleQuestion = document.querySelector("#id_categories-ADD").closest(".object")
    try {
        var rulesForPercentageQuestion = document.querySelector("#id_percentage_ranges-TOTAL_FORMS").closest(".object")
    } catch {
        var rulesForPercentageQuestion = document.createElement("div");
    }


    function responseRules(questionType) {
        if (questionType == "unique_choice" ||
            questionType == "closed_with_ranking" ||
            questionType == "multiple_choice" ||
            questionType == "closed_with_scale") {
            rulesForResponseChoiceQuestions.style.display = "block";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMultipleChoiceQuestion.style.display = "none";
            rulesForPercentageQuestion.style.display = "none";
            if (questionType == "multiple_choice") {
                rulesForMultipleChoiceQuestion.style.display = "block";
            } else if (questionType == "closed_with_scale") {
                rulesForClosedWithScaleQuestion.style.display = "block";
            }
        } else if (questionType == "boolean") {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "block";
            rulesForMultipleChoiceQuestion.style.display = "none";
            rulesForPercentageQuestion.style.display = "none";
        } else if (questionType == "percentage") {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMultipleChoiceQuestion.style.display = "none";
            rulesForPercentageQuestion.style.display = "block";
        } else {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMultipleChoiceQuestion.style.display = "none";
            rulesForPercentageQuestion.style.display = "none";
        }
    }

    responseRules(typeQuestionOptions.value)

    typeQuestionOptions.addEventListener("change", function () {
        responseRules(typeQuestionOptions.value)
    });
}
