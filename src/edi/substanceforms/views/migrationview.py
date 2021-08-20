# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import requests
import psycopg2
import random
import datetime

class Migrationview(BrowserView):
    def __call__(self):
        import pdb; pdb.set_trace()
        template = '''<li class="heading" i18n:translate="">
          Sample View
        </li>'''
        return template
