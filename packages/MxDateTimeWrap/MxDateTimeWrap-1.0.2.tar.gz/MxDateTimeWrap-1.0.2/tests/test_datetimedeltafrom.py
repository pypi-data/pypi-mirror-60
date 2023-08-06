import unittest

from mx.DateTime import DateTimeDeltaFrom, DateTime


class DateTimeTests(unittest.TestCase):
    def testInteger(self):
        tc = DateTimeDeltaFrom(45)
        self.failUnlessEqual(tc.hours, 0.0125)
        self.failUnlessEqual(tc.minutes, 0.75)
        self.failUnlessEqual(tc.seconds, 45)

        tc = DateTimeDeltaFrom(30 * 60)
        self.failUnlessEqual(tc.hours, 0.5)
        self.failUnlessEqual(tc.minutes, 30)
        self.failUnlessEqual(tc.seconds, 30 * 60)

        tc = DateTimeDeltaFrom(30 * 60 * 60)
        self.failUnlessEqual(tc.hours, 30)
        self.failUnlessEqual(tc.minutes, 30 * 60)
        self.failUnlessEqual(tc.seconds, 30 * 60 * 60)

    def testString(self):
        tc = DateTimeDeltaFrom("07:54")
        self.failUnlessEqual(tc.hours, 7.9)
        self.failUnlessEqual(tc.minutes, 7 * 60 + 54)

        tc = DateTimeDeltaFrom('08:30:30')
        # self.failUnlessEqual(tc.hours, 8.5)
        self.failUnlessAlmostEqual(
            tc.hours, 8 + 30 / 60.0 + 30 / (60.0 * 60.0)
        )
        self.failUnlessEqual(tc.minutes, 8 * 60 + 30 + 30 / 60.0)
        self.failUnlessEqual(tc.seconds, 8 * 60 * 60 + 30 * 60 + 30)

    def testStringCommas(self):
        tc = DateTimeDeltaFrom('3.25:0')
        self.failUnlessEqual(tc.hours, 3.25)
        self.failUnlessEqual(tc.minutes, 3 * 60 + 15)

        tc = DateTimeDeltaFrom('1.25:45:60')
        self.failUnlessEqual(tc.hours, 2 + 1/60.0)
        self.failUnlessEqual(tc.minutes, 121)
        self.failUnlessEqual(tc.seconds, 121 * 60)

    def testStringNegative(self):
        tc = DateTimeDeltaFrom('-08:00')
        base = DateTime(2014, 11, 24, 16, 30, 0)
        summed = base + tc
        self.failUnlessEqual(summed.hour, 8)
        self.failUnlessEqual(summed.minute, 30)

        tc = DateTimeDeltaFrom('-03:30')
        self.failUnlessEqual(tc.hours, -3.5)
        self.failUnlessEqual(tc.minutes, -(60 * 3 + 30))

    def testKeywords(self):
        tc = DateTimeDeltaFrom(
            hours=3,
            minutes=30,
            seconds=30
        )
        self.failUnlessEqual(tc.hours, 3.5 + 0.5 / 60.0)
        self.failUnlessEqual(tc.minutes, 3 * 60 + 30.5)

    def testFromTime(self):
        tc = DateTimeDeltaFrom(DateTime(2014, 1, 2, 18, 30, 20).time)
        self.failUnlessEqual(tc.hour, 18)
        self.failUnlessEqual(tc.minute, 30)
        self.failUnlessEqual(tc.second, 20)

    def testEmptyString(self):
        tc = DateTimeDeltaFrom('')
        self.failUnlessEqual(tc.hour, 0)
        self.failUnlessEqual(tc.minute, 0)

    def testSubtractReturnsMX(self):
        a = DateTimeDeltaFrom("24:00")
        b = DateTimeDeltaFrom("20:00")
        res = a - b
        self.failUnless(hasattr(res, 'hours'))
        self.failUnlessEqual(res.hours, 4)
        a = DateTimeDeltaFrom("24:00")
        b = DateTimeDeltaFrom("20:30")
        res = a - b
        self.failUnless(hasattr(res, 'hours'))
        self.failUnlessEqual(res.hours, 3.5)

    def testMissingArgs(self):
        tc = DateTimeDeltaFrom(':')
        self.failUnlessEqual(tc.hour, 0)
        self.failUnlessEqual(tc.minute, 0)
        self.failUnlessEqual(tc.second, 0)
        tc = DateTimeDeltaFrom(':00')
        self.failUnlessEqual(tc.hour, 0)
        self.failUnlessEqual(tc.minute, 0)
        self.failUnlessEqual(tc.second, 0)
        tc = DateTimeDeltaFrom('00:')
        self.failUnlessEqual(tc.hour, 0)
        self.failUnlessEqual(tc.minute, 0)
        self.failUnlessEqual(tc.second, 0)
