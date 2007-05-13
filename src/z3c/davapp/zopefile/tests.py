import os
import unittest
from zope.testing import doctest

import z3c.etree.testing
import z3c.dav.testing

here = os.path.dirname(os.path.realpath(__file__))
ZopeFileDAVLayer = z3c.dav.testing.WebDAVLayerClass(
    os.path.join(here, "ftesting.zcml"), __name__, "ZopeFileDAVLayer")


def test_suite():
    properties = doctest.DocFileSuite(
        "properties.txt",
        setUp = z3c.dav.testing.functionalSetUp,
        tearDown = z3c.dav.testing.functionalTearDown,
        checker = z3c.etree.testing.xmlOutputChecker,
        optionflags = doctest.REPORT_NDIFF | doctest.NORMALIZE_WHITESPACE)
    properties.layer = ZopeFileDAVLayer
                                      
    return unittest.TestSuite((
        doctest.DocTestSuite("z3c.davapp.zopefile"),
        properties,
        ))
