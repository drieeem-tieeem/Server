$(function() {

  // contact form animations
  $('#newpill_popup').click(function() {
    $('#newpill_form').fadeToggle();
  })
  $(document).mouseup(function (e) {
    var container = $("#newpill_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});

$(function() {

  // contact form animations
  $('#pill1_popup').click(function() {
    $('#pill1_form').fadeToggle();
  })
  $(document).mouseup(function (e) {
    var container = $("#pill1_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});

$(function() {

  // contact form animations
  $('#pill2_popup').click(function() {
    $('#pill2_form').fadeToggle();
  })
  $(document).mouseup(function (e) {
    var container = $("#pill2_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});

$(function() {

  // contact form animations
  $('#pill3_popup').click(function() {
    $('#pill3_form').fadeToggle();
  })
  $(document).mouseup(function (e) {
    var container = $("#pill3_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});

$(function() {

  // contact form animations
  $('#pill4_popup').click(function() {
    $('#pill4_form').fadeToggle();
  })
  $(document).mouseup(function (e) {
    var container = $("#pill4_form");

    if (!container.is(e.target) // if the target of the click isn't the container...
        && container.has(e.target).length === 0) // ... nor a descendant of the container
    {
        container.fadeOut();
    }
  });

});
