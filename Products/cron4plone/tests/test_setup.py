import unittest
import doctest

from Testing import ZopeTestCase as ztc

from zope.component import getUtility
from zope.testing import doctestunit
import zope.component.testing

from Products.CMFCore.utils import getToolByName

from Products.cron4plone.tests.base import cron4ploneTestCase

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(ztc.FunctionalDocFileSuite(
        'tests/cron4plone.txt', package='Products.cron4plone',
        test_class=cron4ploneTestCase,
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))


    return suite

