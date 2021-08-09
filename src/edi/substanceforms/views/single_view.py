# -*- coding: utf-8 -*-
from edi.substanceforms import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import BoundPageTemplate
import psycopg2


class SingleView(BrowserView):

    index = ViewPageTemplateFile('standard.pt')

    def __call__(self):
        self.itemid = self.request.get('item')
        self.host = self.context.aq_parent.host
        self.dbname = self.context.aq_parent.database
        self.username = self.context.aq_parent.username
        self.password = self.context.aq_parent.password
        self.article = self.get_article()
        self.machines = []
        self.secsheet = []
        if self.context.tablename == 'substance_mixture':
            self.machines = self.get_machines()
            self.secsheet = self.get_recipes()
            template = ViewPageTemplateFile('substance_mixture_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        elif self.context.tablename == 'spray_powder':
            template = ViewPageTemplateFile('spray_powder_view.pt')
            self.template = BoundPageTemplate(template, self)
            return self.template()
        return self.index()

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

    def get_recipes(self):
        substances = []
        conn = psycopg2.connect(host=self.host, user=self.username, dbname=self.dbname, password=self.password)
        cur = conn.cursor()
        select = "SELECT substance_id, concentration from recipes WHERE mixture_id = %s" %self.itemid
        cur.execute(select)
        substance_ids = cur.fetchall() #TODO: muss evenutell noch behandelt werden
        cur.close()
        for sid, concentration in substance_ids:
            cur = conn.cursor()
            select = "SELECT title from substance WHERE substance_id = %s" %sid
            cur.execute(select)
            substance_title = cur.fetchall()
            cur.close()
            entry = {'title':substance_title, 'concentration':concentration}
            substances.append(entry)
        conn.close()
        return substances

    def get_substance_type(self, substance_type):
        substance_types = {'detergent_labels': u'Reinigungsmittel Etiketten',
                           'detergent_heatset': u'Heatsetwaschmittel',
                           'detergent_manual' : u'Reinigungsmittel manueller Gebrauch',
                           'product_datasheet': u'Wasch- und Reinigungsmittel für den Offsetdruck'}
        return substance_types.get(substance_type)
