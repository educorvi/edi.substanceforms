# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from edi.substanceforms.vocabularies import vocabularies
from jinja2 import Template
from edi.substanceforms.helpers import get_vocabulary

terms = [SimpleTerm(value = i, token = i, title = i) for i in vocabularies]

vocabvocab = SimpleVocabulary(terms)

class IPreselect(model.Schema):
    """ Marker interface and Dexterity Python Schema for Preselect
    """

    preselects = schema.List(
        title=u'Liste mit Preselects, die ausgeführt werden sollen, um eine Ergebnisliste zu erzeugen',
        description=u"Bitte bearchten Sie, dass die Variable der WHERE-Klausel mit {{ value }} übergeben wird.",
        value_type=schema.TextLine(),
        required=True
    )

    vocab = schema.Choice(
        title=u'Bitte wählen Sie das Vocabulary aus, mit dem die Ergebnisliste gebildet werden soll',
        vocabulary=vocabvocab,
        required=False
    )

@implementer(IPreselect)
class Preselect(Item):
    """
    """
