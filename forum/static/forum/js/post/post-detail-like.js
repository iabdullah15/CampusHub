$(document).ready(function() {
    // Get the 'is_liked_by_user' value from the data attribute and convert it to a boolean
    let isLikedByUser = $('.interaction-container').data('liked') === true;
    console.log(isLikedByUser);
    

    // Show/Hide buttons based on whether the post is liked by the user
    if (isLikedByUser) {
        $('#like-button').hide();  // Hide the "like" button if post is liked
        $('#unlike-button').show();  // Show the "unlike" button
    } else {
        $('#unlike-button').hide();  // Hide the "unlike" button if post is not liked
        $('#like-button').show();  // Show the "like" button
    }

    // Handle the like/unlike button click
    $('#like-button, #unlike-button').on('click', function() {
        let actionUrl = $(this).data('url');  // Get the URL from the data-url attribute

        $.ajax({
            type: 'POST',
            url: actionUrl,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Add CSRF token to request headers
            },
            success: function(response) {
                if (response.liked) {
                    // Hide the like button and show the unlike button
                    $('#like-button').hide();
                    $('#unlike-button').show();
                } else {
                    // Hide the unlike button and show the like button
                    $('#unlike-button').hide();
                    $('#like-button').show();
                }


                // Update the like count
                var ct = $('#like-count').text();
                console.log(response.total_likes)
                $('.like-count').text(response.total_likes + ' likes');
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
