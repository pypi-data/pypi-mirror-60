"""
Contains a Console class that reads keys from the console.

The test case `test_getch_helper` can be used to display key codes, etc.
"""
import sys
from threading import Thread, Event, Lock
from typing import Union, Tuple, Optional, cast


_sentinel = object()
