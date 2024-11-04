document.addEventListener("DOMContentLoaded", () => {
  document
    .getElementById("comments-container")
    .addEventListener("click", (event) => {
      if (event.target.classList.contains("reply-link")) {
        const commentId = event.target.getAttribute("data-comment-id");
        const replyContainer = event.target
          .closest(".comment")
          .querySelector(".post-comment-reply-container");
        const replyTextarea = replyContainer.querySelector(
          ".reply-comment-textarea"
        );
        const replyBtnsContainer = replyContainer.querySelector(
          ".reply-btn-container"
        );

        replyContainer.style.display = "block";
        replyTextarea.style.display = "block";
        replyTextarea.focus();
        replyBtnsContainer.style.display = "flex";
      }

      if (event.target.classList.contains("cancel-btn-reply")) {
        const replyContainer = event.target.closest(
          ".post-comment-reply-container"
        );
        const replyTextarea = replyContainer.querySelector(
          ".reply-comment-textarea"
        );
        const replyBtnsContainer = replyContainer.querySelector(
          ".reply-btn-container"
        );

        replyContainer.style.display = "none";
        replyTextarea.style.display = "none";
        replyBtnsContainer.style.display = "none";
      }
    });

  // Event listener for comment textarea
  const commentTextarea = document.getElementById(
    "CommentFormControlTextarea1"
  );
  const commentSubmitButton = document.getElementById("CommentSubmitButton");
  const cancelButton = document.getElementById("CancelButton");

  commentTextarea.addEventListener("focus", () => {
    commentSubmitButton.style.display = "inline-block";
    cancelButton.style.display = "inline-block";
  });

  cancelButton.addEventListener("click", () => {
    commentSubmitButton.style.display = "none";
    cancelButton.style.display = "none";
    commentTextarea.blur();
  });
});
