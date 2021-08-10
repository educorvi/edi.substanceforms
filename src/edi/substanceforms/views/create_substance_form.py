# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField, IntegerField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import hskategorie, branchen
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()])
    description = StringField("Beschreibung", [validators.required()])
    casnr = IntegerField("CAS-Nummer")
    skin_category = SelectField("Hautschutzkategorie", choices = hskategorie)
    branch = SelectField("Branche", choices = branchen)
    image = FileField("Bild hochladen")

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

    def submit(self, button):
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():

            try:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO substance VALUES (DEFAULT, '%s', '%s', '%s', 
                            '%s', '%s', '%s', NULL);""" % (self.form.title.data, 
                                                           self.form.description.data,
                                                           self.context.aq_parent.get_webcode(),
                                                           check_value(self.form.casnr.data),
                                                           check_value(self.form.skin_category.data),
                                                           check_value(self.form.branch.data))
          
                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()
            except:
                print(u'Fehler beim Einfügen in die Datenbank')
            message=u'Der Gefahrstoff wurde erfolgreich gespeichert.'    
            ploneapi.portal.show_message(message=message, type='info', request=self.request)    
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

