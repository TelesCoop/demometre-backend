// Drawer questions: display expert questions only if assessment is expert type
if (
    (window.location.href).indexOf('assessment/add') != -1
    || (window.location.href).indexOf('assessment/edit') != -1
    || (window.location.href).indexOf('assessment/create') != -1) {
    const typeAssessmentOptions = document.getElementById("id_assessment_type");
    var expertsInputSelect = document.querySelector("#id_experts").closest(".object")
    var royaltyPayedBoolean = document.querySelector("#id_royalty_payed").closest(".object")

    function assessmentTypeDrawerQuestions(assessmentTypeText) {
        if (assessmentTypeText == "Evaluation avec experts") {
            expertsInputSelect.style.display = "block";
            royaltyPayedBoolean.style.display = "block";
        } else {
            expertsInputSelect.style.display = "none";
            royaltyPayedBoolean.style.display = "none";
        }
    }

    assessmentTypeDrawerQuestions(typeAssessmentOptions.options[typeAssessmentOptions.selectedIndex].text)

    typeAssessmentOptions.addEventListener("change", function () {
        assessmentTypeDrawerQuestions(typeAssessmentOptions.options[typeAssessmentOptions.selectedIndex].text)
    });
}
