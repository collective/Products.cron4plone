Product description

    Cron4Plone can do scheduled tasks in Plone, in a syntax very like *NIX
    systems' cron daemon. It plugs into Zope's ClockServer machinery.


Warning

    This is an early alpha release, and is considered work in progress, just
    like this documentation...


Installation

    1. Configure the ticker in the buildout (or zope.conf)::

        [instance]
        ....
        eggs = 
            ...
            Products.ClockServer
        zope-conf-additional = 
          <clock-server>
              method /<your-plone-site>/@@cron-tick
              period 60
          </clock-server>

    2. Configure the scheduled tasks

        In the ZMI, go to the CronTool.  This form can be used to enter the
        cron-like data. Cronjobs can be entered in a python list of
        dictionaries like so::

            [   {   'id': 'task_number_one', 
                    'schedule':((0,15,30,45),'*','*','*'),
                    'expression': 'python: portal.do_something_every_15_minutes()',
                    },
                {   'id': 'task_number_two',
                    'schedule':('*','*','*','*'),
                    'expression': 'python: portal.do_something_every_minute()',
                    },
                ]

        Here 'schedule' is a cron tuple, and 'expression' is a TAL statement
        that should be executed. 'id' can be anything to describe your action.

        The cron tuple should have 4 elements: minute, hour, day_of_month and
        month.  Each element can also be a tuple as is shown in the example. 

        A special '*' can be used as a wildcard.


License and credits

    Author: "Huub Bouma", mailto:bouma@gw20e.com

    License: This product is licensed under the GNU Public License version 2.
    See the file LICENSE included in this product.

    Parts of the code were taken from 
    "PloneMaintenance", http://plone.org/products/plonemaintenance by 
    "Ingeniweb", http://www.ingeniweb.com/.
