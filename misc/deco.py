
import time

def time_this(func):
    """decorator to time functions"""

    def wrapper(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        print "%s completed in %i seconds" % (func.__name__, time.time() -t0)
        return result
    return wrapper


# from http://mail.python.org/pipermail/python-list/2007-July/450302.html
import logging
import traceback

def log_debug(func):
    """Returns a function object that transparently wraps the
parameter with the HelpDebug function"""
    def wrapper(*args, **kwargs):
        try:
            logging.debug( 'called as %s(%s, %s)'  \
                % (func.__name__,",".join(map(str,args)),"".join(["%s=%s" % (str(k),str(v)) for k,v in kwargs])))
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

    @log_debug
    def divide(a,b):
        return a/b

    d1 = divide(1,2.)
    d2 = divide(1,0)
