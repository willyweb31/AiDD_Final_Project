// Conveniences for /chat and /conversations/<id>. Every rule here is also
// enforced by the server, and every page works without this file.
(function () {
  "use strict";

  var MAX_LENGTH = 500;
  var form = document.querySelector("form.ask");
  var box = document.getElementById("question");
  var send = document.getElementById("send");
  var counter = document.getElementById("question-counter");

  // Show a live "N / 500" count that turns red above 500. It counts the way the
  // server does: spaces around the question are ignored, and an emoji is one character.
  function updateCounter() {
    var length = Array.from(box.value.trim()).length;
    counter.textContent = length + " / " + MAX_LENGTH;
    counter.classList.toggle("over", length > MAX_LENGTH);
  }

  if (form && box && send) {
    var sending = false;

    form.addEventListener("submit", function (event) {
      // Ignore a second Send or Enter while the first question is on its way.
      if (sending) {
        event.preventDefault();
        return;
      }
      sending = true;
      send.disabled = true;
      send.textContent = "Thinking...";
    });

    // Send on Enter; Shift+Enter adds a new line.
    box.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        if (form.requestSubmit) {
          form.requestSubmit();
        } else {
          send.click();
        }
      }
    });

    // Coming back with the browser's Back button should not leave Send stuck.
    window.addEventListener("pageshow", function () {
      sending = false;
      send.disabled = false;
      send.textContent = "Send";
    });

    if (counter) {
      box.addEventListener("input", updateCounter);
      updateCounter();
    }
  }

  // Ask before deleting a conversation.
  document.querySelectorAll("form[data-confirm]").forEach(function (deleteForm) {
    deleteForm.addEventListener("submit", function (event) {
      if (!window.confirm(deleteForm.getAttribute("data-confirm"))) {
        event.preventDefault();
      }
    });
  });

  // Scroll to the newest answer.
  var messages = document.querySelectorAll(".thread .message");
  if (messages.length) {
    messages[messages.length - 1].scrollIntoView({ block: "start" });
  }
})();
