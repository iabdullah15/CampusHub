$(document).ready(function () {
  // Loop over each interaction container (one for each post)
  $(".interaction-container").each(function () {
    let container = $(this);
    let postId = container.data("post-id"); // Get the post ID
    let isLikedByUser = container.data("liked") === true; // Get whether the post is liked
    console.log(isLikedByUser);

    // Show/Hide buttons based on whether the post is liked by the user
    if (isLikedByUser) {
      $("#like-button-" + postId).hide(); // Hide the "like" button if post is liked
      $("#unlike-button-" + postId).show(); // Show the "unlike" button
    } else {
      $("#unlike-button-" + postId).hide(); // Hide the "unlike" button if post is not liked
      $("#like-button-" + postId).show(); // Show the "like" button
    }

    // Handle the like/unlike button click for this post
    $("#like-button-" + postId + ", #unlike-button-" + postId).on(
      "click",
      function () {
        let actionUrl = $(this).find(".interaction-button").data("url"); // Get the URL from the data-url attribute

        $.ajax({
          type: "POST",
          url: actionUrl,
          headers: {
            "X-CSRFToken": getCookie("csrftoken"), // Add CSRF token to request headers
          },
          success: function (response) {
            if (response.liked) {
              // Hide the like button and show the unlike button
              $("#like-button-" + postId).hide();
              $("#unlike-button-" + postId).show();
            } else {
              // Hide the unlike button and show the like button
              $("#unlike-button-" + postId).hide();
              $("#like-button-" + postId).show();
            }

            // Update the like count for this post
            $(".like-" + postId).text(response.total_likes + " likes");
          },
        });
      }
    );
  });
});

// Function to get the CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
