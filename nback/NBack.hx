import flash.display.Sprite;
import flash.display.Shape;
import flash.events.MouseEvent;
import flash.events.TimerEvent;
import flash.utils.Timer;
import flash.text.TextField;

class NBack extends Sprite {

    private static var timer:Timer;
    private static var hide_timer:Timer;
    // the n second timer.
    private static var time_step:Int = 3000;
    // how many milliseconds to show the blue square.
    private static var show_time:Int = 500;

    // how many time steps back to compare.
    private static var nback:UInt = 2;

    // the blue  to move around the screen.
    public static var rect_size:UInt = 80;
    public static var rect:Rect = new Rect();

    // a list of discrete locations that the rectangle can occupy.
    // the article doesnt say what is the resolution of the grid...
    // but seems to be 3 * 3. 5 * 5 is _very_ hard.
    static var grid = new Array<Array<Int>>();
    // the number of sqares per side in the grid. 
    // (3 * 3) gives 9 positions - 1 for the center.
    private static var grid_size:UInt = 3;

    // stores the past rect locations so we can compare against n back.
    static var grid_history = new Array<Int>();

    // paper also doesnt say how many letters...
    // todo. link these to sound. instead of txt.
    static var letters = ['C', 'P', 'T']; //, 'L'];
    static var letters_history = new Array<String>();

    public static var txt = new TextField(); 
    public var clear_txt:Bool;
    
    // keep track of and display correct/incorrect, total.
    static var stats_txt = new TextField();
    static var stats     = new Array<Int>();

    // show the current parameters. 
    static var params_txt = new TextField();

    public static function main(){
        //haxe.Firebug.redirectTraces();
        flash.Lib.current.stage.scaleMode = flash.display.StageScaleMode.NO_SCALE;
        flash.Lib.current.stage.align     = flash.display.StageAlign.TOP_LEFT;
        flash.Lib.current.addChild(new NBack());
    }

    
    public function new(){
        super()/*duper*/;
        read_pvars();
        init_grid(NBack.grid_size);
        register_events();
        setup_txt();
        // total, n missed, n correct, n incorrect. why array???
        stats = [0, 0, 0, 0];
    }
    private function read_pvars(){
        var p = flash.Lib.current.loaderInfo.parameters;
        if(p.time_step != null && p.time_step != ''){ 
            NBack.time_step = Std.parseInt(p.time_step); 
        }
        if(p.show_time != null && p.show_time != ''){ 
            NBack.show_time = Std.parseInt(p.show_time); 
        }
        if(p.nback != null && p.nback != ''){ 
            NBack.nback = Std.parseInt(p.nback); 
        }
        //flash.external.ExternalInterface.call('alert', NBack.show_time + "," + NBack.time_step);
    }

    private function setup_txt(){
        txt.x = flash.Lib.current.stage.stageWidth / 2  - 20;
        txt.y = flash.Lib.current.stage.stageHeight / 2 - 25;
        txt.styleSheet = styler();
        flash.Lib.current.addChild(txt);

        stats_txt.x = 4;
        stats_txt.y = 4;
        stats_txt.width = 400;
        stats_txt.styleSheet = new flash.text.StyleSheet();
        stats_txt.styleSheet.setStyle("p", {fontSize: 18, color: '#555555'});
        flash.Lib.current.addChild(stats_txt);
        stats_txt.htmlText = "<p>Stats:</p>";

        params_txt.styleSheet = new flash.text.StyleSheet();
        params_txt.styleSheet.setStyle("p", {fontSize: 18, color: '#555555'});
        params_txt.x = 4;
        params_txt.width = 400;
        params_txt.y = flash.Lib.current.stage.stageHeight - 24;
        params_txt.htmlText = "<p>Time Step: " + NBack.time_step
                            + ", Show Time: " + NBack.show_time
                            + ", N-back: " + NBack.nback
                            + "</p>";
        flash.Lib.current.addChild(params_txt);
    }
    static function styler(){ 
        var css = new flash.text.StyleSheet();
        css.setStyle("p", {fontSize: 50, color: "#000000"});
        return css;
    }

    private function cleanup(?e:TimerEvent){
        if(NBack.letters_history.length < 10){ return; }
        NBack.letters_history = NBack.letters_history.slice(-4);
        NBack.grid_history    = NBack.grid_history.slice(-4);
    }


