from os import path

basepath = path.dirname(path.realpath(__file__))
build_path = lambda *args: path.sep.join(args)
build_absolute_path = lambda p: path.sep.join([basepath] + p.split('/'))
