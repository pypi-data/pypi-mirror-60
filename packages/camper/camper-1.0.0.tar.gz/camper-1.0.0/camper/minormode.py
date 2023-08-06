from functools import partial

try:
    from rv import rvtypes
except ImportError:
    from dummyrv import rvtypes


class Binding(object):
    def __init__(self, event_name, event_handler, description, **kwargs):
        self._data = {
            'event_name': event_name,
            'event_handler': event_handler,
            'description': description,
        }
        if kwargs:
            self._data.update(kwargs)

    def __getattribute__(self, item):
        if item == '_data':
            return super(Binding, self).__getattribute__(item)

        try:
            return self._data[item]
        except KeyError:
            return None

    def run(self, event_name, *args, **kwargs):
        if self.qualifier:
            qualifiers = self.qualifier
            if not isinstance(qualifiers, list):
                qualifiers = [qualifiers]
            for q in qualifiers:
                if not q(*args, **kwargs):
                    return

        if self.handler:
            handlers = self.handler
            if not isinstance(handlers, list):
                handlers = [handlers]
            for h in handlers:
                h(*args, **kwargs)


class MinorMode(rvtypes.MinorMode):

    mode_name = None
    sort_key = None
    sort_order = None

    def __init__(self):
        super(MinorMode, self).__init__()

        if self.mode_name is None:
            self.mode_name = self.__class__.__name__
        if self.sort_key is None:
            self. sort_key = self.mode_name
        if self.sort_order is None:
            self.sort_order = 10

        self.bindings = dict()
        self.menu_bindings = list()
        self.event_bindings = list()
        self.menu = list()
        self.setup_bindings()
        self.setup_menu()

        self.init(self.mode_name,
                  self.event_bindings,
                  None,
                  self.menu,
                  self.sort_key,
                  self.sort_order)

    def setup_menu(self):
        self.menu = []

    def setup_bindings(self):
        pass

    def rebuild_menu(self):
        pass

    def bind_menu(self):
        pass

    def bind_event(self, event_name, event_handler, description, **kwargs):

        if not isinstance(event_name, list):
            event_name = [event_name]

        binding = Binding(event_name,
                          event_handler,
                          description,

                          **kwargs)
        self.bindings[id(binding)] = binding

        for e in event_name:
            self.event_bindings.append((e, partial(self.run_binding, id(binding), e), description))

    def unbind_event(self):
        pass

    def run_binding(self, binding_id, event_name, *args, **kwargs):
        try:
            binding = self.bindings[binding_id]
        except KeyError:
            print('Cannot find binding: ', binding_id)
            return

        try:
            binding.run(*args, **kwargs)
        except Exception:
            print('Error encountered: ', event_name)

        try:
            for arg in args:
                if arg.__class__.__name__ == 'Event' and hasattr(arg, 'reject'):
                    arg.reject()
                    break
        except Exception:
            print('Error encountered calling event.reject()')

