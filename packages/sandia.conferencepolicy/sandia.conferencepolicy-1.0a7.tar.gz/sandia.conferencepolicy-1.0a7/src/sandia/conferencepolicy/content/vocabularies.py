from plone import api
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


PRESENTATION_DURATION_TYPES = SimpleVocabulary(
    [SimpleTerm(value=u'LongTalk', title=u'Long Talk'),
     SimpleTerm(value=u'ShortTalk', title=u'Short Talk'),
     SimpleTerm(value=u'Demo', title=u'Demo')]
    )

TRAINING_CLASS_DURATION_TYPES = SimpleVocabulary(
    [SimpleTerm(value=u'HalfDay', title=u'1/2 day'),
     SimpleTerm(value=u'OneDay', title=u'1 day'),
     SimpleTerm(value=u'TwoDay', title=u'2 day')]
    )

LEVEL_TYPES = SimpleVocabulary(
    [SimpleTerm(value=u'Beginner', title=u'Beginner'),
     SimpleTerm(value=u'Intermediate', title=u'Intermediate'),
     SimpleTerm(value=u'Expert', title=u'Expert')]
    )

AUDIENCE_TYPES = SimpleVocabulary(
    [SimpleTerm(value=u'User', title=u'User'),
     SimpleTerm(value=u'Integrator', title=u'Integrator'),
     SimpleTerm(value=u'Designer', title=u'Designer'),
     SimpleTerm(value=u'Developer', title=u'Developer')]
    )

def persons(context):
    catalog = api.portal.get_tool('portal_catalog')
    person_brains = catalog(portal_type=('person', 'keynoter'),
                        sort_on='sortable_title',
                        sort_order='ascending')
    terms = []
    for brain in person_brains:
        token = brain.getPath()
        terms.append(SimpleTerm(
            value=brain.UID,
            token=token,
            title=brain.Title
            ))
    return SimpleVocabulary(terms)
directlyProvides(persons, IContextSourceBinder)
