
// When a user clicks the edit button on a goal,
// the goal is hidden and the editable form is shown.
$(".edit-goal-btn").on("click", (evt) => {
    const goalId = evt.target.dataset.goalId;
    $(`#goal-${goalId}`).hide();
    $(`#editable-goal-${goalId}`).show();
});

// When a user clicks the cancel button, editable form is hidden
// and the goal is shown without any changes.
$(".cancel-edit-btn").on("click", (evt) => {
    evt.preventDefault();
    const goalId = evt.target.dataset.goalId;
    $(`#goal-${goalId}`).show();
    $(`#editable-goal-${goalId}`).hide();
});

// When a user clicks the delete button, they're asked if they
// want to delete the goal. If so, goal is deleted in database
// and page is relaoded to reflect change.
$(".delete-goal-btn").on("click", (evt) => {
    result = window.confirm("Are you sure you want to delete this goal?");

    if (result) {
        const goalId = evt.target.dataset.goalId;
        $.post("/dietitian/delete/goal", { goal: goalId }, () => {
            location.reload(true);
        });
    };
});
