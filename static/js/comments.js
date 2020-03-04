
// When a user clicks the edit button on a comment,
// the comment is hidden and the editable form is shown.
$("body").on("click", "button.edit-comment-btn", (evt) => {
    const commentId = evt.target.dataset.commentId;
    $(`#comment-${commentId}`).hide();
    $(`#editable-comment-${commentId}`).show();
});


// When a user clicks the cancel button, editable form is hidden
// and the comment is shown without any changes.
$("body").on("click", "button.cancel-edit-btn", (evt) => {
    evt.preventDefault();
    const commentId = evt.target.dataset.commentId;
    $(`#comment-${commentId}`).show();
    $(`#editable-comment-${commentId}`).hide();
});


// When a user clicks the delete button, they're asked if they
// want to delete the comment. If so, comment is deleted in database
// and page is relaoded to reflect change.
$("body").on("click", "button.delete-comment-btn", (evt) => {
    result = window.confirm("Are you sure you want to delete this comment?");

    if (result) {
        const commentId = evt.target.dataset.commentId;
        $.post("/delete-comment", { comment: commentId }, () => {
            location.reload(true);
        });
    };
});


const getDiv = (res) => {
    const timeStamp = (moment(res.comment.time_stamp).format("MMM D, YYYY [at] h:mm A"));
    return `<div id="comment-and-edit-form-${res.comment.comment_id}">
                <div id="comment-${res.comment.comment_id}">
                    <p class="comment-body">
                        <b>${res.user.fname} ${res.user.lname}:</b> 
                        ${res.comment.comment_body}
                    </p>
                    <p class="comment-time">
                        ${timeStamp}${res.comment.edited}
                        <button class="edit-comment-btn btn btn-link" data-comment-id="${res.comment.comment_id}">Edit</button>
                        <button class="delete-comment-btn btn btn-link" data-comment-id="${res.comment.comment_id}">Delete</button>
                    </p>
                </div>
                <div class="hidden edit-comment-div" id="editable-comment-${res.comment.comment_id}">
                    <form class="edit-comment-form" id="edit-comment-form-${res.comment.comment_id}" data-comment-id="${res.comment.comment_id}">
                        <textarea required class="comment-box" name="comment">${res.comment.comment_body}</textarea>
                        <button class="cancel-edit-btn btn btn-link btn-edit-cmt" data-comment-id="${res.comment.comment_id}">Cancel</button>
                        <button class="btn btn-link btn-edit-cmt " type="submit">Save Changes</button>
                    </form>
                </div>
            </div>`;
}


$(".add-comment-form").on("submit", (evt) => {
    evt.preventDefault();
    const postId = evt.target.dataset.postId;
    const formValues = $(`#add-comment-form-${postId}`).serialize();
    $(`#add-comment-form-${postId}`)[0].reset();
    $.post(`/post/${postId}/add-comment.json`, formValues, (res) => {
        $(`#comments-for-${postId}`).append(getDiv(res));
    });
});


$("body").on("submit", "form.edit-comment-form", (evt) => {
    evt.preventDefault();
    const commentId = evt.target.dataset.commentId;
    const formValues = $(`#edit-comment-form-${commentId}`).serialize();
    $.post(`/comment/${commentId}/edit.json`, formValues, (res) => {
        $(`#comment-and-edit-form-${commentId}`).replaceWith(getDiv(res));
    });
});


