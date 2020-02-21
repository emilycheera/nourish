
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


$(".add-comment-form").on("submit", (evt) => {
    evt.preventDefault();
    const postId = evt.target.dataset.postId;
    const formValues = $(`#add-comment-form-${postId}`).serialize();
    $(`#add-comment-form-${postId}`)[0].reset();
    $.post(`/post/${postId}/add-comment`, formValues, (res) => {
        $(`#comments-for-${postId}`).append(`<div id="comment-and-edit-form-${res.comment.comment_id}">
                                <div id="comment-${res.comment.comment_id}">
                                    <p>${res.dietitian.fname} ${res.dietitian.lname} | 
                                        ${res.comment.time_stamp}</p>
                                    <p>${res.comment.comment_body}</p>
                                    <button class="edit-comment-btn" data-comment-id="${res.comment.comment_id}">Edit</button>
                                    <button class="delete-comment-btn" data-comment-id="${res.comment.comment_id}">Delete</button>
                                </div>
                                <div id="editable-comment-${res.comment.comment_id}" hidden>
                                    <form class="edit-comment-form" id="edit-comment-form-${res.comment.comment_id}" data-comment-id="${res.comment.comment_id}" action="/comment/${res.comment.comment_id}/edit" method="POST">
                                        <textarea required name="comment">${res.comment.comment_body}</textarea>
                                        <button class="cancel-edit-btn" data-comment-id="${res.comment.comment_id}">Cancel</button>
                                        <button type="submit">Update Comment</button>
                                    </form>
                                </div>
                            </div>`)
    });
});


$("body").on("submit", "form.edit-comment-form", (evt) => {
    evt.preventDefault();
    const commentId = evt.target.dataset.commentId;
    const formValues = $(`#edit-comment-form-${commentId}`).serialize();
    $.post(`/comment/${commentId}/edit`, formValues, (res) => {
        $(`#comment-and-edit-form-${commentId}`).replaceWith(`<div id="comment-and-edit-form-${res.comment.comment_id}">
                                <div id="comment-${res.comment.comment_id}">
                                    <p>${res.dietitian.fname} ${res.dietitian.lname} | 
                                        ${res.comment.last_mod_date} (edited)</p>
                                    <p>${res.comment.comment_body}</p>
                                    <button class="edit-comment-btn" data-comment-id="${res.comment.comment_id}">Edit</button>
                                    <button class="delete-comment-btn" data-comment-id="${res.comment.comment_id}">Delete</button>
                                </div>
                                <div id="editable-comment-${res.comment.comment_id}" hidden>
                                    <form class="edit-comment-form" id="edit-comment-form-${res.comment.comment_id}" data-comment-id="${res.comment.comment_id}" action="/comment/${res.comment.comment_id}/edit" method="POST">
                                        <textarea required name="comment">${res.comment.comment_body}</textarea>
                                        <button class="cancel-edit-btn" data-comment-id="${res.comment.comment_id}">Cancel</button>
                                        <button type="submit">Update Comment</button>
                                    </form>
                                </div>
                            </div>`)
    });
});


