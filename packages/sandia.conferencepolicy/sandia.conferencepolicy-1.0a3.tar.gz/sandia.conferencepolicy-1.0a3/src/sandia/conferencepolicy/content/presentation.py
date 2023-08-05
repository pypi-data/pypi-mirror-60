from plone import api
from plone.indexer.decorator import indexer
from plone.supermodel import model
from plone.dexterity.browser.view import DefaultView
from .vocabularies import PRESENTATION_DURATION_TYPES, LEVEL_TYPES, \
AUDIENCE_TYPES

class IPresentation(model.Schema):
    model.load('models/presentation.xml')


class PresentationView(DefaultView):

    def duration_vocab(self):
        return PRESENTATION_DURATION_TYPES

    def level_vocab(self):
        return LEVEL_TYPES

    def audience_vocab(self):
        return AUDIENCE_TYPES

    def speakers(self):
        """ parse speaker set into something template can iterate over
        """
        speaker_set = self.context.speaker
        speakers = [api.content.get(UID=x) for x in speaker_set]
        speaker_data = []
        for x in speakers:
            scale_func = api.content.get_view(name='images', context=x, request=self.request)
            # scale choices are taken from portal_registry/edit/plone.allowed_sizes
            scaled_image = getattr(x.aq_explicit, 'headshot', False) and scale_func.scale('headshot', width=150, height=150)
            if scaled_image:
                tag = scaled_image.tag(css_class='image-left')
            else:
                tag = ''
            speaker_data.append({'url': x.absolute_url(), 'name': x.title, 'headshot': tag})
        return speaker_data

    def vocab_title(self, values, vocab):
        """ return title when given the vocabulary and the value key
        """
        if not isinstance(values, (list, set)):
            result = vocab.getTerm(values).title
            if vocab == AUDIENCE_TYPES:
                return [result] # hacky fix
            return result
        return [vocab.getTerm(x).title for x in values ]
