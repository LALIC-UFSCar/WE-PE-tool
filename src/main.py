#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import gettext
import locale
import tkinter as tk
from gui.main_window import Application

try:
    gettext.translation('ape', localedir='locale', languages=[locale.getlocale()[0]]).install()
except IOError:
    gettext.translation('ape', localedir='locale', languages=['en_US']).install()

ROOT = tk.Tk()
Application(ROOT)
ROOT.mainloop()
