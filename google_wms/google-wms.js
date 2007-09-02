/* 
A Simple Set of Functions to overlay WMS images in Google maps.



Consists mainly of change in code layout from John Deck's wms236.js: 
http://chignik.berkeley.edu/google/wmstest236.html

CHANGES from wms236.js: 
+ No global variables. 
+ CustomGetTileUrl (?) replaced with prototype.
+ any parameters can be sent in on the constructor.


*/
if (typeof GWMS == 'undefined'){ var GWMS = {}; }

GWMS.Layer = function(){
    var MAGIC_NUMBER          = 6356752.3142; 
    var WGS84_SEMI_MAJOR_AXIS = 6378137.0;
    var WGS84_ECCENTRICITY    = 0.0818191913108718138;
    var DEG2RAD               = Math.PI/180;

    var DEFAULTS = {
         LAYERS       : ''
        ,FORMAT       : 'image/png'
        ,HEIGHT       : 256
        ,REASPECT     : 'FALSE'
        ,REQUEST      : 'GetMap'
        ,STYLES       : ''
        ,SERVICE      : 'WMS'
        ,TRANSPARENT  : 'TRUE'
        ,VERSION      : '1.1.1'
        ,WIDTH        : 256
    };

    var WGS84_DEG2RAD = WGS84_SEMI_MAJOR_AXIS * DEG2RAD; 
    function DD_to_meters_lng(p_lng) {
        return WGS84_DEG2RAD * p_lng;
    }

    PI2 = Math.PI / 2;
    function DD_to_meters_lat(p_lat) {
        var lat_rad = p_lat * DEG2RAD;
        var WGS84_SIN_LAT_RAD = WGS84_ECCENTRICITY * Math.sin(lat_rad);
        return WGS84_SEMI_MAJOR_AXIS * Math.log(Math.tan((lat_rad + PI2) / 2) 
                * Math.pow( ((1 - WGS84_SIN_LAT_RAD) 
                / (1 + WGS84_SIN_LAT_RAD))
                , (WGS84_ECCENTRICITY/2)));
    }

    var _wmslayer = function(url,options, title){
        if(! options){ options = {}}
        this.each_draw = {};
        this.url = url.indexOf('?') != -1 && url + '&' || url + '?';
        this.title = title;
        this.options = options;
        for(var key in DEFAULTS){
            this.url += key + '=' 
                + (options[key] || DEFAULTS[key]) + '&';
        }
        // NASA doesn't like this...
        this.url = this.url.replace('?&','?');
        // NOTE: set USE_MERCATOR = true; after constructor call as desired.
        this.USE_MERCATOR = 0;
        this.opacity = 0.999;
    }

    // inherit from the tile layer.
    var proj = G_NORMAL_MAP.getProjection();
    _wmslayer.prototype = new GTileLayer(new GCopyrightCollection(""), 1, 19);
//    _wmslayer.prototype = GTileLayer.prototype;
    _wmslayer.prototype.getTileUrl = function(a, b, c){
        var lULP = new GPoint(a.x*256,(a.y+1)*256);
        var lLRP = new GPoint((a.x+1)*256,a.y*256);
        var lUL = proj.fromPixelToLatLng(lULP,b,c);
        var lLR = proj.fromPixelToLatLng(lLRP,b,c);    
        var url;
        if(this.USE_MERCATOR){
            url = this.url + 'BBOX=' 
                           + DD_to_meters_lng(lUL.x) + "," 
                           + DD_to_meters_lat(lUL.y) + ","
                           + DD_to_meters_lng(lLR.x) + "," 
                           + DD_to_meters_lat(lLR.y) 
                           + '&SRS=EPSG:54004';
        }
        else {
            url = this.url + 'BBOX=' + [lUL.x, lUL.y, lLR.x, lLR.y].join(",")
                           + '&SRS=EPSG:4326';
        }

        if(this.options.NO_CACHE){ url +='&r=' + (new Date()).getTime(); }
        for ( var key in this.each_draw){
            url += '&' + key + '=' + this.each_draw[key];
        }
        return url;
        
    };
    _wmslayer.prototype.getOpacity = function(){
        return this.opacity;
    };
    _wmslayer.prototype.isPng = function(){ return 1; };
    return _wmslayer;

}();

GWMS.HybridSandwich = function(/*typename, [{url:'http://...' ,url_options:{...}, ...], minResolution, maxResolution */) {
    var tls = G_HYBRID_MAP.getTileLayers();
    var layers = [tls[0]]
    for(var layer in arguments[1]){
        layer = arguments[1][layer];
        var tl = new GWMS.Layer(layer.url, layer.url_options)
        tl.USE_MERCATOR = layer.options && layer.options.USE_MERCATOR;
        layers.push(tl);
    }
    layers.push(tls[1]);
    var mt = new GMapType(layers, G_NORMAL_MAP.getProjection(), arguments[0])
    mt.getMinResolution = function(){ return arguments[2] || 0;  }
    mt.getMaxResolution = function(){ return arguments[3] || 19; }
    return mt
};

