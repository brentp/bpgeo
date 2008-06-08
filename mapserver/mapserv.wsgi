#!/usr/bin/python2.5

import mapscript
from cgi import parse_qsl

try: import Image
except: Image = None

from cStringIO import StringIO


def application(environ, start_response):
    winput = dict(parse_qsl(environ['QUERY_STRING']))

    try:
        mapfile = winput['map']
        wms = mapscript.mapObj(mapfile)
        bbox = map(float, winput['BBOX'].split(","))
        w, h = int(winput['WIDTH']), int(winput['HEIGHT'])
    except Exception, e:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['ERROR (are you sure the path to the mapfile is correct?):\n' 
                + str(e)]


    format = winput.get('FORMAT', 'image/png')
    extension = format[format.find('/') + 1:]
    start_response('200 OK', [('Content-Type', format)])

    req = mapscript.OWSRequest()

    for k, v in winput.items():
        req.setParameter(k, v)

    if not 'buffer' in winput or Image is None:
        wms.loadOWSParameters(req)
        return [wms.draw().getBytes()]
        
            
    buffer = 0.05 # pct per side.

    rangex = bbox[2] - bbox[0]
    rangey = bbox[3] - bbox[1]

    xdelta = int(round(w * buffer)) # e.g add 13px on each side
    ydelta = int(round(h * buffer)) # for 256x256 image

    bbox[0] -= rangex * buffer # extend the
    bbox[1] -= rangey * buffer # bbox in
    bbox[2] += rangex * buffer # all
    bbox[3] += rangey * buffer # directions

    # http://trac.osgeo.org/mapserver/ticket/2299
    req.setParameter('WIDTH',  str(w + 2 * xdelta))   # and adjust the
    req.setParameter('HEIGHT', str(h + 2 * ydelta))   # h, w by the same
    req.setParameter('BBOX', ",".join(map(str,bbox))) # amount
    req.setParameter("STYLES", "")
    req.setParameter("REQUEST", "GetMap")

    # PIL doesnt like interlace.
    wms.outputformat.setOption('FORMATOPTIONS', 'INTERLACE=OFF')
    wms.loadOWSParameters(req)

    im = Image.open(StringIO(wms.draw().getBytes()))
    if im is None: return ['']
    # crop the image back to the requested w, h
    im = im.crop((xdelta, ydelta, w + xdelta, h + ydelta))

    buffer = StringIO()
    im.save(buffer, extension)
    buffer.seek(0)
    data = buffer.read()
    return [ data ]

