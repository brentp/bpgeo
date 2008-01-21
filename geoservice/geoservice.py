#!/usr/bin/python
'''
A GeoService javascript and url-based API.

=============
geoservice.py
=============

Overview
--------

geoservice.py is a web.py script that provides:
    geocoding
    reverse_geocoding
    projection

Details
-------
with a url api and a javascript API that calls those urls.
see http://path/to/geoservice.py/   (note trailing slash)
available here:

    http://firecenter.berkeley.edu/proxy/bpgeo/geoservice.py/
    and view html source for that example application.

also see:

    http://kellylab.berkeley.edu/blog/?p=169

'''

__docformat__ = "restructuredtext"
__author__  = "Brent Pedersen <bpederse@gmail.com"
__version__ = "0.0.3"
__license__ = "MIT"

from geopy import geocoders
import simplejson as SJ
import sys
import web
from urllib import urlopen
try:
    from osgeo import ogr
    from osgeo import osr
except:
    import ogr
    import osr

YAHOO_ID = 'brent_s_p'
# see also
# http://hobu.biz/index_html/geographic-projection-web-services-redux

def project(x,y,to_epsg=4326,from_epsg=4326):
    '''
    project `x`, `y` coordinates from `from_epsg` to `to_epsg`
    requires ogr python bindings. eventuall use a web
    service (hobu's?) to remove this dependency. 

    >>> project(-121,43,to_epsg=26910)
    {'y': 4762755.6415722491, 'epsg': 26910, 'x': 663019.07008285949}
    '''

    x,y = float(x),float(y)

    ifrom = osr.SpatialReference()
    ifrom.ImportFromEPSG(from_epsg)

    p = ogr.CreateGeometryFromWkt('POINT(%f %f)' % (x, y))
    p.AssignSpatialReference(ifrom)

    ito = osr.SpatialReference()
    ito.ImportFromEPSG(to_epsg)

    p.TransformTo(ito)
    return {'epsg': to_epsg, 'x':p.GetX(), 'y': p.GetY()}


class Yahoo(geocoders.Yahoo):
    ''' geopy prints to STDOUT by default. overide that here'''
    def geocode_url(self, url, exactly_one=True):
        page = urlopen(url)
        parse = getattr(self, 'parse_' + self.output_format)
        return parse(page, exactly_one) 

class source(object):
    ''' print out contents of this file.
    mapped to url: http://path/to/geoservice.py/source/ 
    '''
    def GET(self):
        if not web.input(html=False).html:
            web.header('Content-type', 'text/plain')
            print open(__file__).read()
        else:
            # why wont this work???
            web.header('Content-type', 'text/html')
            from docutils.core import publish_file
            publish_file(open(__file__)
                      ,writer_name='html')

class reverse_geocode(object):
    '''take an x,y (and optional EPSG) and try to use geonames
    to reverse geocode.
    mapped to url: http://path/to/geoservice.py/reverse_geocode/x/y?epsg=4326
    '''
    url = 'http://ws.geonames.org/findNearestAddressJSON?lat=%s&lng=%s'
    def GET(self,x,y):
        web.header('Content-type', 'text/javascript')
        epsg = int(web.input(epsg='4326').epsg)
        res = project(x,y,from_epsg=epsg)
        rurl = self.url % (res['y'],res['x'])
        # get the reverse geocoded stuff
        ds = SJ.loads( urlopen(rurl).read())
        print SJ.dumps(ds);
        

class geocode(object):
    '''take an address (and optional EPSG) and try to use geonames
    to reverse geocode.
    mapped to url: http://path/to/geoservice.py/geocode/address+string?epsg=4326
    '''
    def GET(self,address):
        web.header('Content-type', 'text/javascript')
        to_epsg = int(web.input(epsg='4326').epsg)
        gc = Yahoo(YAHOO_ID)
        res = gc.geocode(address)
        #print >>open('/tmp/geocode.log','a'), res
        if len(res) > 1:
            prj = project(res[1][1], res[1][0], to_epsg=to_epsg)
            print SJ.dumps(prj),

