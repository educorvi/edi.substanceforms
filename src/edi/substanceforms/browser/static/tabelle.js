$(document).ready(function () {
  $('#sortTable').DataTable({
    language: {
      "emptyTable": "Keine Daten in der Tabelle vorhanden",
      "info": "_START_ bis _END_ von _TOTAL_ Einträgen",
      "infoEmpty": "Keine Daten vorhanden",
      "infoFiltered": "(gefiltert von _MAX_ Einträgen)",
      "infoThousands": ".",
      "loadingRecords": "Wird geladen ..",
      "processing": "Bitte warten ..",
      "paginate": {
        "first": "Erste",
        "previous": "Zurück",
        "next": "Nächste",
        "last": "Letzte"
      },
      "decimal": ",",
      "search": "Filter:",
      "thousands": ".",
      "zeroRecords": "Keine passenden Einträge gefunden",
      "lengthMenu": "_MENU_ &nbsp; Zeilen anzeigen",
    }
  });
});
