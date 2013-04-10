from DateTime import DateTime
from Products.cron4plone.tools.crontab_utils import getNextScheduledExecutionTime, getNoSecDate, splitJob
import unittest

JOB_FORMAT = "%(_minute)d %(_hour)d %(_day)d %(_month)d command"

class TestJobFormat(unittest.TestCase):
    """ If we're not going to write the schedules ourselves we should be sure they
    work correctly when pulling from a DateTime"""
    
    def test_simple_format_gives_correct_string(self):
        date = DateTime(2000, 01, 02, 03, 04, 00, "GMT")
        job = JOB_FORMAT % vars(date)
        self.assertEqual(job, "4 3 2 1 command")

    def test_format_with_larger_numbers_still_works(self):
        date = DateTime(2010, 11, 12, 13, 14, 00, "GMT")
        job = JOB_FORMAT % vars(date)
        self.assertEqual(job, "14 13 12 11 command")

    def test_year_difference_are_irrelevant(self):
        first = DateTime(2010, 11, 12, 13, 00, 00, "GMT")
        second = DateTime(4545, 11, 12, 13, 00, 00, "GMT")
        first_job = JOB_FORMAT % vars(first)
        second_job = JOB_FORMAT % vars(second)
        self.assertEqual(first_job, second_job)
    

class TestSplitJob(unittest.TestCase):
    
    def test_split_single_digit_numbers(self):
        target = DateTime(2014, 1, 2, 3, 4, 00, "GMT")
        job = JOB_FORMAT % vars(target)
        parts = splitJob(job)
        self.assertEqual(parts['schedule'], ["4", "3", "2", "1"])
    
    def test_split_double_digit_numbers(self):
        target = DateTime(2014, 10, 11, 13, 40, 00, "GMT")
        job = JOB_FORMAT % vars(target)
        parts = splitJob(job)
        self.assertEqual(parts['schedule'], ["40", "13", "11", "10"])
    
    def test_split_commas(self):
        parts = splitJob("13,20 1 12 9")
        self.assertEqual(parts['schedule'], [["13", "20"], "1", "12", "9"])
    
    def test_split_slashes(self):
        parts = splitJob("*/20 1 12 9")
        self.assertEqual(parts['schedule'], [["*", "20"], "1", "12", "9"])
    
    def test_split_slashes_and_commas(self):
        parts = splitJob("*/20 1,3 12 9")
        self.assertEqual(parts['schedule'], [["*", "20"], ["1", "3"], "12", "9"])
    

class TestScheduling(unittest.TestCase):
    
    def test_specific_datetime_in_future(self):
        current = DateTime(2014, 01, 01, 01, 00, 00, "GMT")
        target = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        job = JOB_FORMAT % vars(target)
        parts = splitJob(job)
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        self.assertEqual(next_run, target)
    
    def test_specific_datetime_in_past(self):
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        target = DateTime(2014, 04, 12, 14, 40, 00, "GMT")
        job = JOB_FORMAT % vars(target)
        parts = splitJob(job)
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # Because the target date has already past, 
        # it should schedule it for the next year
        self.assertEqual(next_run, target + 365)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestJobFormat))
    suite.addTest(unittest.makeSuite(TestSplitJob))
    suite.addTest(unittest.makeSuite(TestScheduling))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
