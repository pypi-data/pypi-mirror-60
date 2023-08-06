"""
core.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

import atexit
from glob import iglob
import os
import shutil
from tempfile import gettempdir

# Create a cache
cache = []


# GloveBox
class GloveBox:
    # Initialize class instance
    def __init__(self, _id=None, persist=False):
        # If _id is None, generate
        while _id is None:
            # Propose _id
            _id = 'glovebox_' + os.urandom(3).hex()

            # Check if this element exists already
            path = os.path.join(self.get_root(), _id)

            # IF this path exists, set _id to None and try again
            if os.path.exists(path):
                _id = None

        # Finally, save _id and create the glovebox
        self._id = _id
        self.create()

        # If not persist, store this in cache
        if not persist:
            cache.append(self)

    # Clean the path
    def clean(self):
        # Get path
        path = self.get_path()

        # Iterate through all files and remove
        for file in iglob(os.path.join(path, '*')):
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)

    # Create the path
    def create(self):
        # Get path
        path = self.get_path()

        # Check that the path does not already exist
        # if os.path.exists(path):
        #     raise AttributeError('path already exists')

        # Create the path
        # os.makedirs(path)

        # If path does not exist, create
        if not os.path.exists(path):
            os.makedirs(path)

    # Delete the path
    def delete(self):
        shutil.rmtree(self.get_path())

    # Get the path
    def get_path(self):
        return os.path.join(self.get_root(), self._id)

    # Get the path root
    @classmethod
    def get_root(cls):
        return gettempdir()

    # A shortcut to get_path()
    @property
    def path(self):
        return self.get_path()


# Clean up cache
def _clean():
    for glovebox in cache:
        glovebox.delete()


# At exit, clean!
atexit.register(_clean)
