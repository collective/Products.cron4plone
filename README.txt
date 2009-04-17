Product description
===================
Cron4Plone can do scheduled tasks in Plone, in a syntax very like \*NIX
systems' cron daemon. It plugs into Zope's ClockServer machinery.


Installation
============
1. Configure the ticker in the buildout (or zope.conf)::

    [instance]
    ...
    eggs = 
        ...
        Products.ClockServer
    zope-conf-additional = 
      <clock-server>
          method /<your-plone-site>/@@cron-tick
          period 60
      </clock-server>

2. Configure the scheduled tasks

    In the Plone site setup, go to the cron4plone configuration. This form can 
    be used to enter cron-like jobs. 
    
    The cron job should have 5 elements: minute, hour, day_of_month, month and 
    command expression. For the command python and tal expression can be used.
  
    definition: m h dom m command

    Examples:
    * 11 * * portal/@@run_me
    15,30 * * * python: portal.my_tool.runThis()


3. Wait and see
    
    In the ZMI, go to the CronTool. If a cronjob has run the history is shown.

TODO
====
- Day of week is missing in cron-like syntax, add it.
- Improve doc test, currently test has basic coverage.
- Perhaps make a configuration form that allows users without cron syntax
  knowledge to enter jobs.

License and credits
===================
Authors: "Huub Bouma", mailto:bouma@gw20e.com
         "Kim Chee Leong", mailto:leong@gw20e.com

License: This product is licensed under the GNU Public License version 2.
See the file LICENSE included in this product.

Parts of the code were taken from 
"PloneMaintenance", http://plone.org/products/plonemaintenance by 
"Ingeniweb", http://www.ingeniweb.com/.
