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
        this.options = options;
        for(var key in DEFAULTS){
            this.url += key + '=' 
                + (options[key] || DEFAULTS[key]) + '&';
        }
        // NASA doesn't like this...
        this.url = this.url.replace('?&','?');
        // NOTE: set USE_MERCATOR = true; after constructor call as desired.
        this.USE_MERCATOR = 0;
    }

    // inherit from the tile layer.
    var tl = new GTileLayer(new GCopyrightCollection(""), 1, 17);
    _wmslayer.prototype = tl;
    _wmslayer.prototype.getTileUrl = function(a, b, c){
        var lULP = new GPoint(a.x*256,(a.y+1)*256);
        var lLRP = new GPoint((a.x+1)*256,a.y*256);
        var lUL = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lULP,b,c);
        var lLR = G_NORMAL_MAP.getProjection().fromPixelToLatLng(lLRP,b,c);    
        var url;
        if(this.USE_MERCATOR){
            url = this.url + 'BBOX=' 
                            + dd2MercMetersLng(lUL.x) + "," 
                            + dd2MercMetersLat(lUL.y) + ","
                            + dd2MercMetersLng(lLR.x) + "," 
                            + dd2MercMetersLat(lLR.y) 
                            + '&SRS=EPSG:900913'  
        }
        else {
            url = this.url + 'BBOX=' + [lUL.x, lUL.y, lLR.x, lLR.y].join(",")
                            + '&SRS=EPSG:4326';
        }
        if(this.options.NO_CACHE){ url +='&r=' + (new Date()).getTime(); }
        return url;
        
    };
    _wmslayer.prototype.getOpacity = function(){
        return this.opacity;
    };
    return _wmslayer;

}();


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
