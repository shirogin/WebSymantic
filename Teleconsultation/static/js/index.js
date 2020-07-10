$("select[multiple]:not([disabled]) option").unbind().mousedown(function(e) {
    e.preventDefault();
    $(this).prop('selected', !$(this).prop('selected'));
    return false;
});