$(function() {

  // contact form animations
  $('#newpill_popup').click(function() {
    $('#newpill_form').fadeIn();
  });
  $(document).mouseup(function (e) {
    var container = $("#newpill_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});


