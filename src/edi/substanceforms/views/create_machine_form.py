# -*- coding: utf-8 -*-
from wtforms import Form, StringField, SelectField, FileField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect

class CreateForm(Form):

    title = StringField("Titel", [validators.required()])
    description = StringField("Beschreibung", [validators.required()])
    manufacturer_id = SelectField("Hersteller", choices = [])
    image = FileField("Bild hochladen")

class CreateFormView(WTFormView):
    formClass = CreateForm
    buttons = ('Speichern', 'Abbrechen')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        return self.index()

    def renderForm(self):
        conn = self.db.connect()
        select = "SELECT manufacturer_id, title FROM manufacturer;"
        manus = conn.execute(select)
        conn.close()
        self.form.manufacturer_id.choices = manus
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        conn = self.db.connect()
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern':
            insert = """INSERT INTO printing_machine VALUES (DEFAULT, '%s', '%s', '%s', 
                        %s, %s);""" % (self.form.title.data, 
                                       self.form.description.data,
                                       self.context.aq_parent.get_webcode(),
                                       check_value(self.form.image.data),
                                       check_value(self.form.manufacturer_id.data))
            conn.execute(insert)  
            conn.close()
            message=u'Die Maschine wurde erfolgreich gespeichert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
   
