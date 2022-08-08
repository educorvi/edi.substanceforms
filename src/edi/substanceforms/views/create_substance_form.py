# -*- coding: utf-8 -*-
import transaction
from wtforms import Form, StringField, SelectField, IntegerField, FileField, BooleanField, HiddenField, FormField, FieldList, RadioField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from edi.substanceforms.vocabularies import hskategorie, branchen
from plone.namedfile import NamedBlobImage
from edi.substanceforms.views.create_mixture_form import MultiCheckboxField
from edi.substanceforms.lib import DBConnect
from plone import api as ploneapi
import requests
import psycopg2
from PIL import Image
from io import BytesIO

class IngredientForm(Form):
    substance = StringField(u"Reinstoff", [validators.required()], render_kw={'class': 'form-control'})
    concentration = IntegerField(u"Konzentration", render_kw={'class': 'form-control'})
    # itemid = HiddenField(u'ReinstoffID')

class CreateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    casnr = StringField("CAS-Nummer", render_kw={'class': 'form-control'})
    egnr = StringField("EG-Nummer", render_kw={'class': 'form-control'})
    concentration = IntegerField("Konzentration in wässriger Lösung", render_kw={'class': 'form-control'})
    skin_category = RadioField("Hautschutzkategorie", choices = hskategorie)
    branch = RadioField("Branche", choices=branchen)
    formula = StringField("Formel", render_kw={'class': 'form-control'})
    mol = StringField("Molmasse [g/mol]", render_kw={'class': 'form-control'})
    gestislink = StringField("Link in externe Datenbank", render_kw={'class': 'form-control'})
    status = "published"
    #image_url = FileField("Bild hochladen", render_kw={'class': 'form-control'})

class UpdateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    casnr = StringField("CAS-Nummer", render_kw={'class': 'form-control'})
    egnr = StringField("EG-Nummer", render_kw={'class': 'form-control'})
    concentration = IntegerField("Konzentration in wässriger Lösung", render_kw={'class': 'form-control'})
    skin_category = RadioField("Hautschutzkategorie", choices = hskategorie)
    branch = RadioField("Branche", choices=branchen)
    #image_url = FileField("Neues Bild hochladen", render_kw={'class': 'form-control'})
    #no_image = BooleanField("Vorhandenes Bild entfernen", render_kw={'class': 'form-check-input'})
    formula = StringField("Formel", render_kw={'class': 'form-control'})
    mol = StringField("Molmasse [g/mol]", render_kw={'class': 'form-control'})
    gestislink = StringField("Link in externe Datenbank", render_kw={'class': 'form-control'})
    published = True
    item_id = HiddenField()

