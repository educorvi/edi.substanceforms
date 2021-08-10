# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
import random
from datetime import datetime
import psycopg2


from edi.substanceforms import _


class IDatenbank(model.Schema):
    """ Marker interface and Dexterity Python Schema for Datenbank
    """

    host = schema.TextLine(
            title = u"IP-Adresse oder DNS-Name der Datenbank"
            )

    database = schema.TextLine(
            title = u"Name der Datenbank auf die zugegriffen werden soll"
            )

    port = schema.TextLine(
            title = u"Portnummer für die Verbindung zur Datenbank",
            description = u"Keine Angabe entspricht Standardportnummer",
            required = False
            )

    username = schema.TextLine(
            title = u"Benutzername für die Verbindung zur Datenbank"
            )

    password = schema.Password(
            title = u"Passwort für die Verbindung zur Datenbank"
            )

    text = RichText(
            title = "Text vor der Auflistung der Datenbanktabellen",
            required = False
            )

    endtext = RichText(
            title = u"Text nach der Auflistung der Datenbanktabellen",
            required = False
            )


@implementer(IDatenbank)
class Datenbank(Container):
    """
    """

    def check_webcode(self, generated_webcode):
        host = self.host
        dbname = self.database
        username = self.username
        password = self.password

        conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
        cur = conn.cursor()
        select = """SELECT tablename from pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' 
                    AND schemaname != 'information_schema';"""
        cur.execute(select)
        tables = cur.fetchall()
        cur.close()

        for i in tables:
            table = i[0]
            cur = conn.cursor()
            select = "SELECT webcode from %s WHERE webcode = '%s'" % (table, generated_webcode)
            try:
                cur.execute(select)
                erg = cur.fetchall()
            except:
                erg = False
            cur.close()
            if erg:
                return False
        conn.close()    
        return True
                
    def get_webcode(self, webcode=False):
        while not webcode:
            random_number = random.randint(100000, 999999)
            shortyear = datetime.now().strftime('%Y')[2:]
            generated_webcode = "PD%s%s" %(shortyear,random_number)
            webcode = self.check_webcode(generated_webcode)
            if webcode:
                return generated_webcode
