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
        if funcname in dir(self):
            getattr(self, funcname)(*args, **kwargs)
    def _adj_return(self, name, preret):
        ret = self.__get_call('adj_return_%s' % name, (preret,))
        if ret is None:
            ret = preret
        return ret
    def _wrapped_call(self, attr, args):
        ret = getattr(self.wrapped, attr)(*args)
        ret = self._adj_return(attr, ret)
        data = return2data(ret)
        self.sock.send(data)
        self.__get_call('post_call_%s' % attr)
        return ret
    def _adj_args(self, name, args, kwargs):
        ret = self.__get_call('adj_args_%s' % name, args, kwargs)
        if ret is None:
            ret = args
        return ret
    def _message(self, name, args=(), kwargs={}):
        self.__get_call('pre_func_%s' % name)
        args = self._adj_args(name, args, kwargs)
        self.sock.send(objects2data(name, *args))
        while True:
            res = data2objects(self.sock.recv(self.chunk_size))
            if res['return']: break
            else:
                self._wrapped_call(res['name'], res['args'])
        self.__get_call('post_func_%s' % name)
        return res['args']
    def __getattr__(self, attr):
        if attr in self.attrs:
            do_getattr = self.__get_call('pre_getattr_%s' % attr)
            if do_getattr:
                func = '__getattr__'
            else:
                func = '__getattribute__'
            ret = self._message(func, (attr,))
            self.__get_call('post_getattr_%s' % attr)
            return ret
        else:
            def wrapper_function(*args, **kwargs):
                nonlocal attr
                return self._message(attr, args, kwargs)
            return wrapper_function
    def poll(self):
        while True:
            res = data2objects(self.sock.recv(self.chunk_size))
            if res['return']: continue
            else: break
        return self._wrapped_call(res['name'], res['args'])

__all__ = ['NetworkScript']