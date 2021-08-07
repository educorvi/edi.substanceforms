# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


from edi.substanceforms import _


class IDatenbank(model.Schema):
    """ Marker interface and Dexterity Python Schema for Datenbank
    """

    adresse = schema.TextLine(
            title = u"IP-Adresse oder DNS-Name der Datenbank"
            )

    portnummer = schema.TextLine(
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

    schlusstext = RichText(
            title = u"Text nach der Auflistung der Datenbanktabellen",
            required = False
            )


@implementer(IDatenbank)
class Datenbank(Container):
    """
    """
