# -*- coding: utf-8 -*-
from edi.substanceforms import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
from edi.substanceforms.config import editrole
from edi.substanceforms.helpers import get_vocabulary
from plone import api as ploneapi
from edi.substanceforms.lib import DBConnect
import psycopg2


class SingleView(BrowserView):

    index = ViewPageTemplateFile('standard.pt')

    def __call__(self):
        dbdata = self.context.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        self.itemid = self.request.get('item')
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        self.article = self.get_article()
        self.machines = []
        self.secsheet = []
        if self.context.tablename == 'substance_mixture':
            #self.machines = self.get_machines()
            self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('substance_mixture_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        if self.context.tablename == 'substance':
            #self.machines = self.get_machines()
            self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('substance_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'spray_powder':
            template = ViewPageTemplateFile('spray_powder_view.pt')
            self.image_url = self.get_image_url()
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'manufacturer':
            template = ViewPageTemplateFile('manufacturer_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        return self.index()

    def userCanEdit(self):
        if not ploneapi.user.is_anonymous():
            current = ploneapi.user.get_current()
            roles = ploneapi.user.get_roles(user=current)
            if editrole in roles or 'Manager' in roles or 'Site Administrator' in roles:
                return self.context.absolute_url() + '/update-%s-form' % self.context.tablename
        return False

    def get_article(self):
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        tablename = self.context.tablename
        select = "SELECT * from %s WHERE %s_id = %s" %(tablename, tablename, self.itemid)
        cur.execute(select)
        article = cur.fetchall()[0]
        print(article)
        cur.close
        conn.close()
        return article

    def get_image_url(self):
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        tablename = self.context.tablename
        select = "SELECT image_url from %s WHERE %s_id = %s" % (tablename, tablename, self.itemid)
        cur.execute(select)
        uid = cur.fetchall()[0][0]
        cur.close
        conn.close()

        if uid:
            imageobj = ploneapi.content.get(UID=uid)
            image_url = '%s/@@images/image/preview' % imageobj.absolute_url()
            return image_url
        else:
            return False

    """
    def get_machines(self):
        machine_titles = []
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        select = "SELECT machine_id from mixture_pairs WHERE mixture_id = %s" %self.itemid
        cur.execute(select)
        machine_ids = cur.fetchall() #TODO: muss evenutell noch behandelt werden
        cur.close()
        for i in machine_ids:
            cur = conn.cursor()
            select = "SELECT title from printing_machine WHERE printing_machine_id = %s" %i
            cur.execute(select)
            machine_title = cur.fetchall()
            cur.close()
            machine_titles.append(machine_title)
        conn.close()
        return machine_titles
    """

    def get_synonyms(self):
        synonyms = []
        select = "SELECT synonym_name from synonyms WHERE substance_id = %s" %self.itemid
        synonyms = self.db.execute(select)
        import pdb; pdb.set_trace()
        # Continue here
        for sid, concentration in substance_ids:
            select = "SELECT title from substance WHERE substance_id = %s" %sid
            substance_title = self.db.execute(select)
            entry = {'title':substance_title, 'concentration':concentration}
            substances.append(entry)
        #self.db.close()
        return substances

    def get_recipes(self):
        substances = []
        select = "SELECT substance_id, concentration from recipes WHERE mixture_id = %s" %self.itemid
        substance_ids = self.db.execute(select)
        # Continue here
        for sid, concentration in substance_ids:
            select = "SELECT title from substance WHERE substance_id = %s" %sid
            substance_title = self.db.execute(select)
            entry = {'title':substance_title, 'concentration':concentration}
            substances.append(entry)
        #self.db.close()
        return substances

    def translate_recipes(self, recipe):
        resultstring = ""
        index = 0
        for i in recipe:
            resultstring = resultstring + "%s (%s %s), " % (recipe[index]['title'][0][0], recipe[index]['concentration'], "%")
            index = index + 1
        resultstring = resultstring[:-2]
        return resultstring

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value

    def get_none_translation(self, value):
        if value == None or value == 'None':
            return ''
        else:
            return value

    def usecase_translation(self, value):
        vocabulary = get_vocabulary('usecases')
        newlist = list()
        try:
            for v in value:
                for i in vocabulary:
                    if i[0] == v:
                        newlist.append(i[1])
            result = ', '.join(newlist)
        except:
            result = ''
        return result

    def application_areas_translation(self, value):
        vocabulary = get_vocabulary('application_areas')
        newlist = list()
        try:
            for v in value:
                for i in vocabulary:
                    if i[0] == v:
                        newlist.append(i[1])
            result = ', '.join(newlist)
        except:
            result = ''
        return result

    def unbundle_list(self, value):
        if value:
            result = value.split('@')
        else:
            result = list()
        return result
