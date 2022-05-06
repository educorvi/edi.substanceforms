# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import provider
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from edi.substanceforms.helpers import tableheads
import psycopg2
from plone import api as ploneapi
#from z3c.form.browser.checkbox import CheckBoxFieldWidget

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
    try:
        tablename = context.tablename
        host = context.host
        dbname = context.database
        username = context.username
        password = context.password

        conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
        cur = conn.cursor()
        select = "SELECT column_name FROM information_schema.columns WHERE table_name = '%s' ORDER BY ordinal_position;" % tablename
        cur.execute(select)
        tables = cur.fetchall()
        cur.close()
        conn.close()

        terms = []
        newtables = list()
        for i in tables:
            newtables.append(i[0])
            table = i[0]
            #mytoken = int(newtables.index(table)) + 2
            mytoken = int(newtables.index(table))
            terms.append(SimpleVocabulary.createTerm(table, mytoken, tableheads(table)))
            #terms.append(SimpleVocabulary.createTerm(table, table, table))
    except:
        terms = []

    return SimpleVocabulary(terms)

@provider(IContextSourceBinder)
def possiblePreselects(context):
    #import pdb; pdb.set_trace()
    if context.portal_type == 'Tabelle':
        terms = list()
        brains = ploneapi.content.find(context=context, portal_type='Preselect')
        for i in brains:
            terms.append(SimpleVocabulary.createTerm(i.id, i.id, i.Title))
        return SimpleVocabulary(terms)
    else:
        terms = list()
        return SimpleVocabulary(terms)

@provider(IContextSourceBinder)
def mixturetypes(context):
    try:
        tablename = context.tablename
        host = context.host
        dbname = context.database
        username = context.username
        password = context.password

        conn = psycopg2.connect(host=host, user=username, dbname=dbname, password=password)
        cur = conn.cursor()
        select = "SELECT DISTINCT substance_type FROM substance_mixture;"
        cur.execute(select)
        tables = cur.fetchall()
        cur.close()
        conn.close()

        terms = []
        for i in tables:
            table = i[0]
            terms.append(SimpleVocabulary.createTerm(table, table, table))
    except:
        terms = []

    return SimpleVocabulary(terms)

class ITabelle(model.Schema):
    """ Marker interface and Dexterity Python Schema for Tabelle
    """

    tablename = schema.Choice(
            title = u"Name der Datenbanktabelle",
            description = u"Der Name der Datenbanktabelle wird nur für interne Zugriffe verwendet\
                    und dem Benutzer nicht angezeigt",
            source = possibleTables,
            )

    columns = schema.List(
            title = u"Darstellung Einzelansicht",
            description = u"Datenbankspalten auswählen, die in der Einzelansicht berücksichtigt werden sollen",
            value_type=schema.Choice(source=possibleColumns),
            )

    morecolumns = schema.List(
        title=u"Weitere Spalten für die Einzelansicht",
        description=u"Datenbankspalten auswählen, die zusätzlich in der Einzelansicht berücksichtigt werden sollen",
        value_type=schema.Choice(source=possiblePreselects),
    )

    resultcolumns = schema.List(
            title = u"Darstellung Trefferliste",
            description = u"Datenbankspalten auswählen, die in der Trefferliste berücksichtigt werden sollen",
            value_type=schema.Choice(source=possibleColumns),
            )

    moreresultcolumns = schema.List(
        title=u"Weitere Spalten für die Treffferliste",
        description=u"Datenbankspalten auswählen, die zusätzlich in der Trefferliste berücksichtigt werden sollen",
        value_type=schema.Choice(source=possiblePreselects),
    )

    mixturetype = schema.List(
        title=u"Art des Gefahrstoffgemisches",
        description=u"Art des Gefahrstoffgemisches auswählen (aus Tabelle substance_mixutre)",
        value_type=schema.Choice(source=mixturetypes),
        required = False
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
