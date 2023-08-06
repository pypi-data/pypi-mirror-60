import unittest

import datetime
import copy

from mx.DateTime import DateTime, now, DateTimeType, DateTimeDelta


class DateTimeTests(unittest.TestCase):
    def testDateSet(self):
        tc = DateTime(2004, 12, 13)
        rc = datetime.datetime(2004, 12, 13)
        self.failUnless(tc.year == rc.year)
        self.failUnless(tc.month == rc.month)
        self.failUnless(tc.day == rc.day)

        tc = DateTime(2014, 8, 14)
        rc = datetime.datetime(2014, 8, 14)
        self.failUnless(tc.year == rc.year)
        self.failUnless(tc.month == rc.month)
        self.failUnless(tc.day == rc.day)

    def testDateTimeSet(self):
        tc = DateTime(2011, 2, 28, 16, 44, 39)
        rc = datetime.datetime(2011, 2, 28, 16, 44, 39)
        self.failUnless(tc.year == rc.year)
        self.failUnless(tc.month == rc.month)
        self.failUnless(tc.day == rc.day)
        self.failUnless(tc.hour == rc.hour)
        self.failUnless(tc.minute == rc.minute)
        self.failUnless(tc.second == rc.second)

    def testDTZero(self):
        tc = DateTime(0)
        self.failUnless(0 <= tc.year <= 1)
        self.failUnless(tc.month == 1)
        self.failUnless(tc.day == 1)
        self.failUnless(tc.hour == 0)
        self.failUnless(tc.minute == 0)
        self.failUnless(tc.second == 0.0)

    def testIntegerAdd(self):
        tc = DateTime(2014, 11, 24)
        oc = DateTime(2014, 11, 26)
        self.failUnlessEqual(tc + 2, oc)
        self.failUnlessEqual(tc, oc - 2)
        self.failUnless(isinstance(oc + 1, DateTimeType))
        self.failUnless(isinstance(oc - 1, DateTimeType))

    def testSubtract(self):
        tc = DateTime(2014, 11, 24)
        oc = DateTime(2014, 11, 22)
        self.failUnlessEqual(tc - datetime.timedelta(days=2), oc)
        self.failUnlessEqual(tc - oc, DateTimeDelta(2))

        def fu():
            return tc - 'minus'
        self.assertRaises(TypeError, fu)
        # self.failUnlessEqual(tc - 'minus', DateTimeDelta(2))

    def testDateSplit(self):
        tc = DateTime(2015, 2, 15)
        tc_date = tc.date
        self.failUnless(hasattr(tc_date, 'split'))
        y, m, d = tc_date.split('-')
        self.failUnlessEqual(y, '2015')
        self.failUnlessEqual(m, '02')
        self.failUnlessEqual(d, '15')

    def testCopy(self):
        tc = now()
        oc = copy.deepcopy(tc)
        self.failUnlessEqual(tc, oc)

    def testComparisonSimple(self):
        a = DateTime(2015, 1, 15)
        b = DateTime(2015, 2, 15)
        self.assertLess(a, b)
        self.assertLessEqual(a, b)
        self.assertLessEqual(a, a)
        self.assertGreater(b, a)
        self.assertGreaterEqual(b, a)
        self.assertGreaterEqual(b, b)

    def testComparisonComplex(self):
        a = DateTime(2015, 1, 15)
        self.assertGreaterEqual(a, None)
        self.assertGreaterEqual(a, 0)

        self.assertGreater(a, None)
        self.assertGreater(a, 0)

        self.assertLess(None, a)
        self.assertLess(0, a)
        self.assertLessEqual(None, a)
        self.assertLessEqual(0, a)

        self.assertFalse(a <= None)
        self.assertFalse(None >= a)

        self.assertFalse(a <= a-1)
        self.assertFalse(a-1 >= a)
        self.assertTrue(a >= 1)
        self.assertTrue(1 <= a)
        self.assertFalse(a <= 1)
        self.assertFalse(1 >= a)

        inta = int(a)
        # self.assertGreaterEqual(a, inta)
        # self.assertEqual(a, inta)
        # self.assertLessEqual(a, inta)
        # self.assertLessEqual(a, inta+1)
        self.assertGreaterEqual(int(a), inta)
        self.assertEqual(int(a), inta)
        self.assertLessEqual(int(a), inta)
        self.assertLessEqual(int(a), inta+1)

    def testTuple(self):
        dow = 3
        doy = 1
        expected = (
            2015, 1, 1,
            0, 0, 0,
            dow, doy)
        a = DateTime(2015, 1, 1)
        self.assertEqual(expected, a.tuple()[:-1])

        expected = (
            2015, 1, 1,
            16, 30, 45,
            dow, doy)
        a = DateTime(2015, 1, 1, 16, 30, 45)
        self.assertEqual(expected, a.tuple()[:-1])

        expected = (
            2015, 1, 2,
            16, 30, 45,
            dow+1, doy+1)
        a = DateTime(2015, 1, 2, 16, 30, 45)
        self.assertEqual(expected, a.tuple()[:-1])

    def testDayOfWeek(self):
        d = now()
        self.assertEquals(d.day_of_week, d.weekday())

    def testDaysInMonth(self):
        d = DateTime(2015, 6, 1)
        self.assertEquals(d.days_in_month, 30)
        d = DateTime(2015, 2, 1)
        self.assertEquals(d.days_in_month, 28)
        d = DateTime(1988, 2, 1)
        self.assertEquals(d.days_in_month, 29)

    def testIsoWeek(self):
        d = DateTime(2015, 6, 1)
        self.assertEquals(d.iso_week, (2015, 23, 1))
        d = DateTime(2015, 1, 1)
        self.assertEquals(d.iso_week, (2015, 1, 4))
        d = DateTime(2015, 12, 30)
        self.assertEquals(d.iso_week, (2015, 53, 3))

    def testAbsDays(self):
        d = DateTime(2015, 1, 1, 23, 31, 29)
        self.assertAlmostEqual(d.absdays, 735598.98019675922)