    private function register_events(){
        timer = new Timer(NBack.time_step);
        flash.Lib.current.stage.addChild(rect);
        flash.Lib.current.stage.addEventListener(MouseEvent.CLICK, handle_click);
        timer.addEventListener(TimerEvent.TIMER, tick);
        hide_timer = new Timer(NBack.show_time, 1);
        hide_timer.addEventListener(TimerEvent.TIMER, clear_rect);

        var _cleanup_timer = new Timer(NBack.time_step * 25 - 1);
        _cleanup_timer.addEventListener(TimerEvent.TIMER, cleanup);
        _cleanup_timer.start();
        timer.start();
    }

    public function is_history_match(){
        var l = NBack.grid_history.length - 1; 
        if (NBack.grid_history[l] == NBack.grid_history[l - NBack.nback] 
              ||
            NBack.letters_history[l] 
                     == NBack.letters_history[l - NBack.nback]){
            return true;
        }
        return false;
    }


    public function handle_click(e:MouseEvent){
        // match to nback ago in grid_history or letters_history.
        if (is_history_match()){ 
            // green + for good. clicked at correct time.
            txt.styleSheet.setStyle("p", {color: '#00ff00', fontSize: 80});
            txt.htmlText = "<p>+</p>";
            stats[2] += 1;
        }
        else{
            // red - for bad == 'clicked but shouldn't have.
            txt.styleSheet.setStyle("p", {color: '#ff0000', fontSize: 80});
            stats[3] += 1;
            txt.htmlText = "<p>-</p>";
        }
        // they clicked so keep the ceter text showing.
        // to show if they were wrong / right.
        clear_txt = false;
    }

    public function clear_rect(e:TimerEvent){
        rect.graphics.clear();
        if(clear_txt){
            txt.htmlText = '';
        }
    }
        
    public function tick(e:TimerEvent){
        update_stats(! clear_txt);
        clear_txt = true;
        var xy = grid_choose();
        rect.x = xy[0];
        rect.y = xy[1];
        rect.draw(0x000000);

        var letter = txt_choose();
        txt.styleSheet.setStyle("p", {color: '#000000', fontSize: 50});
        txt.htmlText = "<p>" + letter + "</p>";
        hide_timer.start();
    }
    public function update_stats(did_click){
        stats[0] += 1; 
        if(! did_click  && is_history_match()){
            // should have clicked but didn't.
            stats[1] +=1;
        }
        stats_txt.htmlText = "<p>Stats: " 
            + stats[0] + " ticks, " 
            + stats[1] + " missed, " 
            + stats[2] + " correct, " 
            + stats[3] + " wrong</p>";
    }

    // choose the next xy from the grid.
    // can bias.
    public function grid_choose(){
        // - 1 because dont have the center tile.
        var grid_index = Std.random(grid_size * grid_size - 1);
        var last_index = NBack.grid_history[NBack.grid_history.length - 1];
        // dont let the same position show 2x.
        while (last_index == grid_index){
            grid_index = Std.random(grid_size * grid_size);
        }
        NBack.grid_history.push(grid_index);
        return NBack.grid[grid_index];
    }

    public function txt_choose(){
        var ltr = letters[Std.random(letters.length)];
        letters_history.push(ltr);
        return ltr;
    }
    /* the block can only occupy discrete locations in a grid.
       this sets the x, y location for that grid
    */
    public function init_grid(grid_size:UInt){
        // the full movie h, w
        trace(flash.Lib.current.stage.stageHeight);
        var dx = Math.round(flash.Lib.current.stage.stageWidth / (grid_size  ));
        var dy = Math.round(flash.Lib.current.stage.stageHeight / (grid_size ));
        trace(dx, dy);
        for(i in 0 ... grid_size){
            for(j in 0 ... grid_size){
                // attempt to account for the grid size and the
                // rectangle size ...
                // dont show the center tile. (only works for odd
                // number grid size.
                if (i == (grid_size - 1) / 2  && j == (grid_size - 1) / 2 ){ continue; }
                var x = Std.int(dx/2 + dx * i - NBack.rect_size/2); 
                // add to allow room for stats.
                var y = 5 + Std.int(dy/2 + dy * j - NBack.rect_size/2); 
                NBack.grid.push([x, y]);
            }
        }
    }

}


class Rect extends Shape {
    static var c:UInt = 0x0000ff;
    public var cfill:UInt;

    public function new(?color:UInt) {
        if(color != null){ this.cfill = color; } else { this.cfill = 0x0000ff; }
        super()/*duper*/;
        draw(0x000000);
    }
    public function draw(color:UInt){
        var g = this.graphics;    
        g.clear();
        g.lineStyle(3, color);
        g.beginFill(this.cfill);
        g.drawRect(0, 0, NBack.rect_size, NBack.rect_size);
        g.endFill();
    }

}
