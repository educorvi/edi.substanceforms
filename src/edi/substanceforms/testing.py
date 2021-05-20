# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import edi.substanceforms


class EdiSubstanceformsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=edi.substanceforms)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'edi.substanceforms:default')


EDI_SUBSTANCEFORMS_FIXTURE = EdiSubstanceformsLayer()


EDI_SUBSTANCEFORMS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EDI_SUBSTANCEFORMS_FIXTURE,),
    name='EdiSubstanceformsLayer:IntegrationTesting',
)


EDI_SUBSTANCEFORMS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EDI_SUBSTANCEFORMS_FIXTURE,),
    name='EdiSubstanceformsLayer:FunctionalTesting',
)


EDI_SUBSTANCEFORMS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        EDI_SUBSTANCEFORMS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='EdiSubstanceformsLayer:AcceptanceTesting',
)
