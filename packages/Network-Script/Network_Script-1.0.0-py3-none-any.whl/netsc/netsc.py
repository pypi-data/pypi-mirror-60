from .struct import objects2data, data2objects, return2data

class NetworkScript:
    """Abstract class
Must define:
    sock : socket.socket
    wrapped : object"""
    attrs = []
    chunk_size = 8192

    def __init__(self):
        raise NotImplementedError('Abstract class')
    def __get_call(self, funcname, args=(), kwargs={}):
        if hasattr(self, funcname):
            getattr(self, funcname)(*args, **kwargs)
    def _wrapped_call(self, attr, args):
        ret = getattr(self.wrapped, attr)(*args)
        ret = self.__get_call('_adj_return_%s' % attr, ret)
        data = return2data(ret)
        self.sock.send(data)
        self.__get_call('_post_call_%s' % attr)
        return ret
    def _message(self, name, args=(), kwargs={}):
        if name in attrs:
            self.__get_call('_pre_func_getattr')
            self.__get_call('_attr_get', (name,))
            self.sock.send(objects2data('getattr', name))
            while True:
                res = data2objects(self.sock.recv(self.chunk_size))
                if res['return']: break
                else:
                    self._wrapped_call(res['name'], res['args'])
            self.__get_call('_post_func_getattr')
            return res['args']
        else:
            self.__get_call('_pre_func_%s' % name)
            args = self.__get_call('_adj_args_%s' % name, args, kwargs)
            self.sock.send(objects2data(name, *args))
            while True:
                res = data2objects(self.sock.recv(self.chunk_size))
                if res['return']: break
                else:
                    self._wrapped_call(res['name'], res['args'])
            self.__get_call('_post_func_%s' % name)
            return res['args']
    def poll(self):
        while True:
            res = data2objects(self.sock.recv(self.chunk_size))
            if res['return']: continue
            else: break
        return self._wrapped_call(res['name'], res['args'])

__all__ = ['NetworkScript']