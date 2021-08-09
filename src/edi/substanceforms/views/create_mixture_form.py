# -*- coding: utf-8 -*-

from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField
from wtforms import FileField, RadioField, SelectMultipleField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import substance_types, hskategorie, produktkategorien, produktklassen 
from edi.substanceforms.vocabularies import classifications, usecases, application_areas
import requests
import psycopg2

class CreateForm(Form):

    title = StringField(u"Titel", [validators.required()])
    description = StringField(u"Beschreibung", [validators.required()])
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()])
    substance_type = StringField(u"Art des Wasch- und Reinigungsmittels", [validators.required()])
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor bei 150 Grad Celsius")
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor bei 160 Grad Celsius")
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor bei 170 Grad Celsius")
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor bei 180 Grad Celsius")
    ueg = StringField(u"UEG")
    response = StringField(u"Response-Faktor")
    skin_category = SelectField(u"Hautschutz-Kategorie", choices=hskategorie)
    date_checked = DateField(u"Datum der letzten Prüfung")
    checked_emissions = BooleanField(u"Emissionsarmes Produkt")
    product_category = SelectField(u"Produktkategorie", choices=produktkategorien)
    product_class = SelectField(u"Produktklasse", choices=produktklassen)
    flashpoint = IntegerField(u"Flammpunkt")
    values_range = BooleanField(u"Wertebereich")
    material_compatibility = RadioField(u"Materialverträglichkeit", choices = [('fogra', 'FOGRA'), ('not', 'nicht getestet')])
    classifications = RadioField(u"Klassifikation", choices=classifications)
    safety_instructions = TextAreaField(u"Sicherheitshinweise")
    usescases = SelectMultipleField(u"Anwendungsfälle", choices=usecases)
    application_areas = SelectMultipleField(u"Anwendungsbereiche", choices=application_areas)
    image = FileField("Bilddatei hochladen")
    comments = TextAreaField("Bemerkungen")

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        return self.index()

    def renderForm(self):
        try:
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            cur.execute("SELECT manufacturer_id, title FROM manufacturer;")
            manus = cur.fetchall()
            cur.close
            conn.close()
        except:
            manus = []
        self.form.manufacturer_id.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        if button == 'Speichern' and self.validate():
            print('Speichern')
