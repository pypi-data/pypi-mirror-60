#Note: Converted
from __future__ import absolute_import

from nose.tools import *
import os

import testit
#import tests.testit

class TestBasics(testit.LocalCase):
    def test_all(self):
        with assert_raises(SystemExit) as r:
            testit.sciunit()
        assert_equals(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('-h')
        assert_equals(r.exception.code, 2)

        with assert_raises(SystemExit) as r:
            testit.sciunit('nonexistent')
        assert_equals(r.exception.code, 2)

        assert_is_none(testit.sciunit('--help'))
        assert_is_none(testit.sciunit('--version'))
