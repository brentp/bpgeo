/* 
A Simple Set of Functions to overlay WMS images in Google maps.



Consists mainly of change in code layout from John Deck's wms236.js: 
http://chignik.berkeley.edu/google/wmstest236.html

CHANGES from wms236.js: 
+ No global variables. 
+ CustomGetTileUrl (?) replaced with prototype.
+ any parameters can be sent in on the constructor.


*/

var WMSLayer = function(){
    var MAGIC_NUMBER = 6356752.3142; 
    var WGS84_SEMI_MAJOR_AXIS = 6378137.0;
    var WGS84_ECCENTRICITY = 0.0818191913108718138;
    var DEG2RAD = Math.PI/180;
    var MERC_ZOOM_DEFAULT = 15;
    var DEFAULTS = {
         FORMAT       : 'image/png'
        ,VERSION      : '1.1.1'
        ,STYLES       : ''
        ,REQUEST      : 'GetMap'
        ,SERVICE      : 'WMS'
        ,TRANSPARENT  : 'TRUE'
        ,WIDTH        : 256
        ,HEIGHT       : 256
        ,REASPECT     : 'FALSE'
        ,LAYERS       : ''
    };

    function dd2MercMetersLng(p_lng) {
        return WGS84_SEMI_MAJOR_AXIS * (p_lng*DEG2RAD);
    }

    function dd2MercMetersLat(p_lat) {
        var lat_rad = p_lat * DEG2RAD;
        return WGS84_SEMI_MAJOR_AXIS * Math.log(Math.tan((lat_rad + PI / 2) / 2) 
                * Math.pow( ((1 - WGS84_ECCENTRICITY * Math.sin(lat_rad)) 
                / (1 + WGS84_ECCENTRICITY * Math.sin(lat_rad)))
                , (WGS84_ECCENTRICITY/2)));
    }

    var _wmslayer = function(url,options){
        if(! options){ options = {}}
        this.url = url.indexOf('?') != -1 && url + '&' || url + '?';
        for(var key in DEFAULTS){
            this.url += key + '=' 
                + (options[key] || DEFAULTS[key]) + '&';
        }
        // NASA doesn't like this...
        this.url = this.url.replace('?&','?');
        // NOTE: set USE_MERCATOR = true; after constructor call as desired.
        this.USE_MERCATOR = false;
    }

    // inherit from the tile layer.
    var tl = new GTileLayer(new GCopyrightCollection(""), 1, 17);
    _wmslayer.prototype = tl;
    _wmslayer.prototype.getTileUrl = function(a, b, c){
        var lULP = new GPoint(a.x*256,(a.y+1)*256);
        var lLRP = new GPoint((a.x+1)*256,a.y*256);
        var lUL = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lULP,b,c);
        var lLR = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lLRP,b,c);    
        if(this.USE_MERCATOR){
            return this.url + 'BBOX=' 
                            + dd2MercMetersLng(lUL.x) + "," 
                            + dd2MercMetersLat(lUL.y) + ","
                            + dd2MercMetersLng(lLR.x) + "," 
                            + dd2MercMetersLat(lLR.y) 
                            + '&SRS=EPSG:41001'  
        }
        else {
            var url = this.url + 'BBOX=' + [lUL.x, lUL.y, lLR.x, lLR.y].join(",")
                            + '&SRS=EPSG:4326';
            return url;
        }
        
    };
    _wmslayer.prototype.getOpacity = function(){
        return this.opacity;
    };
    return _wmslayer;

}();
