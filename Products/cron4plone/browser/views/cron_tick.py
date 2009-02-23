from Acquisition import aq_inner
from zope.interface import implements
from Products.cron4plone.interfaces import ICronTickView
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.memoize import view
import time
import random

from threading import Lock
_mutex=Lock()

class CronTick(BrowserView):
    implements(ICronTickView)

    # decorator to only allow one thread to run the decorated method
    def locked(fn):
        def wrapper(*args):
            lock = _mutex.acquire(False) # non-blocking lock
            if not lock:
                return # already running..
            try:
                return fn(*args)
            finally:
                _mutex.release()
        return wrapper

    @locked
    def tick(self):
        print "CronTick %s" % time.ctime()
        context = aq_inner(self.context)
        crontool = getToolByName(context, 'CronTool')
        result = crontool.run_tasks(context)
        return result


