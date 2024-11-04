$(document).ready(function () {
    // Disable the submit button initially
    $('#profileSubmit').prop('disabled', true);

    // Store the initial value of the username field
    var initialUsername = $('#usernameInputField').val();
    console.log(initialUsername);
    

    // Event listener for changes in the username input field
    $('#usernameInputField').on('input', function () {
        var currentUsername = $(this).val();

        // Enable the submit button if the username is changed, otherwise keep it disabled
        if (currentUsername !== initialUsername) {
            $('#profileSubmit').prop('disabled', false);
        } else {
            $('#profileSubmit').prop('disabled', true);
        }
    });
});