class DeleteForm(Form):
    sure = BooleanField("Reinstoff löschen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

class SynonymForm(Form):
    synonym_name = StringField("Synonyn", [validators.required()], render_kw={'class': 'form-control'})
    item_id = HiddenField()

class DeleteSynonymsForm(Form):
    sure = BooleanField("Synonyme löschen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

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

    """
    def create_image(self, image, title):
        filedata = image.data.read()
        filename = image.data.filename

        blobimage = NamedBlobImage(data=filedata, filename=filename)
        obj = ploneapi.content.create(type='Image', title=title, image=blobimage, container=self.context)

        obj.indexObject()
        transaction.commit()

        return obj.UID()
    """

    def submit(self, button):
        """
        image_url = ''
        if self.form.image_url.data.filename:
            image_url = self.create_image(self.form.image_url, self.form.title.data)
        """
        redirect_url = self.context.absolute_url() + '/reinstoffe-1'

        workingcas = False
        if self.form.casnr.data:
            index = 1
            checksum = 0
            cas = self.form.casnr.data.strip()
            newcas = cas.replace('-', '')
            validator = newcas[-1]
            newcas = newcas[:-1]
            reversedcas = newcas[::-1]
            for i in reversedcas:
                checksum = checksum + (int(i) * index)
                index = index + 1

            if int(checksum) % 10 == int(validator):
                workingcas = True
            else:
                workingcas = False



        if button == 'Speichern' and self.form.casnr.data: #and self.validate():
            if workingcas == True:
                conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
                cur = conn.cursor()
                insert = """INSERT INTO substance (title, description, webcode, casnr, egnr, concentration, skin_category, branch, formula, mol, link, status)
                VALUES ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s);""" % (self.form.title.data,
                                                           self.form.description.data,
                                                           self.context.aq_parent.get_webcode(),
                                                           check_value(self.form.casnr.data).strip(),
                                                           check_value(self.form.egnr.data),
                                                           check_value(self.form.concentration.data),
                                                           check_value(self.form.skin_category.data),
                                                           check_value(self.form.branch.data),
                                                           check_value(self.form.formula.data),
                                                           check_value(self.form.mol.data),
                                                           check_value(self.form.gestislink.data),
                                                           check_value(self.form.status),
                                                                   )


                cur.execute(insert)
                conn.commit()
                cur.close()
                conn.close()

                message = u'Der Reinstoff wurde erfolgreich gespeichert.'
                ploneapi.portal.show_message(message=message, type='info', request=self.request)

                return self.request.response.redirect(redirect_url)

            else:
                message = u'Die CAS-Nummer enthält einen Fehler'
                ploneapi.portal.show_message(message=message, type='error', request=self.request)
                return None


        elif button == 'Speichern':
            conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
            cur = conn.cursor()
            insert = """INSERT INTO substance (title, description, webcode, casnr, egnr, concentration, skin_category, branch, formula, mol, link, status)
            VALUES ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s);""" % (self.form.title.data,
                                                                                 self.form.description.data,
                                                                                 self.context.aq_parent.get_webcode(),
                                                                                 check_value(self.form.casnr.data).strip(),
                                                                                 check_value(self.form.egnr.data),
                                                                                 check_value(
                                                                                     self.form.concentration.data),
                                                                                 check_value(
                                                                                     self.form.skin_category.data),
                                                                                 check_value(self.form.branch.data),
                                                                                 check_value(
                                                                                     self.form.formula.data),
                                                                                 check_value(self.form.mol.data),
                                                                                 check_value(
                                                                                     self.form.gestislink.data),
                                                                                 check_value(self.form.status),
                                                                                 )

            cur.execute(insert)
            conn.commit()
            cur.close()
            conn.close()

            message = u'Der Reinstoff wurde erfolgreich gespeichert.'
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
        getter = """SELECT title, description, casnr, egnr, concentration, skin_category, branch, formula, mol, link
                    FROM %s WHERE %s_id = %s;""" % (self.context.tablename,
                                                    self.context.tablename,
                                                    self.itemid)
        self.result = self.db.execute(getter)
        self.db.close()
        return self.index()

    def renderForm(self):
        self.form.title.default = self.result[0][0]
        self.form.description.default = self.result[0][1]
        self.form.casnr.default = self.result[0][2]
        self.form.egnr.default = self.result[0][3]
        self.form.concentration.default = self.result[0][4]
        self.form.skin_category.default = self.result[0][5]
        self.form.branch.default = self.result[0][6]
        self.form.formula.default = self.result[0][7]
        self.form.mol.default = self.result[0][8]
        self.form.gestislink.default = self.result[0][9]
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        redirect_url = self.context.aq_parent.absolute_url()
        if button == 'Speichern': #and self.validate():
            command = """UPDATE substance SET title='%s', description='%s', casnr=%s, egnr=%s, concentration=%s,
                         skin_category='%s', branch='%s', formula='%s', mol='%s', link='%s'
                         WHERE substance_id = %s;""" % (self.form.title.data,
                                                        self.form.description.data,
                                                        check_value(self.form.casnr.data),
                                                        check_value(self.form.egnr.data),
                                                        check_value(self.form.concentration.data),
                                                        self.form.skin_category.data,
                                                        self.form.branch.data,
                                                        self.form.formula.data,
                                                        self.form.mol.data,
                                                        self.form.gestislink.data,
                                                        self.form.item_id.data)
            self.db.execute(command)
            message = u'Der Reinstoff wurde erfolgreich aktualisiert.'
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
            command = "DELETE FROM substance WHERE substance_id = %s" % (self.form.item_id.data)
            self.db.execute(command)
            message = u'Der Reinstoff wurde erfolgreich gelöscht'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Speichern' and self.form.sure.data is False:
            message = u'Der Reinstoff wurde nicht gelöscht, da das Bestätigungsfeld nicht ausgewählt war.'
            ploneapi.portal.show_message(message=message, type='error', request=self.request)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class SynonymFormView(CreateFormView):
    formClass = SynonymForm

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
        #redirect_url = self.context.aq_parent.absolute_url()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern': #and self.validate():
            insert = "INSERT INTO synonyms VALUES (DEFAULT, %s, '%s');" % (self.form.item_id.data,
                                                               self.form.synonym_name.data)
            self.db.execute(insert)
            message = u'Das Synonym wurde erfolgreich angelegt'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)

class DeleteSynonymsFormView(CreateFormView):
    formClass = DeleteSynonymsForm

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
        #redirect_url = self.context.aq_parent.absolute_url()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern': #and self.validate():
            insert = "DELETE FROM synonyms WHERE substance_id = %s;" % self.form.item_id.data
            self.db.execute(insert)
            message = u'Die Synonyme wurden erfolgreich gelöscht'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)

            self.db.close()
            return self.request.response.redirect(redirect_url)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
