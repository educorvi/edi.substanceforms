$(document).ready(function () {
  $("select.edi-select").each(function () {
    $('option').removeAttr('value');
    var listid = $(this).attr('id') + "datalistOptions";
    $(this).replaceWith("<datalist id=" + listid + ">" + this.innerHTML + "</datalist>")
  });
});
