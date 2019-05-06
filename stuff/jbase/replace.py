import sys

from item import Item

class Replace(Item):
    """Replacement class, can print nml"""
    def __init__(self, **kwargs):
        super(Replace, self).__init__(**kwargs)
        if len(sys.argv) == 2 and sys.argv[1] == 'print_nml':
            self.print_nml()
    def print_nml(self):
        print("NML print test of {0}".format())
