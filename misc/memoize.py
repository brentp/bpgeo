import shelve
import cPickle
import os

# modified slightly from
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/466320/index_txt
# to create a persistent cache.

cachedir = "/tmp/shelved/"
if not os.path.exists(cachedir): os.mkdir(cachedir)

class memoize(object):
    def __init__(self, func,mode='c'):
        self.func = func
        file = os.path.join(cachedir,"%s.shelve" % func.func_name )
        self._cache = shelve.open(file,mode)
        self._file = file

    def __call__(self, *args, **kwds):
        key = args
        if kwds:
            items = kwds.items()
            items.sort()
            key += tuple(items)
        try:
            if key in self._cache:
                return self._cache[key]
            self._cache[key] = result = self.func(*args, **kwds)
            self._cache.sync()
            return result
        except TypeError:
            try:
                dump = cPickle.dumps(key)
            except cPickle.PicklingError:
                return self.func(*args, **kwds)
            else:
                if dump in self._cache:
                    return self._cache[dump]
                self._cache[dump] = result = self.func(*args, **kwds)
                self._cache.sync()
                return result


if __name__ == "__main__": # Some examples
    @memoize
    def fibonacci(n):
       "Return the n-th element of the Fibonacci series."
       if n < 3:
          return 1
       return fibonacci(n-1) + fibonacci(n-2)

    a = [fibonacci(i) for i in xrange(1, 701)]

    @memoize
    def pow(x, p=2):
        if p==1:
            return x
        else:
            return x * pow(x, p=p-1)

    print [pow(3, p=i) for i in xrange(1, 6)]

    @memoize
    def printlist(l):
        print l
    printlist([1,2,3,4])
