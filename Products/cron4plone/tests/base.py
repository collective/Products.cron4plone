from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_cron4plone():
    """Set up the additional products required for cron4plone.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the wedgematch.data package.

    fiveconfigure.debug_mode = True
    import Products.cron4plone
    zcml.load_config('configure.zcml', Products.cron4plone)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('Products.cron4plone')

# The order here is important: We first call the (deferred) function which
# installs the products we need for the wedgematch package. Then, we let
# PloneTestCase set up this product on installation.

setup_cron4plone()
ptc.setupPloneSite(products=['Products.cron4plone'])


class cron4ploneTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
