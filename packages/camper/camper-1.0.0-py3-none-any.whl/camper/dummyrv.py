
class Dummy(object):
    def __init__(self, *args, **kwargs):
        return

    def __getattr__(self, *args, **kwargs):
        return Dummy(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return


commands = Dummy('commands')
extra_commands = Dummy('extra_commands')
rvtypes = Dummy('rvtypes')
