
import logging
import traceback
import sys
import time

def time_this(func, out=None):
    if out is None:
        out = sys.stderr
    """decorator to time functions"""
    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        print >>out, "%s completed in %i seconds" % (func.__name__, time.time() -t0)
        return result
    return wrapper


# from http://mail.python.org/pipermail/python-list/2007-July/450302.html
class log_calls:
    def __init__(self, func, out=None):
        if out is None: out = sys.stderr
        else: sys.stderr = out
        self.out = out
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            args_str   = ", ".join(map(str, args))
            format_str = "%s(%s" % (self.func.__name__, args_str)
            if kwargs:
                kwargs_str = ", ".join(["%s=%s" % (str(k), str(v)) for k, v in kwargs.items()])
                format_str += ", " + kwargs_str
            format_str += ')'
            print >>self.out, "called as:\n" + format_str + "\n"
            result = self.func(*args, **kwargs)
            print >>self.out, str(result)
            return result

        except SystemExit:
            raise

        except Exception, error:
            print >>self.out, error
            print >>self.out, traceback.print_exc()
        return 


def log_debug(func):
    """Returns a function object that transparently wraps the
        parameter with the HelpDebug function"""
    def wrapper(*args, **kwargs):
        try:
            args_str   = ", ".join(map(str, args))
            format_str = "%s(%s" % (func.__name__, args_str)
            if kwargs:
                kwargs_str = ", ".join(["%s=%s" % (str(k), str(v)) for k, v in kwargs.items()])
                format_str += ", " + kwargs_str
            format_str += ')'
            logging.debug( 'called as:' + format_str)
            result = func(*args, **kwargs)
            logging.log(logging.INFO,str(result))
            return result

        except SystemExit:
            raise

        except Exception, error:
            logging.log(logging.ERROR, error)
            print traceback.print_exc()
        return 

    return wrapper


if __name__ == "__main__":
    
    @time_this
    def longfunc(a,k=2):
        time.sleep(k)
        return a

    print longfunc(2,1)

    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    def divide(a,b, **kwargs):
        return a/b
    divide = log_calls(divide, out=open('/tmp/asdf.txt','w'))

    d1 = divide(1,2.,c=3, d=3, e=None, f=range(1000))
    d2 = divide(1,0)
