# -*- coding: utf-8 -*-

import transaction
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import Form, StringField, FloatField, SelectField, DateField, BooleanField, IntegerField, TextAreaField, FileField, HiddenField
from plone.namedfile import NamedBlobImage
from wtforms import FileField, RadioField, SelectMultipleField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value, list_handler
from edi.substanceforms.vocabularies import substance_types, hskategorie, produktkategorien, produktklassen, branchen
from edi.substanceforms.vocabularies import classifications, usecases, application_areas
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import requests
import psycopg2

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class CreateForm(Form):

    substance = SelectField(u"Reinstoff", [validators.required()], render_kw={'class': 'form-control'})
    concentration_min = FloatField(u"Konzentration minimum", render_kw={'class': 'form-control'})
    concentration_max = FloatField(u"Konzentration maximum", render_kw={'class': 'form-control'})
    itemid = HiddenField(u'ReinstoffID')

class CreateIngredientForm(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        self.form.itemid.default = self.request.get('itemid')
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
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
            insert = "SELECT substance_id, title, casnr, egnr FROM substance ORDER BY title;"
            substances = self.db.execute(insert)
        except:
            substances = []
        #import pdb;pdb.set_trace()
        durchlaufvariable = 0
        optionlist = list()
        for i in substances:
            optionlist.append(tuple((i[0], str(i[1])+"|"+str(i[2])+"|"+str(i[3]))))
        self.form.substance.choices = optionlist
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        self.form.itemid.default = self.request.get('itemid')
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():
            insert = """INSERT INTO recipes (mixture_id, substance_id, concentration_min, concentration_max)
                                                        VALUES (%s, %s, %s, %s);""" \
                                                        % (self.form.itemid.data,
                                                        self.form.substance.data,
                                                        self.form.concentration_min.data,
                                                        self.form.concentration_max.data,
                                                        )
            try:
                self.db.execute(insert)
                self.db.close()
                message = u'Der Bestandteil wurde erfolgreich hinzugefügt.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)
            except:
                message = u'Fehler beim Hinzufügen des Bestandteils'
                ploneapi.portal.show_message(message=message, type='error', request=self.request)

            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

