// Drawer questions: display expert questions only if assessment is expert type
if (
    (window.location.href).indexOf('assessment/add') != -1
    || (window.location.href).indexOf('assessment/edit') != -1
    || (window.location.href).indexOf('assessment/create') != -1) {
    const assessmentTypeTitle = document.getElementById("id_assessment_type-title");
    var expertsInputSelect = document.getElementById("panel-experts-section")
    var royaltyPayedBoolean = document.getElementById("panel-royalty_payed-section")

    function assessmentTypeDrawerQuestions(assessmentTypeText) {
        if (assessmentTypeText == "Evaluation avec expert") {
            expertsInputSelect.style.display = "block";
            royaltyPayedBoolean.style.display = "block";
        } else {
            expertsInputSelect.style.display = "none";
            royaltyPayedBoolean.style.display = "none";
        }
    }

    assessmentTypeDrawerQuestions(assessmentTypeTitle.innerHTML)

    // Allow to check if the assessment title div has changed
    const observer = new MutationObserver(function () {
        assessmentTypeDrawerQuestions(assessmentTypeTitle.innerHTML)
    });
    observer.observe(assessmentTypeTitle, { childList: true, subtree: true });
}
