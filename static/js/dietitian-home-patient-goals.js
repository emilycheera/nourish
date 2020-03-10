// When a user clicks the edit button on a goal,
// the goal is hidden and the editable form is shown.
$("body").on("click", "button.edit-goal-btn", (evt) => {
    const goalId = evt.target.dataset.goalId;
    $(`#goal-${goalId}`).hide();
    $(`#editable-goal-${goalId}`).show();
});


// When a user clicks the cancel button, editable form is hidden
// and the goal is shown without any changes.
$("body").on("click", "button.cancel-edit-btn", (evt) => {
    evt.preventDefault();
    const goalId = evt.target.dataset.goalId;
    $(`#goal-${goalId}`).show();
    $(`#editable-goal-${goalId}`).hide();
});

// When a user clicks the delete button, they're asked if they
// want to delete the goal. If so, goal is deleted in database
// and page is relaoded to reflect change.
$("body").on("click", "button.delete-goal-btn", (evt) => {
    result = window.confirm("Are you sure you want to delete this goal?");

    if (result) {
        const goalId = evt.target.dataset.goalId;
        $.post("/delete-goal", { goal: goalId }, () => {
            location.reload(true);
        });
    };
});


const getCurrentGoal = (res) => {
    const timeStamp = (moment(res.current_goal.time_stamp).format("MMM D, YYYY"));
    return `<div id="current-goal-div" class="patient-goals-list mb-5">
                <h4 class="mb-3">Current Goal</h4>
                <div id="goal-${res.current_goal.goal_id}">
                    <div class="goal-container">
                        <div class="goal-content">
                            <p class="post-time mb-2 bold">${timeStamp} ${res.current_goal.edited}</p>
                            <p class="mb-1">${res.current_goal.goal_body}</p>
                            <button class="btn btn-link edit-goal-btn pl-0" data-goal-id="${res.current_goal.goal_id}">Edit</button>
                            <button class="btn btn-link delete-goal-btn" data-goal-id="${res.current_goal.goal_id}">Delete</button>
                        </div>
                    </div>
                </div>
                <div id="editable-goal-${res.current_goal.goal_id}" class="hidden">
                    <div class="goal-container">
                        <div class="goal-content">
                            <form class="edit-goal-form" id="edit-goal-form-${res.current_goal.goal_id}" data-goal-id="${res.current_goal.goal_id}">
                                <div class="form-group mb-1">
                                    <textarea name="goal-body" required class="form-control" rows="4">${res.current_goal.goal_body}</textarea>
                                </div>
                                <div>
                                    <button class="cancel-edit-btn btn btn-link" data-goal-id="${res.current_goal.goal_id}">Cancel</button>
                                    <button type="submit" class="btn btn-link">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>`;
}

const getPastGoal = (res) => {
    if (!res.hasOwnProperty("goal")) {
        $("#past-goals-heading").hide()
        return "";
    };
    const timeStamp = (moment(res.goal.time_stamp).format("MMM D, YYYY"));
    $("#past-goals-heading").show();
    return `<div id="goal-${res.goal.goal_id}">
                <div class="goal-container">
                    <div class="goal-content">
                        <p class="post-time mb-2 bold">${timeStamp} ${res.goal.edited}</p>
                        <p class="mb-1">${res.goal.goal_body}</p>
                        <button class="delete-goal-btn btn btn-link pl-0" data-goal-id="${res.goal.goal_id}">Delete</button>
                    </div>
                </div>
            </div>`;
}


$("#add-goal-form").on("submit", (evt) => {
    evt.preventDefault();
    const patientId = evt.target.dataset.patientId;
    const formValues = $("#add-goal-form").serialize();
    $("#add-goal-form")[0].reset();
    $.post(`/patient/${patientId}/add-goal.json`, formValues, (res) => {
        $("#current-goal-div").replaceWith(getCurrentGoal(res));
        $("#past-goals-div").prepend(getPastGoal(res));
    });
});


$("body").on("submit", "form.edit-goal-form", (evt) => {
    evt.preventDefault();
    const goalId = evt.target.dataset.goalId;
    const formValues = $(`#edit-goal-form-${goalId}`).serialize();
    $.post(`/goal/${goalId}/edit.json`, formValues, (res) => {
        $("#current-goal-div").replaceWith(getCurrentGoal(res));
    });
});
