const checkBox = document.getElementById("showPasswordCheckBox");
checkBox.addEventListener("change", function () {
  const passwordFields = document.querySelectorAll(
    ".profile-update-password"
  );
  console.log(passwordFields.length);
  if (this.checked) {
    for (let i = 0; i < passwordFields.length; i++) {
      passwordFields[i].setAttribute("type", "text");
    }
  } else {
    for (let i = 0; i < passwordFields.length; i++) {
      passwordFields[i].setAttribute("type", "password");
    }
  }
});

// document.addEventListener("DOMContentLoaded", function () {
//   const oldPassword = document.getElementById("inputOldPassword");
//   const newPassword1 = document.getElementById("inputNewPassword");
//   const newPassword2 = document.getElementById("inputConfirmNewPassword");
//   const submitBtn = document.getElementById("submitBtn");

//   // Function to check if all fields are filled
//   function checkFields() {
//       const oldPasswordFilled = oldPassword.value.trim() !== '';
//       const newPassword1Filled = newPassword1.value.trim() !== '';
//       const newPassword2Filled = newPassword2.value.trim() !== '';

//       // Enable the submit button if all fields are filled
//       if (oldPasswordFilled && newPassword1Filled && newPassword2Filled) {
//           submitBtn.disabled = false;
//       } else {
//           submitBtn.disabled = true;
//       }
//   }

//   // Add event listeners to check the fields whenever they change
//   oldPassword.addEventListener('input', checkFields);
//   newPassword1.addEventListener('input', checkFields);
//   newPassword2.addEventListener('input', checkFields);

//   // Function to toggle password visibility
//   document.getElementById("showPasswordCheckBox").addEventListener("change", function () {
//       const passwordFields = document.querySelectorAll(".profile-update-password");
//       const isChecked = this.checked;
      
//       passwordFields.forEach(field => {
//           field.type = isChecked ? "text" : "password";
//       });
//   });
// });
