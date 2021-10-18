# -*- coding: utf-8 -*-
from wtforms import Form, StringField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()])
    description = StringField("Beschreibung")
    homepage = StringField("Homepage")

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
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

    def submit(self, button):
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern' and self.validate():

            if True:
                insert = """INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', %s);""" % (self.form.title.data,
                                                            self.form.description.data,
                                                            self.context.aq_parent.get_webcode(),
                                                            check_value(self.form.homepage.data))
                self.db.execute(insert)
                self.db.close()
                message=u'Der Hersteller wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)
            #except:
            #    print(u'Fehler beim Einfügen in die Datenbank')
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

