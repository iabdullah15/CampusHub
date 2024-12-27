// $(document).ready(function () {
//   // Handle "Delete" button click
//   $(".delete-comment-btn").on("click", function (e) {
//     e.preventDefault();
//     const commentCard = $(this).closest(".comment"); // Find the closest comment container
//     const commentId = commentCard.data("comment-id");

//     if (!commentId) {
//       alert("Failed to retrieve comment ID.");
//       return;
//     }

//     // Confirm deletion
//     const confirmed = confirm("Are you sure you want to delete this comment?");
//     if (!confirmed) {
//       return;
//     }

//     // Send delete request via AJAX
//     $.ajax({
//       url: `/comments/delete/${commentId}/`, // Django URL for deleting comments
//       method: "POST",
//       data: {
//         csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
//       },
//       success: function (response) {
//         if (response.success) {
//           // Remove the comment from the DOM
//           commentCard.remove();
//           showToast(response.message, "bg-success");
//         } else {
//           showToast(
//             response.error || "Failed to delete the comment.",
//             "bg-danger"
//           );
//         }
//       },
//       error: function () {
//         showToast(
//           "An error occurred while deleting the comment. Please try again.",
//           "bg-danger"
//         );
//       },
//     });
//   });

//   // Function to show toast with dynamic message and style
//   function showToast(message, styleClass) {
//     const toastContainer = $("#reportToastContainer");
//     const toastBody = $("#reportToastBody");
//     const toast = $("#reportToastMessage");

//     // Update toast body and style
//     toastBody.text(message);
//     toast.removeClass("bg-success bg-danger").addClass(styleClass);

//     // Show the toast
//     const bootstrapToast = new bootstrap.Toast(toast);
//     bootstrapToast.show();
//   }
// });



$(document).ready(function () {
  let commentToDelete = null;

  // Handle "Delete" button click
  $(".delete-comment-btn").on("click", function (e) {
    e.preventDefault();
    const commentCard = $(this).closest(".comment"); // Find the closest comment container
    const commentId = commentCard.data("comment-id");

    if (!commentId) {
      showToast("Failed to retrieve comment ID.", "bg-danger");
      return;
    }

    commentToDelete = { commentCard, commentId };

    // Show the modal
    const deleteModal = new bootstrap.Modal("#deleteCommentModal");
    deleteModal.show();
  });

  // Handle "Confirm Delete" button click in the modal
  $("#confirmDeleteComment").on("click", function () {
    if (!commentToDelete) return;

    const { commentCard, commentId } = commentToDelete;

    // Send delete request via AJAX
    $.ajax({
      url: `/comments/delete/${commentId}/`, // Django URL for deleting comments
      method: "POST",
      data: {
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
      },
      success: function (response) {
        if (response.success) {
          // Remove the comment from the DOM
          commentCard.remove();
          showToast(response.message, "bg-success");
        } else {
          showToast(
            response.error || "Failed to delete the comment.",
            "bg-danger"
          );
        }
      },
      error: function () {
        showToast(
          "An error occurred while deleting the comment. Please try again.",
          "bg-danger"
        );
      },
      complete: function () {
        // Hide the modal after the request completes
        const deleteModal = bootstrap.Modal.getInstance("#deleteCommentModal");
        deleteModal.hide();
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
