# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from sandia.conferencepolicy.testing import SANDIA_CONFERENCEPOLICY_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that sandia.conferencepolicy is properly installed."""

    layer = SANDIA_CONFERENCEPOLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if sandia.conferencepolicy is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'sandia.conferencepolicy'))

    def test_browserlayer(self):
        """Test that ISandiaConferencepolicyLayer is registered."""
        from sandia.conferencepolicy.interfaces import (
            ISandiaConferencepolicyLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ISandiaConferencepolicyLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = SANDIA_CONFERENCEPOLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['sandia.conferencepolicy'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if sandia.conferencepolicy is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'sandia.conferencepolicy'))

    def test_browserlayer_removed(self):
        """Test that ISandiaConferencepolicyLayer is removed."""
        from sandia.conferencepolicy.interfaces import \
            ISandiaConferencepolicyLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            ISandiaConferencepolicyLayer,
            utils.registered_layers())
