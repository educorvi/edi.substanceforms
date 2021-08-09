# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField, IntegerField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()])
    description = StringField("Beschreibung", [validators.required()])
    casnr = IntegerField("CAS-Nummer")
    skin_category = SelectField("Hautschutzkategorie", choices = [])
    branch = SelectField("Branche", choices = [])
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
        if button == 'Speichern': #and self.validate():

            if True:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO substance VALUES (DEFAULT, '%s', '%s', '%s', 
                            '%s', '%s', '%s', NULL);""" % (self.form.title.data, 
                                                           self.form.description.data,
                                                           self.context.aq_parent.get_webcode(),
                                                           self.form.casnr.data,
                                                           self.form.skin_category.data,
                                                           self.form.branch.data)
          
                cur.execute(insert)
                #cur.execute("UPDATE substance SET casnr = NULL WHERE casnr = '';")
                #cur.execute("UPDATE substance SET skin_category = NULL WHERE skin_category = '';")
                #cur.execute("UPDATE substance SET branch = NULL WHERE branch = '';")
                conn.commit()
                cur.close()
                conn.close()
            #except:
            #    print(u'Fehler beim Einfügen in die Datenbank')
