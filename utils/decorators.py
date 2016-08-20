from functools import wraps
import binascii


def set_log_namespace(func):
    """
    Sets log_namespace as <classname>.<func_name>
    """
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        log_namespace = self.__class__.__name__ + '.' + func.__name__
        try:
            self.log.namespace = log_namespace
        except AttributeError:
            try:
                self.temp_log.namespace = log_namespace
            except AttributeError:
                pass
        return func(self, *args, **kwargs)
    return func_wrapper


def sugarcoat_data(func):
    """
    Makes data received over TCP and UDP readable
    """
    @wraps(func)
    def func_wrapper(self, data, *args, **kwargs):
        if isinstance(data, (list, dict)):
            data = data
        else:
            self.log.debug('Sugar Coating %s' % data)
            sugar = [binascii.unhexlify(binascii.hexlify(d)) for d in data]
            data = ''.join(sugar)
        return func(self, data, *args, **kwargs)
    return func_wrapper
