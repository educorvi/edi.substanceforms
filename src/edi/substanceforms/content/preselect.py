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
from edi.substanceforms.lib import DBConnect
from edi.substanceforms.helpers import get_vocabulary



terms = [SimpleTerm(value = i, token = i, title = i) for i in vocabularies]

vocabvocab = SimpleVocabulary(terms)


# from edi.substanceforms import _


class IPreselect(model.Schema):
    """ Marker interface and Dexterity Python Schema for Preselect
    """

    vocab = schema.Choice(
        title=u'Bitte wählen Sie das Vocabulary aus, mit dem die Ergebnisliste gebildet werden soll',
        vocabulary=vocabvocab,
        required=True
    )

    preselects = schema.List(
        title=u'Liste mit Preselects, die ausgeführt werden sollen',
        value_type=schema.TextLine(),
        required=True
    )

@implementer(IPreselect)
class Preselect(Item):
    """
    """

    def get_attr_translation(self, attribute, value):
        vocabulary = get_vocabulary(attribute)
        for i in vocabulary:
            if i[0] == value:
                return i[1]
        return value

    def get_erglist(self, value):
        dbdata = self.aq_parent.aq_parent
        self.db = DBConnect(host=dbdata.host, db=dbdata.database, user=dbdata.username, password=dbdata.password)
        erg = list()
        for select in self.preselects:
            if not erg:
                select = Template(select).render(value=value)
                erg = self.db.execute(select)
            else:
                res = erg
                erg = []
                for entry in res:
                    select = Template(select).render(value=entry)
                    if not erg:
                        erg = self.db.execute(select)
                    else:
                        erg += self.db.execute(select)

        return [self.get_attr_translation(self.vocab, i) for i in erg]
