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

    substance = SelectField(u"Reinstoff", [validators.required()], render_kw={'class': 'form-control edi-select'})
    concentration_min = FloatField(u"Konzentration minimum", render_kw={'class': 'form-control'})
    concentration_max = FloatField(u"Konzentration maximum", render_kw={'class': 'form-control'})
    itemid = HiddenField(u'MixtureID')

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

    def alreadyselected(self):
        itemid = self.request.get('itemid')
        select = "SELECT DISTINCT substance.title FROM substance, recipes, substance_mixture WHERE recipes.mixture_id = %s AND substance.substance_id = recipes.substance_id" % itemid
        result = self.db.execute(select)
        import pdb; pdb.set_trace()
        newresult = result[0]
        if result:
            try:
                return result[0][0]
            except:
                pass

    def renderForm(self):
        try:
            select = "SELECT substance_id, title, casnr, egnr FROM substance ORDER BY title;"
            substances = self.db.execute(select)
        except:
            substances = []
        optionlist = list()
        for i in substances:
            subid = i[0]
            subname = i[1]
            subcas = i[2]
            subeg = i[3]
            subentry = f"{subname} CAS:{subcas} EG:{subeg} ID:{subid}"
            optionlist.append((i[0], subentry))
        self.form.substance.choices = optionlist
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        self.form.itemid.default = self.request.get('itemid')
        redirect_url = self.context.absolute_url()+'/single_view?item='+self.form.itemid.data
        if button == 'Speichern': #and self.validate():
            insert = """INSERT INTO recipes (mixture_id, substance_id, concentration_min, concentration_max)
                                                        VALUES (%s, %s, %s, %s);""" \
                                                        % (self.form.itemid.data,
                                                        int(self.form.substance.data.split('ID:')[-1]),
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

