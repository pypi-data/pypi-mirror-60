# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
import logging
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'sandia.conferencepolicy:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def replace_summaries(context):
    # Only run step if a flag file is present
    if getattr(context, 'getSite', None):
        if context.readDataFile('sandiaconferencepolicy_marker.txt') is None:
            return
        logger = context.getLogger('ploneconf.policy')
        site = context.getSite()
    else:
        logger = logging.getLogger('ploneconf.policy')
        site = context

    catalog = getToolByName(site, 'portal_catalog')
    brains = catalog(portal_type=['person', 'presentation', 'training_class'])
    count = 0
    for b in brains:
        if not b.Description:
            obj = b.getObject()
            if getattr(aq_base(obj), 'summary', None) is not None:
                obj.description = obj.summary
                del obj.summary
                catalog.catalog_object(obj,
                                       idxs=['Description', 'SearchableText'],
                                       update_metadata=True)
                logger.info(
                    'Replaced description for {}'.format(b.getPath())
                )
                count += 1
    logger.info('Replaced description for {} objects'.format(count))