class example(object):
    ''' this, is the default action for the script. show an example page
    mapped to url: http://path/to/geoservice.py/
    '''
    def GET(self):
        web.header('Content-type', 'text/html')
        print '''\
<html>
    <head>
        <!-- include the necessary javascript -->
        <script src="../geoservice.py/javascript"></script>
        <script>
            var gEBI = function(id){ return document.getElementById(id)};

            // define a callback. probably something better than alert.
            geocode.callback = function(result){
                alert('x: ' + result.x + 'y: ' + result.y);
                reverse_geocode(result.x,result.y,4326);
            }

            function init(){
                gEBI('run_geocode').onclick = function(){
                    geocode(gEBI('address').value,gEBI('epsg').value);
                };
            }

        </script>
    </head>
<body onload=init()>
    <div id='geocoded'> </div>
    <p>address:<input size=40 type='text' id='address' 
       value='university of california, berkeley, CA' /></p>
    <p>epsg:<input type='text' id='epsg' value='4326' /></p>
    <input type='submit' id='run_geocode' value='geocode'/>
</body>
</html>
        '''
       


class javascript(object):
    ''' print out the javascript functions which can be used to call
    the python methods in this script. must be on the same domain to
    allow use of AJAX.
    mapped to url: http://path/to/geoservice.py/javascript/ 
    '''
    def GET(self):
        web.header('Content-type', 'text/javascript')
        print '''\
    // a simple javascript geocode function that makes calls
    // to the python methods in geoservice.py
    function geocode(address,epsg){
        epsg = epsg != undefined ? epsg : '4326'
        jfetch('%s/geocode/' 
            + address + '?epsg=' + epsg
            , function(res){ 
                if(res.indexOf('internal server error') != -1){
                    return geocode.error();
                }
                eval('res=' + res); 
                geocode.callback(res) 
              });
    }
    // override this with your own callback
    geocode.callback = function(res){
        alert(res.x + res.y);
    };
    geocode.error = function(){
        return 'error';
    }

    function reverse_geocode(x,y,epsg){
        epsg = epsg != undefined ? epsg : '4326'
        jfetch('reverse_geocode/' 
            + x + '/' + y +  '?epsg=' + epsg
            , function(res){ 
                if (res.indexOf('{}') != -1) return reverse_geocode.error();
                eval('res=' + res);
                reverse_geocode.callback(res);
              }
        );

    }

    reverse_geocode.error = function(){
        return 'error';
    }
    reverse_geocode.callback = function(res){
        alert(res.address.postalcode + '   ' + res.address.placename);
    }

    function jfetch(url,t,o) {
        var req = jfetch.xhr();
        req.open("GET",url,true);
        req.onreadystatechange = function() {
            if(req.readyState == 4){
                var rsp = req.responseText;
                if(t.constructor == Function) return t.apply(o,[rsp]);
                t = document.getElementById(t);
                t[t.value ==undefined ? 'innerHTML': 'value'] = rsp;
                req = null;
            }
        };
        req.send(null);
    }
    jfetch.xhr =
        (window.ActiveXObject)
    ? function(){ return new ActiveXObject("Microsoft.XMLHTTP"); }
    : function(){ return new XMLHttpRequest()};
    ''' % web.ctx.env["SCRIPT_NAME"]

# map a url pattern to a class
# see http://webpy.infogami.com/docs
urls = (
    '/geocode/(.*)', 'geocode'
    ,'/reverse_geocode/([^\/]+)/(.*)', 'reverse_geocode'
    ,'/javascript.*','javascript'
    ,'/source.*','source'
    ,'/.*','example'
    )

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] != 'test': 
        web.internalerror = web.debugerror
        web.run(urls,globals(), web.reloader)
    else:
        print "running tests..."
        # only one tests. could use twill as well...
        import doctest
        doctest.testmod()
