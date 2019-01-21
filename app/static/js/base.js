function displayNotifications() {
  let el = document.getElementById("notifications");
  if (el.style.display === "none" || el.style.display === "") {
    el.style.display = "block";
    markNotificationsRead();
  } else {
    el.style.display = "none";
  }
}

$(document).mouseup(function(e) {
    var container = $("#notifications");
    if (!$("ion-icon").is(e.target) && !container.is(e.target) && container.find(e.target).get().length === 0) {
      $("#notifications").css("display", "none");
    }
});

function markNotificationsRead() {
  console.log("mark notifications read.")
  $.post('/mark_notifications_read', {})
    .done(function(response) {
      $("#num-notifications").text("");
    }).fail(function() {
      console.log('Error: Could not contact server.');
    });
}
