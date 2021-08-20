# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import requests
import random
import datetime
from wtforms import Form, StringField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
import requests
import psycopg2

class Migrationview(BrowserView):

    def __call__(self):
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        import pdb; pdb.set_trace()
        return self.index()
"""
    def submit(self, button):
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern' and self.validate():

            if True:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', %s);""" % (self.form.title.data,
                                                                                                   self.form.description.data,
                                                                                                   self.context.aq_parent.get_webcode(),
                                                                                                   check_value(
                                                                                                       self.form.homepage.data))
                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()
                message = u'Der Hersteller wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)
            # except:
            #    print(u'Fehler beim Einfügen in die Datenbank')
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
"""
