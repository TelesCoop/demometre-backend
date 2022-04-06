// Drawer questions: display the answer rules for the corresponding question types
if (
    (window.location.href).indexOf('question/add') != -1
    || (window.location.href).indexOf('question/edit') != -1
    || (window.location.href).indexOf('question/create') != -1) {
    const typeQuestionOptions = document.getElementById("id_type");
    var rulesForResponseChoiceQuestions = document.querySelector("#id_response_choices-FORMS").closest(".object")
    var rulesForMaxResponseChoices = document.querySelector("#id_max_multiple_choices").closest(".object")
    var rulesForClosedWithScaleQuestion = document.querySelector("#id_min").closest(".object")
    try {
        var rulesForBinaryQuestion = document.querySelector("#id_true_associated_score").closest(".object")
    } catch {
        var rulesForBinaryQuestion = document.createElement("div");
    }


    function responseRules(questionType) {
        if (questionType == "unique_choice" ||
            questionType == "multiple_choice" ||
            questionType == "closed_with_ranking") {
            rulesForResponseChoiceQuestions.style.display = "block";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMaxResponseChoices.style.display = "none";
            if (questionType == "multiple_choice") {
                rulesForMaxResponseChoices.style.display = "block";
            }
        } else if (questionType == "closed_with_scale") {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "block";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMaxResponseChoices.style.display = "none";
        } else if (questionType == "boolean") {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "block";
            rulesForMaxResponseChoices.style.display = "none";
        } else {
            rulesForResponseChoiceQuestions.style.display = "none";
            rulesForClosedWithScaleQuestion.style.display = "none";
            rulesForBinaryQuestion.style.display = "none";
            rulesForMaxResponseChoices.style.display = "none";
        }
    }

    responseRules(typeQuestionOptions.value)

    typeQuestionOptions.addEventListener("change", function () {
        responseRules(typeQuestionOptions.value)
    });
}
