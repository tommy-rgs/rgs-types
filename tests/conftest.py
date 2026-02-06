import pytest
import os
import sys

# Add src to python path so we can import the module under test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
