# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


# from edi.substanceforms import _


class ITabelle(model.Schema):
    """ Marker interface and Dexterity Python Schema for Tabelle
    """

    tablename = schema.TextLine(
            title = u"Name der Datenbanktabelle",
            description = u"Der Name der Datenbanktabelle wird nur für interne Zugriffe verwendet\
                    und dem Benutzer nicht angezeigt."
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
