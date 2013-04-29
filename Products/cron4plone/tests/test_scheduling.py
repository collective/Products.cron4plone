from DateTime import DateTime
from Products.cron4plone.tools.crontab_utils import getNextScheduledExecutionTime, getNoSecDate, splitJob, makeRange
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
    
class TestMakeRange(unittest.TestCase):
    
    def test_minutes_range(self):
        self.assertEqual([0,5,10,15,20,25,30,35,40,45,50,55], makeRange(60, 5, 0))
        self.assertEqual([0,13,26,39,52], makeRange(60, 13, 0))
        self.assertEqual([0,35], makeRange(60, 35, 0))
        self.assertEqual([0,59], makeRange(60, 59, 0))
        self.assertEqual([0,15,30,45], makeRange(60, 15, 0))
    
    def test_hours_range(self):
        self.assertEqual([0,3,6,9,12,15,18,21], makeRange(24,3,0))
        self.assertEqual([0,5,10,15,20], makeRange(24,5,0))
        self.assertEqual([0,13], makeRange(24,13,0))
    
    def test_day_of_month_range(self):
        # 31 day months
        self.assertEqual([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31], makeRange(31,2,1))
        self.assertEqual([1,6,11,16,21,26,31], makeRange(31,5,1))
        
        # 30 day months
        self.assertEqual([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29], makeRange(30,2,1))
        self.assertEqual([1,6,11,16,21,26], makeRange(30,5,1))
        
        # 29 day months
        self.assertEqual([1,3,5,7,9,11,13,15,17,19,21,23,25,27,29], makeRange(29,2,1))
        self.assertEqual([1,6,11,16,21,26], makeRange(29,5,1))
        
        # 28 day months
        self.assertEqual([1,3,5,7,9,11,13,15,17,19,21,23,25,27], makeRange(28,2,1))
        self.assertEqual([1,6,11,16,21,26], makeRange(28,5,1))
    
    def test_month_range(self):
        self.assertEqual([1,3,5,7,9,11], makeRange(12,2,1))
        self.assertEqual([1,6,11], makeRange(12,5,1))

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
    
    def test_multiple_minute_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the 12/04 at 15:15:00 and 15:45:00
        parts = splitJob("15,45 15 12 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 15:45:00
        target = DateTime(2014, 04, 12, 15, 45, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_star_minute_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the 12/04, every five minutes of the hour 16:00
        parts = splitJob("*/5 16 12 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 16:00:00
        target = DateTime(2014, 04, 12, 16, 00, 00, "GMT")
        self.assertEqual(next_run, target)

    def test_multiple_hour_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the 12/04 at 15:35:00 and 17:35:00
        parts = splitJob("35 15,17 12 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 15:45:00
        target = DateTime(2014, 04, 12, 17, 35, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_star_hour_datetime(self):
        # Time now is 12/04/2014 14:40:00
        current = DateTime(2014, 04, 12, 14, 40, 00, "GMT")
        # Run the job on the 12/04, every second hour on the hour
        parts = splitJob("0 */2 12 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 16:00:00
        target = DateTime(2014, 04, 12, 16, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_multiple_day_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the [12|13]/04 at 15:30:00
        parts = splitJob("30 15 12,13 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 13/04/2014 15:30:00
        target = DateTime(2014, 04, 13, 15, 30, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_star_day_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job every day, at 15:00
        parts = splitJob("0 15 */1 4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 13/04/2014 15:00:00
        target = DateTime(2014, 04, 13, 15, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_multiple_month_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the 12/[04|05] at 15:15:00
        parts = splitJob("15 15 12 4,5")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/05/2014 15:15:00
        target = DateTime(2014, 05, 12, 15, 15, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_star_month_datetime(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job on the 12 of every other month, at 15:00
        # Every other month is always odd [1,3,5,7,9...]
        parts = splitJob("0 15 12 */2")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/05/2014 15:00:00
        target = DateTime(2014, 05, 12, 15, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_run_every_5_mins_all_the_time(self):
        # Time now is 12/04/2014 15:41:00
        current = DateTime(2014, 04, 12, 15, 41, 00, "GMT")
        # Run the job every 5 minutes
        parts = splitJob("*/5 * * *")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 15:45:00
        target = DateTime(2014, 04, 12, 15, 45, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_run_every_minute_every_other_hour(self):
        # Time now is 12/04/2014 15:40:00
        current = DateTime(2014, 04, 12, 15, 40, 00, "GMT")
        # Run the job every minute, every other hour
        parts = splitJob("* */2 * *")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 16:00:00
        target = DateTime(2014, 04, 12, 16, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_run_every_minute_of_every_hour_every_other_day(self):
        # Time now is 11/04/2014 15:40:00
        current = DateTime(2014, 04, 10, 15, 40, 00, "GMT")
        # Run the job every minute, every hour, every other day (i.e. 1st, 3rd, 5th, etc)
        parts = splitJob("* * */2 *")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 12/04/2014 00:00:00
        target = DateTime(2014, 04, 11, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        
    def test_run_every_minute_of_every_hour_of_every_day_of_every_other_month(self):
        # Time now is 12/06/2014 15:40:00
        current = DateTime(2014, 06, 12, 15, 40, 00, "GMT")
        parts = splitJob("* * * */2")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 01/07/2014 00:00:00
        target = DateTime(2014, 07, 01, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_something_with_multiple_everything(self):
        # Time now is 12/05/2014 15:40:00
        current = DateTime(2014, 05, 12, 15, 40, 00, "GMT")
        parts = splitJob("15,45 14,16 11,14 4,6")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 11/06/2014 14:15:00
        target = DateTime(2014, 06, 11, 14, 15, 00, "GMT")
        self.assertEqual(next_run, target)
        
    
    def test_something_with_stars_everywhere(self):
        # Time now is 14/04/2014 05:14:00
        current = DateTime(2014, 04, 14, 05, 14, 00, "GMT")
        # Every 5 minutes for an hour every 3 hours, every 2 days of every 4th Month
        # Day range should calculate as: [1,3,5,7,9,11,13,15...]
        # Month range should calculate as [1,5,9]
        parts = splitJob("*/5 */3 */2 */4")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 01/05/2014 00:00:00
        target = DateTime(2014, 05, 1, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        # Time now is 14/05/2014 05:14:00
        current = DateTime(2014, 05, 14, 05, 14, 00, "GMT")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 15/05/2014 00:00:00
        target = DateTime(2014, 05, 15, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        # Time now is 15/05/2014 05:14:00
        current = DateTime(2014, 05, 15, 05, 14, 00, "GMT")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 15/05/2014 06:00:00
        target = DateTime(2014, 05, 15, 06, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        # Time now is 15/05/2014 06:14:00
        current = DateTime(2014, 05, 15, 06, 14, 00, "GMT")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 15/05/2014 06:15:00
        target = DateTime(2014, 05, 15, 06, 15, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_minute_ticks_over_to_next_hour(self):
        # Time now is 14/04/2014 05:59:00
        current = DateTime(2014, 04, 14, 05, 59, 00, "GMT")
        # Every 20 minutes all the time
        parts = splitJob("*/20 * * *")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 14/04/2014 06:00:00
        target = DateTime(2014, 04, 14, 06, 00, 00, "GMT")
        self.assertEqual(next_run, target)
    
    def test_day_and_month_ranges_are_respected(self):
        # Set up something to run at midnight on the */31 of every month 
        # ^ Would be a shortcut to getting a cron job called on
        # The first of every month, and twice for
        # any month with 31 days
        #
        parts = splitJob("0 0 */30 *")
        
        # It's currently the 14th Feb, should schedule for 1st March 
        current = DateTime(2014, 02, 14, 00, 00, 00, "GMT")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 01/03/2014 00:00:00
        target = DateTime(2014, 03, 01, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        # Now, it's the 10th of March, should schedule for 31st March 
        current = DateTime(2014, 03, 10, 00, 00, 00, "GMT")
        next_run = getNextScheduledExecutionTime(parts['schedule'], current)
        # The next scheduled execution should be at 31/03/2014 00:00:00
        target = DateTime(2014, 03, 31, 00, 00, 00, "GMT")
        self.assertEqual(next_run, target)
        
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestJobFormat))
    suite.addTest(unittest.makeSuite(TestSplitJob))
    suite.addTest(unittest.makeSuite(TestMakeRange))
    suite.addTest(unittest.makeSuite(TestScheduling))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
