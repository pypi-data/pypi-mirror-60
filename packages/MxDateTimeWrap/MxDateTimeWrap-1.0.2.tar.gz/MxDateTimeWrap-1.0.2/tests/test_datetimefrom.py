import unittest
import datetime

from mx.DateTime import DateTimeFrom, DateTime


class DateTimeTests(unittest.TestCase):
    comp_d = DateTime(2014, 11, 10)
    comp_dt = DateTime(2014, 11, 10, 18, 30)

    def testIS(self):
        tc = DateTimeFrom('10.11.2014')
        self.failUnlessEqual(tc, self.comp_d)
        tc = DateTimeFrom('10.11.2014 18:30')
        self.failUnlessEqual(tc, self.comp_dt)
        tc = DateTimeFrom('10.11.2014 18:30:00')
        self.failUnlessEqual(tc, self.comp_dt)

    def testISO(self):
        tc = DateTimeFrom('2014-11-10')
        self.failUnlessEqual(tc, self.comp_d)
        tc = DateTimeFrom('2014-11-10 18:30')
        self.failUnlessEqual(tc, self.comp_dt)
        tc = DateTimeFrom('2014-11-10 18:30:00')
        self.failUnlessEqual(tc, self.comp_dt)

    def testUS(self):
        tc = DateTimeFrom('11/10/2014')
        self.failUnlessEqual(tc, self.comp_d)
        tc = DateTimeFrom('11/10/2014 06:30 PM')
        self.failUnlessEqual(tc, self.comp_dt)
        tc = DateTimeFrom('11/10/2014 06:30:00 PM')
        self.failUnlessEqual(tc, self.comp_dt)

    def testTime(self):
        tc = DateTimeFrom(DateTime(2014, 1, 2, 18, 30, 20).time)
        self.failUnlessEqual(tc.hour, 18)
        self.failUnlessEqual(tc.minute, 30)
        self.failUnlessEqual(tc.second, 20)
        tc = DateTimeFrom(23*60*60+59*60)
        self.failUnlessEqual(tc.year, 1970)
        self.failUnlessEqual(tc.hour, 23)
        self.failUnlessEqual(tc.minute, 59)
        self.failUnlessEqual(tc.second, 0)

    def testDate(self):
        tc = DateTimeFrom(DateTime(2014, 1, 2, 18, 30, 20).date)
        self.failUnlessEqual(tc.year, 2014)
        self.failUnlessEqual(tc.month, 1)
        self.failUnlessEqual(tc.day, 2)

    def testCreateFromDateTime(self):
        d = datetime.datetime(2015, 1, 1)
        dmx = DateTimeFrom(d)
        self.assertEquals(d, dmx)
        dmx = DateTimeFrom(dmx)
        self.assertEquals(d, dmx)
        dmx2 = DateTimeFrom(d.date())
        self.assertEquals(dmx, dmx2)

    def testCreateFromArgs(self):
        d1 = DateTime(2015, 1, 1)
        d2 = DateTimeFrom(2015, 1, 1)
        self.assertEquals(d1, d2)
        d2 = DateTimeFrom(year=2015, day=1, month=1)
        self.assertEquals(d1, d2)

    def testCreateFromSecond(self):
        d1 = DateTime(1970, 1, 1, 0, 0, 1)
        d2 = DateTimeFrom(1)
        self.assertEquals(d1, d2)
        d1 = DateTime(1970, 1, 1, 0, 0, 59)
        d2 = DateTimeFrom(59)
        self.assertEquals(d1, d2)
        self.assertRaises(DateTimeFrom, args=[120])

    def testArgsAndKwargs(self):
        with self.assertRaises(TypeError):
            DateTimeFrom(2014, 1, 1, day=1)

    def testUnknownString(self):
        with self.assertRaises(ValueError):
            DateTimeFrom('2015-2-29')

    def testCreateWithTime(self):
        d1 = DateTimeFrom(datetime.time(7, 0))
        d2 = DateTime(1, 1, 1, 7)
        self.assertEquals(d1, d2)
