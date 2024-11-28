$(document).ready(function () {
    // Handle "Edit" button click
    $(".edit-comment-btn").on("click", function (e) {
        e.preventDefault();
        const commentCard = $(this).closest(".comment"); // Get the closest .comment container
        const commentText = commentCard.find(".comment-text");
        const editForm = commentCard.find(".edit-comment-form");
        const textarea = editForm.find(".edit-comment-textarea");

        // Set textarea value to current comment text
        textarea.val(commentText.text().trim());

        // Show the edit form and hide the comment text
        commentText.hide();
        editForm.show();
    });

    // Handle "Cancel" button click
    $(".cancel-edit-btn").on("click", function () {
        const commentCard = $(this).closest(".comment");
        const commentText = commentCard.find(".comment-text");
        const editForm = commentCard.find(".edit-comment-form");

        // Hide the edit form and show the comment text
        editForm.hide();
        commentText.show();
    });

    // Handle "Submit" button click
    $(".submit-edit-btn").on("click", function () {
        const commentCard = $(this).closest(".comment");
        const textarea = commentCard.find(".edit-comment-textarea");
        const commentText = commentCard.find(".comment-text");
        const commentId = commentCard.data("comment-id"); // Correctly retrieve data-comment-id
        const editForm = commentCard.find(".edit-comment-form");

        console.log(commentId);
        

        if (!commentId) {
            alert("Failed to retrieve comment ID.");
            return;
        }

        // Send updated text to the backend via AJAX
        $.ajax({
            url: `/comments/edit/${commentId}/`,
            method: "POST",
            data: {
                comment_body: textarea.val().trim(),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                if (response.success) {
                    // Update the comment text
                    commentText.text(response.updated_body);
                    // Hide the edit form and show the updated comment text
                    editForm.hide();
                    commentText.show();
                    showToast("Comment updated successfully!", "bg-success");

                } else {
                    showToast(response.error || "An error occurred while updating the comment.", "bg-danger");
                }
            },
            error: function () {
                // console.error("AJAX Error:", `/comments/edit/${commentId}/`, status, error);
                showToast("Failed to update the comment. Please try again.", "bg-danger");

            },
        });
    });



    // Function to show toast with dynamic message and style
    function showToast(message, styleClass) {
        const toastContainer = $("#reportToastContainer");
        const toastBody = $("#reportToastBody");
        const toast = $("#reportToastMessage");

        // Update toast body and style
        toastBody.text(message);
        toast.removeClass("bg-success bg-danger").addClass(styleClass);

        // Show the toast
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();
    }


});


