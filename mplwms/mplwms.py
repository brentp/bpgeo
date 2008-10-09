import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class Tile(Figure):
    """
    convienence wrapper for drawing a tile. 

    >>> t = Tile(dpi=256, bbox=[-180,-90,180,90])
    >>> t.plot([1,2,3],[2,5,2]) #doctest: +ELLIPSIS
    [<matplotlib.lines.Line2D object ...]
    >>> t.plot([[1,2],[3,2],[5,2]]) #doctest: +ELLIPSIS
    [<matplotlib.lines.Line2D object ...]
    >>> t.save('t2.png')


    """
    def __init__(self, bbox=None, dpi=128, width=256, height=256, alpha=0, **kwargs):

        Figure.__init__(self, dpi=dpi, frameon=False, **kwargs)
        
        self.set_size_inches(width/dpi, height/dpi)

        self.patch.set_alpha(alpha)
        self.patch.set_linewidth(2.0)
        self.ax = self.add_axes((0,0,1,1), alpha=alpha, frameon=False, xticks=(), yticks=())
        self.ax.set_aspect(1.0)
        self.ax.set_autoscale_on(False)

        if isinstance(bbox, str):
            bbox = map(float, bbox.split(','))
        if not bbox is None:
            self.set_bbox(bbox)
    
        self.canvas = FigureCanvas(self)

    def set_bbox(self,bbox):
        self._bbox = bbox
        self.ax.set_xlim(bbox[0], bbox[2])
        self.ax.set_ylim(bbox[1], bbox[3])

    
    def plot(self, *args, **kwargs):
        return self.ax.plot(*args, **kwargs)

    def save(self, path):
        return self.canvas.print_figure(path, dpi=self.dpi)




if __name__ == "__main__":
    import doctest
    doctest.testmod()

