$(document).ready(function () {
    // Get CSRF token from meta tag
    var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    console.log(csrfToken);
    

    // Set up AJAX to include CSRF token in the headers for every request
    $.ajaxSetup({
        headers: { "X-CSRFToken": csrfToken }
    });

    // Poll option change event
    $(".poll-option").on("change", function () {
        var postID = $(".poll-container").data("post-id");
        var pollID = $(".poll-container").data("poll-id");
        var choiceID = $(this).data("choice-id");
        console.log(choiceID);
        

        $.ajax({
            url: `/vote/${postID}/${pollID}`,  // Adjust this URL if needed
            type: "POST",
            data: {
                choice_id: choiceID,
            },
            success: function (response) {
                if (response.success) {
                    // Update each choice's percentage dynamically
                    response.choices.forEach(function (choice) {
                        $("#percentage-" + choice.choice_id).text(choice.percentage + "%");
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error("Error in AJAX request:", error);
            },
        });
    });
});
