$(document).ready(function() {
    // Handle the like/unlike button click for comments
    $('.comment-like-btn').on('click', function() {
        let actionUrl = $(this).data('url');  // Get the URL from the data-url attribute
        let isLiked = $(this).attr('id').startsWith('unlike');
        let commentId = $(this).attr('id').split('-')[2];  // Extract comment ID from the button's ID

        $.ajax({
            type: 'POST',
            url: actionUrl,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Add CSRF token to request headers
            },
            success: function(response) {
                if (response.liked) {
                    // Show the unlike button and hide the like button
                    $('#like-comment-' + commentId).hide();
                    $('#unlike-comment-' + commentId).show();
                } else {
                    // Show the like button and hide the unlike button
                    $('#unlike-comment-' + commentId).hide();
                    $('#like-comment-' + commentId).show();
                }

                // Update the like count
                $('.comment-like-count-' + commentId).text(response.total_likes + ' likes');
            }
        });
    });
});

// Function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
