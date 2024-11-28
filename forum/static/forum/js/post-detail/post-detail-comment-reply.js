$(document).ready(function () {
    // Handle "Edit" button click for replies
    $(".edit-reply-btn").on("click", function (e) {
        e.preventDefault();
        const replyCard = $(this).closest(".comment-reply-card");
        const replyText = replyCard.find(".reply-text");
        const editForm = replyCard.find(".edit-reply-form");
        const textarea = editForm.find(".edit-reply-textarea");

        // Set textarea value to current reply text
        textarea.val(replyText.text().trim());

        // Show the edit form and hide the reply text
        replyText.hide();
        editForm.show();
    });

    // Handle "Cancel" button click for replies
    $(".cancel-reply-edit-btn").on("click", function () {
        const replyCard = $(this).closest(".comment-reply-card");
        const replyText = replyCard.find(".reply-text");
        const editForm = replyCard.find(".edit-reply-form");

        // Hide the edit form and show the reply text
        editForm.hide();
        replyText.show();
    });

    // Handle "Submit" button click for replies
    $(".submit-reply-edit-btn").on("click", function () {
        const replyCard = $(this).closest(".comment-reply-card");
        const textarea = replyCard.find(".edit-reply-textarea");
        const replyText = replyCard.find(".reply-text");
        const replyId = replyCard.data("reply-id"); // Ensure data-reply-id is present
        const editForm = replyCard.find(".edit-reply-form");

        console.log("Submitting Reply ID:", replyId);

        if (!replyId) {
            alert("Failed to retrieve reply ID.");
            return;
        }

        // Send updated reply text to the backend via AJAX
        $.ajax({
            url: `/replies/edit/${replyId}/`,
            method: "POST",
            data: {
                reply_body: textarea.val().trim(),
                csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            },
            success: function (response) {
                if (response.success) {
                    // Update the reply text
                    replyText.text(response.updated_body);
                    // Hide the edit form and show the updated reply text
                    editForm.hide();
                    replyText.show();
                    showToast("Reply updated successfully!", "bg-success");
                } else {
                    showToast(response.error || "An error occurred while updating the reply.", "bg-danger");
                }
            },
            error: function () {
                console.error("AJAX Error: Failed to update the reply.");
                showToast("Failed to update the reply. Please try again.", "bg-danger");
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
