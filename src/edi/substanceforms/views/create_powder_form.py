# -*- coding: utf-8 -*-
import transaction
from wtforms import Form, StringField, SelectField, IntegerField, FileField, FloatField, BooleanField, HiddenField, RadioField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import hskategorie, branchen, product_class
from plone.namedfile import NamedBlobImage
from edi.substanceforms.views.create_mixture_form import MultiCheckboxField
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import requests
import psycopg2

class CreateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    manufacturer_id = SelectField(u"Hersteller des Druckbestäubungspuders", [validators.required()], render_kw={'class': 'form-control edi-select'})
    #product_class = SelectField("Produktklasse", choices=product_class, render_kw={'class': 'form-control edi-select'})
    product_class = RadioField("Produktklasse", choices=product_class)
    starting_material = StringField("Ausgangsmaterial", render_kw={'class': 'form-control'})
    median_value = FloatField("Medianwert in µm", render_kw={'class': 'form-control'})
    volume_share = FloatField("Volumenanteil < 10 µm", render_kw={'class': 'form-control'})
    checked_emissions = BooleanField("Emissionsgeprüft", render_kw={'class': 'form-check-input'})
    date_checked = StringField("Prüfdatum", render_kw={'class': 'form-control', 'type': 'date'})
    image_url = FileField("Bild hochladen", render_kw={'class': 'form-control'})

class UpdateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    #product_class = SelectField("Produktklasse", choices=product_class, render_kw={'class': 'form-control edi-select'})
    product_class = RadioField("Produktklasse", choices=product_class)
    starting_material = StringField("Ausgangsmaterial", render_kw={'class': 'form-control'})
    median_value = FloatField("Medianwert in µm", render_kw={'class': 'form-control'})
    volume_share = FloatField("Volumenanteil < 10 µm", render_kw={'class': 'form-control'})
    checked_emissions = BooleanField("Emissionsgeprüft", render_kw={'class': 'form-check-input'})
    date_checked = StringField("Prüfdatum", render_kw={'class': 'form-control'})
    item_id = HiddenField()

class DeleteForm(Form):
    sure = BooleanField("Druckbestäubungspuder löschen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

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

    def renderForm(self):
        try:
            command = "SELECT manufacturer_id, title FROM manufacturer ORDER BY title;"
            erg = self.db.execute(command)
            manus = [(result[0], result[1] + ' ID:' + str(result[0])) for result in erg]
        except:
            manus = []

        self.form.manufacturer_id.choices = manus
        self.form.process()
        return self.formTemplate()

    def create_image(self, image, title):
        filedata = image.data.read()
        filename = image.data.filename

        blobimage = NamedBlobImage(data=filedata, filename=filename)
        obj = ploneapi.content.create(type='Image', title=title, image=blobimage, container=self.context)

        obj.indexObject()
        transaction.commit()

        return obj.UID()

    def submit(self, button):
        image_url = ''
        if self.form.image_url.data.filename:
            image_url = self.create_image(self.form.image_url, self.form.title.data)
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():
            insert = """INSERT INTO spray_powder VALUES (DEFAULT, '%s', '%s', '%s',
                        %s, %s, %s, %s, %s, %s, %s, %s);""" % (self.form.title.data,
                                                       self.form.description.data,
                                                       self.context.aq_parent.get_webcode(),
                                                       check_value(self.form.product_class.data),
                                                       check_value(self.form.starting_material.data),
                                                       check_value(self.form.median_value.data),
                                                       check_value(self.form.volume_share.data),
                                                       check_value(self.form.checked_emissions.data),
                                                       check_value(self.form.date_checked.data),
                                                       check_value(image_url),
                                                       check_value(self.form.manufacturer_id.data.split('ID:')[-1]))

            if self.form.image_url.data.filename:

                try:
                    self.db.execute(insert)
                    message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                    ploneapi.portal.show_message(message=message, type='info', request=self.request)
                except:
                    imageobj = ploneapi.content.get(UID=image_url)
                    ploneapi.content.delete(imageobj)

                    message = u'Fehler beim Hinzufügen des Gefahrstoffgemisches'
                    ploneapi.portal.show_message(message=message, type='error', request=self.request)

                self.db.close()

            else:
                self.db.execute(insert)
                self.db.close()

                message = u'Das Wasch- und Reinigungsmittel wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)

            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class UpdateFormView(CreateFormView):
    formClass = UpdateForm

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        getter = """SELECT title, description, product_class, starting_material, median_value, volume_share, checked_emissions, date_checked
                    FROM %s WHERE %s_id = %s;""" % (self.context.tablename,
                                                    self.context.tablename,
                                                    self.itemid)
        self.result = self.db.execute(getter)
        self.db.close()
        return self.index()

    def renderForm(self):
        self.form.title.default=self.result[0][0]
        self.form.description.default=self.result[0][1]
        self.form.product_class.default=self.result[0][2]
        self.form.starting_material.default=self.result[0][3]
        self.form.median_value.default=self.result[0][4]
        self.form.volume_share.default=self.result[0][5]
        self.form.checked_emissions.default=self.result[0][6]
        self.form.date_checked.default = self.result[0][7]
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern': #and self.validate():
            command = """UPDATE spray_powder SET title='%s', description='%s', product_class='%s', starting_material='%s',
                         median_value=%s, volume_share=%s, checked_emissions=%s
                         WHERE spray_powder_id = %s;""" % (self.form.title.data,
                                                        self.form.description.data,
                                                        self.form.product_class.data,
                                                        self.form.starting_material.data,
                                                        check_value(self.form.median_value.data),
                                                        check_value(self.form.volume_share.data),
                                                        check_value(self.form.checked_emissions.data),
                                                        self.form.item_id.data)
            self.db.execute(command)
            message = u'Der Druckbestäubungspuder wurde erfolgreich aktualisiert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            #message = u'Fehler beim Aktualisieren des Gefahrstoffgemisches'
            #ploneapi.portal.show_message(message=message, type='error', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class DeleteFormView(CreateFormView):
    formClass = DeleteForm

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        if self.submitted:
            button = self.hasButtonSubmitted()
            if button:
                result = self.submit(button)
                if result:
                    return result
        self.itemid = self.request.get('itemid')
        self.db.close()
        return self.index()


    def renderForm(self):
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern' and self.form.sure.data is True: #and self.validate():
            command = "DELETE FROM spray_powder WHERE spray_powder_id = %s" % (self.form.item_id.data)
            self.db.execute(command)
            message = u'Das Druckbestäubungspuder wurde erfolgreich gelöscht'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Speichern' and self.form.sure.data is False:
            message = u'Das Druckbestäubungspuder wurde nicht gelöscht, da das Bestätigungsfeld nicht ausgewählt war.'
            ploneapi.portal.show_message(message=message, type='error', request=self.request)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