GWMS.OverNormal = function(/*typename, [{url:'http://...' ,url_options:{...}, ...], minResolution, maxResolution */) {
    var layers = [G_NORMAL_MAP.getTileLayers()[0]];
    for(var layer in arguments[1]){
        layer = arguments[1][layer];
        var tl = new GWMS.Layer(layer.url, layer.url_options);
        layers.push(tl);
        tl.USE_MERCATOR = layer.options && layer.options.USE_MERCATOR;
    }
    var mt = new GMapType(layers, G_NORMAL_MAP.getProjection(), arguments[0])
    mt.getMinResolution = function(){ return arguments[2] || 0;  }
    mt.getMaxResolution = function(){ return arguments[3] || 19; }
    return mt
};

GMap2.prototype.fromLatLngToPixel = function(ll){
    var cornerll = map.fromContainerPixelToLatLng(new GPoint(0,0),true);
    var cornerxy = this.fromLatLngToDivPixel(cornerll);

    var imgxy = this.fromLatLngToDivPixel(ll);
    imgxy.x -= cornerxy.x;
    imgxy.y -= cornerxy.y;
    return imgxy;
}

/* take an x and y and the wmslayer and do a get featureinfo requests.  */
GMap2.prototype.getFeatureInfo = function(pt,wmslayer){
    if(!pt){ return false; }
    var tpt = pt;
    var imgxy = this.fromLatLngToPixel(tpt);
    var bds = this.getBounds().toString();
    bds = bds.replace(/[\)\(\s]/g,'').split(",");
    bds = [bds[1], bds[0], bds[3], bds[2]].join(",");
    var url = wmslayer.url;
    url = url.replace('GetMap','GetFeatureInfo')
             .replace('WIDTH=256', 'WIDTH=' + this.getSize().width)
             .replace('HEIGHT=256', 'HEIGHT=' + this.getSize().height)
             + '&X=' + imgxy.x
             + '&Y=' + imgxy.y
             + '&SRS=EPSG:' + (wmslayer.USE_MERCATOR ? '41001' : '4326')
             + '&BBOX=' + bds
             + '&INFO_FORMAT=text/html';

    var ma = url.match(/(&LAYERS=[^&]+)/)[0];
    url += ma.replace('&LAYERS','&QUERY_LAYERS');

    var self = this;
    GDownloadUrl(url,function(data){
        self.closeInfoWindow()
        if(!data){ return false;}
        self.openInfoWindowHtml(tpt, data);
    });

};

function WMSControl(url_path){ this.url_path = url_path; }
WMSControl.prototype = new GControl(true, false) ;
WMSControl.prototype.getDefaultPosition = function() {
  return new GControlPosition(G_ANCHOR_TOP_RIGHT, new GSize(7, 31));
};

WMSControl.prototype.initialize = function(map){

    // Make a container
    var div = document.createElement('div');
    div.id = 'wmscontrol_container';
    div.innerHTML = '<p align="center">WMS LAYERS</p>';
    GEvent.addDomListener(div, 'click', function(e){
        e = e || window.event;
        var cbx = e.target || e.srcElement;
        if (!cbx.type || ! cbx.type.toUpperCase() == 'CHECKBOX'){ return false;}
        var idx = cbx.id.replace('wmscbx','') - 1;
        var layer = WMSControl.layers[idx];
        return cbx.checked ? layer.show() : layer.hide();

    });
    map.getContainer().appendChild(div);
    this.map = map;
    this.n = 0;
    return div;
}
WMSControl.layers = [];
WMSControl.HTML = "<div class='wmscontrol'><input type='checkbox' id='wmscbx' CHECKED ><span class='wmstitle'>TITLE</span></div>";

WMSControl.prototype.addOverlayLayer = function(wmslayer /*, hide=false */){
    this.map.addOverlay(wmslayer);
    var n = ++this.n;
    var hide = arguments.length > 1 && arguments[1]
    if(arguments.length > 2 && arguments[1] ){ wmslayer.hide(); }

    html = WMSControl.HTML
    var wmsc = document.getElementById('wmscontrol_container');
    var title = wmslayer.getTileLayer().title;
    if(hide){
        html = html.replace('CHECKED','');
        wmslayer.hide();
    }
    html = html.replace('TITLE',title).replace('wmscbx','wmscbx' + n);
    wmsc.innerHTML += html;
    var wmscbx = document.getElementById('wmscbx' + n);
    // change it so it will be unique;
    WMSControl.layers.push(wmslayer);

}
