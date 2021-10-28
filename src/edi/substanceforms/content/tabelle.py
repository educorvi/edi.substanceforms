# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import provider
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
import psycopg2

from edi.substanceforms import _

@provider(IContextSourceBinder)
def possibleTables(context):
    host = context.host
    dbname = context.database
    username = context.username
    password = context.password

    conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
    cur = conn.cursor()
    select = "SELECT tablename from pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
    cur.execute(select)
    tables = cur.fetchall()
    cur.close()
    conn.close()

    terms = []
    for i in tables:
        table = i[0]
        terms.append(SimpleVocabulary.createTerm(table,table,table))
    return SimpleVocabulary(terms)

@provider(IContextSourceBinder)
def possibleColumns(context):
    terms = []
    return SimpleVocabulary(terms)

class ITabelle(model.Schema):
    """ Marker interface and Dexterity Python Schema for Tabelle
    """

    tablename = schema.Choice(
            title = u"Name der Datenbanktabelle",
            description = u"Der Name der Datenbanktabelle wird nur für interne Zugriffe verwendet\
                    und dem Benutzer nicht angezeigt.",
            source = possibleTables,
            )

    columns = schema.Choice(
            title = u"Datenbankspalten",
            description = u"Datenbankspalten auswählen, die berücksichtigt werden sollen",
            source = possibleColumns,
    )

    artikeltyp = schema.TextLine(
            title = u"Name des Artikeltyps der in dieser Tabelle gespeichert wird",
            default = u"Produkt",
            required = False
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
