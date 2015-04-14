import one_resume.one_resume as P
import pytest
import os
import logging

import smtplib
from mock import Mock
from mock import patch, call
from mock import MagicMock
from mock import PropertyMock

from hypothesis import given

class Testone_resume_options:

    def setup(self):
        self.p = P.OneResume()

    def test_single(self):
        opts = ['single', '-t blah.txt', '-y blah.yml', '-o blah.out', '-fText']
        self.p.getOptions(opts)
