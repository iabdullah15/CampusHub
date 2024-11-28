$(document).ready(function () {
    // Handle delete reply button click
    $(".delete-reply-btn").on("click", function (e) {
        e.preventDefault();

        const replyId = $(this).data("reply-id");
        const replyCard = $(this).closest(".comment-reply-card");

        if (!replyId) {
            alert("Failed to retrieve the reply ID.");
            return;
        }

        if (confirm("Are you sure you want to delete this reply?")) {
            $.ajax({
                url: `/replies/delete/${replyId}/`,
                method: "POST",
                data: {
                    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
                },
                success: function (response) {
                    if (response.success) {
                        replyCard.remove();
                        showToast("Reply deleted successfully!", "bg-success");
                    } else {
                        showToast(response.error || "An error occurred while deleting the reply.", "bg-danger");
                    }
                },
                error: function () {
                    showToast("Failed to delete the reply. Please try again.", "bg-danger");
                },
            });
        }
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
