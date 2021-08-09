# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
import psycopg2


# from edi.substanceforms import _

@provider(IContextSourceBinder)
def possibleTables(context):
    host = self.context.host
    dbname = self.context.database
    username = self.context.username
    password = self.context.password

    conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
    cur = conn.cursor()
    select = "SELECT tablename from pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
    cur.execute(select)
    tables = cur.fetchall()
    cur.close()
    conn.close()
    import pdb;pdb.set_trace()


class ITabelle(model.Schema):
    """ Marker interface and Dexterity Python Schema for Tabelle
    """

    tablename = schema.Choice(
            title = u"Name der Datenbanktabelle",
            description = u"Der Name der Datenbanktabelle wird nur für interne Zugriffe verwendet\
                    und dem Benutzer nicht angezeigt."
            source = possibleTables,
            )

    text = RichText(
            title = "Text vor dem View auf die Datenbanktabelle",
            required = False
            )

    endtext = RichText(
            title = u"Text nach dem View auf die Datenbanktabelle",
            required = False
            )

    #TODO: Vielleicht kann man hier noch den Suchstring redaktionell zusammenbauen?

@implementer(ITabelle)
class Tabelle(Container):
    """
    """
