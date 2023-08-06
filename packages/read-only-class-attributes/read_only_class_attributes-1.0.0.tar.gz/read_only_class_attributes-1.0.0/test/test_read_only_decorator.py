from read_only_class_attributes import read_only

import unittest

# example for all read only attributes
@read_only('*')
class _CONSTANTS:
    pi = 3.14159
    G = 6.67430e-11


CONSTANTS = _CONSTANTS()


# example for some read only attributes
@read_only('pi', 'G')
class _PLANETCONSTANTS:
    pi = 3.14159
    G = 6.67430e-11
    g = 9.18  # can change
    planet = 'Earth'  # can change


PLANETCONSTANTS = _PLANETCONSTANTS()


def modifyAttr():
    CONSTANTS.pi = 2


def modifySelectedAttr():
    PLANETCONSTANTS.G = 5


class ReadonlyTestCase(unittest.TestCase):
    def testErrorOnModifying(self):
        self.assertRaises(AttributeError, modifyAttr)

    def testErrorOnModifyingSelected(self):
        self.assertRaises(AttributeError, modifySelectedAttr)

    def testNoErrorOnReading(self):
        try:
            _ = CONSTANTS.pi
        except Exception:
            self.fail(
                "Reading read only attributes should not throw exceptions")

    def testCanEditNonReadOnly(self):
        try:
            PLANETCONSTANTS.g = 1.625
            PLANETCONSTANTS.planet = 'Moon'
        except Exception:
            self.fail("Non read only attributes should be modifiable")
