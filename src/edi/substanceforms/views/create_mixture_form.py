# -*- coding: utf-8 -*-

from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField
from wtforms import FileField, RadioField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class CreateForm(Form):

    title = StringField(u"Titel", [validators.required()])
    description = StringField(u"Beschreibung", [validators.required()])
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()])
    webcode = StringField(u"Webcode", [validators.required()])
    substance_type = StringField(u"Art des Wasch- und Reinigungsmittels", [validators.required()])
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor bei 150 Grad Celsius")
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor bei 160 Grad Celsius")
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor bei 170 Grad Celsius")
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor bei 180 Grad Celsius")
    ueg = StringField(u"UEG")
    response = StringField(u"Response-Faktor")
    skin_category = SelectField(u"Hautschutz-Kategorie", choices=[])
    date_checked = DateField(u"Datum der letzten Prüfung")
    checked_emissions = BooleanField(u"Emissionsarmes Produkt")
    product_category = SelectField(u"Produktkategorie", choices=[])
    product_class = SelectField(u"Produktklasse", choices=[])
    flashpoint = IntegerField(u"Flammpunkt")
    values_range = BooleanField(u"Wertebereich")
    material_compatibility = RadioField(u"Materialverträglichkeit", choices = [('fogra', 'FOGRA'), ('not', 'nicht getestet')])
    classifications = SelectField(u"Klassifikation", choices=[])
    safety_instructions = TextAreaField(u"Sicherheitshinweise")
    usescases = SelectMultipleField(u"Anwendungsfälle", choices=[])
    application_areas = TextAreaField(u"Anwendungsbereiche")
    image = FileField("Bilddatei hochladen")
    comments = TextAreaField("Bemerkungen")


class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def submit(self, button):
        if button == 'Speichern' and self.validate():
            print('Speichern')
