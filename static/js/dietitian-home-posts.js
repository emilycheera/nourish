
// When a user clicks the edit button on a comment,
// the comment is hidden and the editable form is shown.
$(".edit-comment-btn").on("click", (evt) => {
    const commentId = evt.target.dataset.commentId;
    $(`#comment-${commentId}`).hide();
    $(`#editable-comment-${commentId}`).show();
});

// When a user clicks the cancel button, editable form is hidden
// and the comment is shown without any changes.
$(".cancel-edit-btn").on("click", (evt) => {
    evt.preventDefault();
    const commentId = evt.target.dataset.commentId;
    $(`#comment-${commentId}`).show();
    $(`#editable-comment-${commentId}`).hide();
});

// When a user clicks the delete button, they're asked if they
// want to delete the comment. If so, comment is deleted in database
// and page is relaoded to reflect change.
$(".delete-comment-btn").on("click", (evt) => {
    result = window.confirm("Are you sure you want to delete this comment?");

    if (result) {
        const commentId = evt.target.dataset.commentId;
        $.post("/dietitian/delete/comment", { comment: commentId }, () => {
            location.reload(true);
        });
    };
});
