
// When a user clicks the edit button on a post,
// the post is hidden and the editable form is shown.
$(".edit-post-btn").on("click", (evt) => {
    const postId = evt.target.dataset.postId;
    $(`#post-${postId}`).hide();
    $(`#editable-post-${postId}`).show();
});

// When a user clicks the cancel button, editable form is hidden
// and the post is shown without any changes.
$(".cancel-edit-btn").on("click", (evt) => {
    evt.preventDefault();
    const postId = evt.target.dataset.postId;
    $(`#post-${postId}`).show();
    $(`#editable-post-${postId}`).hide();
});

// When a user clicks the delete button, they're asked if they
// want to delete the post. If so, post is deleted in database
// and page is relaoded to reflect change.
$(".delete-post-btn").on("click", (evt) => {
    result = window.confirm("Are you sure you want to delete this post?");

    if (result) {
        const postId = evt.target.dataset.postId;
        $.post("/delete-post", { post: postId }, () => {
            location.reload(true);
        });
    };
});
