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
    const timeStamp = (moment(res.current_goal.time_stamp).format("MMM D YYYY [at] h:mm A"));
    return `<div id="current-goal-div">
                <div id="goal-${res.current_goal.goal_id}">
                    <p>${timeStamp} ${res.current_goal.edited}</p>
                    <p>${res.current_goal.goal_body}</p>
                    <button class="edit-goal-btn" data-goal-id="${res.current_goal.goal_id}">Edit</button>
                    <button class="delete-goal-btn" data-goal-id="${res.current_goal.goal_id}">Delete</button>
                </div>
                <div id="editable-goal-${res.current_goal.goal_id}" class="hidden-form">
                    <form class="edit-goal-form" id="edit-goal-form-${res.current_goal.goal_id}" data-goal-id="${res.current_goal.goal_id}">
                        <textarea name="goal-body" required rows="4" cols="48">${res.current_goal.goal_body}</textarea>
                        <div>
                            <button class="cancel-edit-btn" data-goal-id="${res.current_goal.goal_id}">Cancel</button>
                            <button type="submit">Update Goal</button>
                        </div>
                    </form>
                </div>
            </div>`;
}

const getPastGoal = (res) => {
    const timeStamp = (moment(res.goal.time_stamp).format("MMM D YYYY [at] h:mm A"));
    return `<div id="goal-${res.goal.goal_id}">
                <p>${timeStamp} ${res.goal.edited}</p>
                <p>${res.goal.goal_body}</p>
                <button class="delete-goal-btn" data-goal-id="${res.goal.goal_id}">Delete</button>
            </div>`
}


$("#add-goal-form").on("submit", (evt) => {
    evt.preventDefault();
    const patientId = evt.target.dataset.patientId;
    const formValues = $("#add-goal-form").serialize();
    $("#add-goal-form")[0].reset();
    $.post(`/patient/${patientId}/add-goal`, formValues, (res) => {
        $("#current-goal-div").replaceWith(getCurrentGoal(res));
        $("#past-goals-div").prepend(getPastGoal(res));
    });
});

$("body").on("submit", "form.edit-goal-form", (evt) => {
    evt.preventDefault();
    const goalId = evt.target.dataset.goalId;
    const formValues = $(`#edit-goal-form-${goalId}`).serialize();
    $.post(`/goal/${goalId}/edit`, formValues, (res) => {
        $("#current-goal-div").replaceWith(getCurrentGoal(res));
    });
});
