// Drawer questions: display the answer rules for the corresponding question types
if(
    (window.location.href).indexOf('question/add') != -1
    || (window.location.href).indexOf('question/edit') != -1
    || (window.location.href).indexOf('profiling/add') != -1
    || (window.location.href).indexOf('profiling/edit') != -1) {
    const typeQuestionOptions = document.getElementById("id_type");
    var responseChoice = document.querySelector("#id_response_choices-FORMS").closest(".object")
    var extremeBounds = document.querySelector("#id_min").closest(".object")

    function responseRules(questionType) {
        if(questionType == "unique_choice" ||
            questionType == "multiple_choice" ||
            questionType == "closed_with_ranking"){
                responseChoice.style.display =  "block";
                extremeBounds.style.display =  "none";

            } else if (questionType == "closed_with_scale") {
                responseChoice.style.display =  "none";
                extremeBounds.style.display =  "block";
            } else {
                responseChoice.style.display =  "none";
                extremeBounds.style.display =  "none";
            }
    }

    responseRules(typeQuestionOptions.value)

    typeQuestionOptions.addEventListener("change", function() {
        responseRules(typeQuestionOptions.value)
    });
}