function displayNotifications() {
  let el = document.getElementById("notifications");
  if (el.style.display === "none" || el.style.display === "") {
    el.style.display = "block";
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
