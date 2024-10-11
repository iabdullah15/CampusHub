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