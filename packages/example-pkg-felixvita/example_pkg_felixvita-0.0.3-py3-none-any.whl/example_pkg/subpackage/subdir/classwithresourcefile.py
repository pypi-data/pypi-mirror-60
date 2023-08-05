import os


class ClassWithResourceFile:
    def __init__(self):
        # This does not work with Cython
        dirname = os.path.dirname(os.path.realpath(__file__))

        # Here's a replacement
        # it's fine to use /subpackage/resourcefile.txt
        # it's not ok to use ~markus/mycode/thislibrary...
        # it's also not ok to use, that the library is installed next to the application:
        # ../samplelibrary/subpackage/resourcefile.txt

        # dirname =

        filename = 'resourcefile.txt'
        with open(os.path.join(dirname, filename)) as f:
            self.numbers = f.readlines()

    def get_numbers(self):
        return self.numbers
