# -*- coding: utf-8 -*-

from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField
from wtforms import FileField, RadioField, SelectMultipleField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import substance_types, hskategorie, produktkategorien, produktklassen, branchen
from edi.substanceforms.vocabularies import classifications, usecases, application_areas
from plone import api as ploneapi
import requests
import psycopg2

class CreateForm(Form):

    title = StringField(u"Titel", [validators.required()])
    description = StringField(u"Beschreibung", [validators.required()])
    branch = SelectField("Branche", choices=branchen)
    manufacturer_id = SelectField(u"Hersteller des Wasch- und Reinigungsmittels", [validators.required()])
    substance_type = RadioField(u"Art des Wasch- und Reinigungsmittels", [validators.required()], choices=substance_types)
    offset_print_manner = StringField(u"Offsetdruckverfahren")
    detergent_special = BooleanField(u"Es handelt sich um einen Sonderreiniger")
    evaporation_lane_150 = FloatField(u"Verdampfungsfaktor bei 150 Grad Celsius")
    evaporation_lane_160 = FloatField(u"Verdampfungsfaktor bei 160 Grad Celsius")
    evaporation_lane_170 = FloatField(u"Verdampfungsfaktor bei 170 Grad Celsius")
    evaporation_lane_180 = FloatField(u"Verdampfungsfaktor bei 180 Grad Celsius")
    ueg = StringField(u"UEG")
    response = StringField(u"Response-Faktor")
    skin_category = SelectField(u"Hautschutz-Kategorie", choices=hskategorie)
    date_checked = DateField(u"Datum der letzten Prüfung")
    checked_emissions = BooleanField(u"Emissionsarmes Produkt")
    #product_category = SelectField(u"Produktkategorie", choices=produktkategorien)
    #product_class = SelectField(u"Produktklasse", choices=produktklassen)
    flashpoint = IntegerField(u"Flammpunkt")
    values_range = BooleanField(u"Wertebereich")
    #material_compatibility = RadioField(u"Materialverträglichkeit", choices = [('fogra', 'FOGRA'), ('not', 'nicht getestet')])
    #classifications = RadioField(u"Klassifikation", choices=classifications)
    #safety_instructions = TextAreaField(u"Sicherheitshinweise")
    usecases = SelectMultipleField(u"Anwendungsfälle", choices=usecases)
    application_areas = SelectMultipleField(u"Anwendungsbereiche", choices=application_areas)
    image_url = FileField("Bilddatei hochladen")
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
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():
            import pdb; pdb.set_trace()
            if True:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO substance_mixture VALUES (DEFAULT, '%s', '%s', %s, '%s', '%s', '%s', '%s', %s, %s, %s,
                         %s, %s, %s, %s, %s, '%s', %s, '%s',
                          %s, %s, '%s');""" % (self.form.title.data,
                                                            self.form.description.data,
                                                            check_value(self.form.branch.data),
                                                            self.context.aq_parent.get_webcode(),
                                                            self.form.substance_type.data,
                                                            self.form.offset_print_manner.data,
                                                            self.form.detergent_special.data,
                                                            self.form.evaporation_lane_150.data,
                                                            self.form.evaporation_lane_160.data,
                                                            self.form.evaporation_lane_170.data,
                                                            self.form.evaporation_lane_180.data,
                                                            check_value(self.form.ueg.data),
                                                            check_value(self.form.response.data),
                                                            check_value(self.form.skin_category.data),
                                                            check_value(self.form.date_checked.data),
                                                            self.form.checked_emissions.data,
                                                            check_value(self.form.flashpoint.data),
                                                            self.form.values_range.data,
                                                            check_value(self.form.comments.data),
                                                            #self.form.usecases.data,
                                                            #self.form.application_areas.data,
                                                            check_value(self.form.image_url.data),
                                                            self.form.manufacturer_id.data)
                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()
                message=u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)
            #except:
            #    print(u'Fehler beim Einfügen in die Datenbank')

            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

