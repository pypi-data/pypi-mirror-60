# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import sandia.conferencepolicy


class SandiaConferencepolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=sandia.conferencepolicy)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'sandia.conferencepolicy:default')


SANDIA_CONFERENCEPOLICY_FIXTURE = SandiaConferencepolicyLayer()


SANDIA_CONFERENCEPOLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SANDIA_CONFERENCEPOLICY_FIXTURE,),
    name='SandiaConferencepolicyLayer:IntegrationTesting',
)


SANDIA_CONFERENCEPOLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SANDIA_CONFERENCEPOLICY_FIXTURE,),
    name='SandiaConferencepolicyLayer:FunctionalTesting',
)


SANDIA_CONFERENCEPOLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        SANDIA_CONFERENCEPOLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='SandiaConferencepolicyLayer:AcceptanceTesting',
)
