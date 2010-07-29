Product description
===================
Cron4Plone can do scheduled tasks in Plone, in a syntax very like \*NIX
systems' cron daemon. It plugs into Zope's ClockServer machinery.

Optionally cron4plone also uses unimr.memcachedlock to make sure that
only one task is running at a time, even when using a distributed environment
like multiple zeo clients on multiple machines.

Rationale
=========
Cron4plone uses the clockserver and allows advanced task scheduling:

* Scheduled tasks at scheduled times. E.g. I want to perform a certain task at 
  3 AM on the first day of the month.
* Single thread running the task: We don't want 2 threads running the same task
  at the same time. When using clock server only this might happen if a task 
  takes longer than the tick period.


Installation
============

1. Configure the ticker in the buildout (or zope.conf)
------------------------------------------------------

`buildout.cfg`::

    [instance]
    ...
    eggs = 
        Products.cron4plone

    zope-conf-additional = 
      <clock-server>
          method /<your-plone-site>/@@cron-tick
          period 60
          user admin
          password admin_password
      </clock-server>

The `user` and `password` variables can be omitted, but are required if you
want to call a view that requires special permissions, for example when trying 
to create content. 

1.1 Optionally use memcached server(s) to share locks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`buildout.cfg`::

    [instance]
    ...
    eggs =
        Products.cron4plone
        unimr.memcachedlock


You can specify where you are running your memcached servers in the 
MEMCACHEDLOCK_SERVERS environment variable, e.g.::
    
    zope-conf-additional =
      <environment>
          MEMCACHEDLOCK_SERVERS <ip/hostname of host1>:<port>,<ip/hostname of host2>:<port>
      </environment>


1.2 Optionally install memcached from buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A memcached server is a standalone server process which you can either
get via your favourite package manager (for debian / ubuntu:
apt-get install memcached)

But you can also build it from a buildout::

    parts +=
        memcached
        memcached-ctl
        supervisor

    [memcached]
    recipe = zc.recipe.cmmi
    url = http://memcached.googlecode.com/files/memcached-1.4.0.tar.gz
    extra_options = --with-libevent=${libevent:location}

    [memcached-ctl]
    recipe = ore.recipe.fs:mkfile
    path = ${buildout:bin-directory}/memcached
    mode = 0755
    content =
     #!/bin/sh
     PIDFILE=${memcached:location}/memcached.pid
        case "$1" in
          start)
           ${memcached:location}/bin/memcached -d -P $PIDFILE
            ;;
          stop)
            kill `cat $PIDFILE`
            ;;
          restart|force-reload)
            $0 stop
            sleep 1
            $0 start
            ;;
          *)
            echo "Usage: $SCRIPTNAME {start|stop|restart}" >&2
            exit 1
            ;;
        esac


You need to have the libevent development libraries
(apt-get install libevent-dev)
or in buildout::

    [libevent]
    recipe = zc.recipe.cmmi
    url = http://www.monkey.org/~provos/libevent-1.3b.tar.gz

Make sure that the libevent.so (shared object) file is in your
LD_LIBRARY_PATH before you start the memcached server if you build
the libevent library from the buildout.


If you use supervisor, you can add a line like this to start the
memcached server::

    10 memcached ${buildout:directory}/parts/memcached/bin/memcached

2. Configure the scheduled tasks
--------------------------------

In the Plone site setup, go to the cron4plone configuration. This form can 
be used to enter cron-like jobs. 

The cron job should have 5 elements: minute, hour, day_of_month, month and 
command expression. For `command`, a TAL expression can be used (including
'python: '). The variable `portal` is the Plone site root.

Examples::

    * 11 * * portal/@@run_me
    15,30 * * * python: portal.my_tool.runThis()

Since the 1.1.4 release the /N and N-M syntax is also supported,
thanks to Derek Broughton. This example will run the cron job ::

    */4 11 * * portal/@@run_me

3. Wait and see
---------------

In the ZMI, go to the CronTool. If a cronjob has run the history is shown.


TODO
====
- Day of week is missing in cron-like syntax, add it.
- Send mail report each time a job run, or only when one fail.
- Improve doc test, currently test has basic coverage.
- Perhaps make a configuration form that allows users without cron syntax
  knowledge to enter jobs.

License and credits
===================
Authors: "Huub Bouma", mailto:bouma@gw20e.com
         "Kim Chee Leong", mailto:leong@gw20e.com

License: This product is licensed under the GNU Public License version 2.
See the file docs/LICENSE.txt included in this product.

Parts of the code were taken from 
"PloneMaintenance", http://plone.org/products/plonemaintenance by 
"Ingeniweb", http://www.ingeniweb.com/.
"unimr.memcachedlock"
