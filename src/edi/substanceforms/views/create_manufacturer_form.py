# -*- coding: utf-8 -*-
from wtforms import Form, StringField, FileField, HiddenField, BooleanField
from wtforms import validators
from collective.wtforms.views import WTFormView
from edi.substanceforms.helpers import check_value
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect

class CreateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    homepage = StringField("Homepage", render_kw={'class': 'form-control'})
    status = "published"

class UpdateForm(Form):

    title = StringField("Titel", [validators.required()], render_kw={'class': 'form-control'})
    description = StringField("Beschreibung", render_kw={'class': 'form-control'})
    homepage = StringField("Homepage", render_kw={'class': 'form-control'})
    item_id = HiddenField()

class DeleteForm(Form):
    sure = BooleanField("Hersteller löschen", render_kw={'class': 'form-check-input'})
    item_id = HiddenField()

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

    def submit(self, button):
        self.db.connect()
        redirect_url = self.context.absolute_url()
        if button == 'Speichern' and self.validate():
            insert = """INSERT INTO manufacturer VALUES (DEFAULT, '%s', '%s', '%s', %s, %s);""" % (self.form.title.data,
                                                                                                   self.form.description.data,
                                                                                                   self.context.aq_parent.get_webcode(),
                                                                                                   check_value(self.form.homepage.data),
                                                                                                   check_value(self.form.status))
            self.db.execute(insert)
            self.db.close()
            message=u'Der Hersteller wurde erfolgreich gespeichert.'
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
        getter = """SELECT title, description, homepage
                    FROM %s WHERE %s_id = %s;""" % (self.context.tablename,
                                                    self.context.tablename,
                                                    self.itemid)
        self.db.connect()
        self.result = self.db.execute(getter)
        self.db.close()
        return self.index()

    def renderForm(self):
        self.form.title.default=self.result[0][0]
        self.form.description.default=self.result[0][1]
        self.form.homepage.default=self.result[0][2]
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url() + '/single_view?item=' + self.form.item_id.data
        if button == 'Speichern': #and self.validate():
            command = """UPDATE manufacturer SET title='%s', description='%s', homepage='%s'
                         WHERE manufacturer_id = %s;""" % (self.form.title.data,
                                                        self.form.description.data,
                                                        self.form.homepage.data,
                                                        self.form.item_id.data)
            self.db.execute(command)
            self.db.close()
            message = u'Der Hersteller wurde erfolgreich aktualisiert.'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
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
        return self.index()

    def renderForm(self):
        self.form.item_id.default=self.itemid
        self.form.process()
        return self.formTemplate()

    def submit(self, button):
        """
        """
        self.db.connect()
        redirect_url = self.context.absolute_url()
        if button == 'Speichern' and self.form.sure.data is True: #and self.validate():
            command = "DELETE FROM manufacturer WHERE manufacturer_id = %s" % (self.form.item_id.data)
            self.db.execute(command)
            self.db.close()
            message = u'Der Hersteller wurde erfolgreich gelöscht'
            ploneapi.portal.show_message(message=message, type='info', request=self.request)
            return self.request.response.redirect(redirect_url)

        elif button == 'Speichern' and self.form.sure.data is False:
            message = u'Der Hersteller wurde nicht gelöscht, da das Bestätigungsfeld nicht ausgewählt war.'
            ploneapi.portal.show_message(message=message, type='error', request=self.request)

        elif button == 'Abbrechen':
            return self.request.response.redirect(redirect_url)
