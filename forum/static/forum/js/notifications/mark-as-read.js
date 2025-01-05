document.addEventListener("DOMContentLoaded", function () {
  const notificationItems = document.querySelectorAll(".notification-item");

  notificationItems.forEach((item) => {
    item.addEventListener("click", function (event) {
      event.preventDefault();

      const notificationId = item.getAttribute("data-notification-id");

      if (notificationId) {
        fetch(`/notifications/mark-read/${notificationId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              item.classList.add("read"); // Add a class to visually mark as read
            } else {
              console.error(data.error);
            }
          })
          .catch((error) => console.error("Error:", error));
      }
    });
  });
});
