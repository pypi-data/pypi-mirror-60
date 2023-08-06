from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import functions as fn
import numpy as np
from cellpose import gui


class ImageDraw(pg.ImageItem):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`
    GraphicsObject displaying an image. Optimized for rapid update (ie video display).
    This item displays either a 2D numpy array (height, width) or
    a 3D array (height, width, RGBa). This array is optionally scaled (see
    :func:`setLevels <pyqtgraph.ImageItem.setLevels>`) and/or colored
    with a lookup table (see :func:`setLookupTable <pyqtgraph.ImageItem.setLookupTable>`)
    before being displayed.
    ImageItem is frequently used in conjunction with
    :class:`HistogramLUTItem <pyqtgraph.HistogramLUTItem>` or
    :class:`HistogramLUTWidget <pyqtgraph.HistogramLUTWidget>` to provide a GUI
    for controlling the levels and lookup table used to display the image.
    """

    sigImageChanged = QtCore.Signal()

    def __init__(self, image=None, viewbox=None, parent=None, **kargs):
        """
        See :func:`setImage <pyqtgraph.ImageItem.setImage>` for all allowed initialization arguments.
        """
        pg.GraphicsObject.__init__(self)
        self.menu = None
        self.image = None   ## original image data
        self.qimage = None  ## rendered image for display
        self.viewbox = viewbox
        self.paintMode = None

        self.setOpacity(0.35)
        self.levels = np.array([0,255])
        self.lut = None
        self.autoDownsample = False

        self.axisOrder = 'row-major'

        # In some cases, we use a modified lookup table to handle both rescaling
        # and LUT more efficiently
        self._effectiveLut = None

        self.border = None
        self.removable = False

        if image is not None:
            self.setImage(image, **kargs)
        else:
            self.setOpts(**kargs)

        kernel = 1*np.ones((3,3))
        #kernel[1,1] = 1
        self.setDrawKernel(kernel=kernel)
        onmask = 255.0 * kernel[:,:,np.newaxis]
        offmask = np.zeros((3,3,1))
        self.redmask = np.concatenate((onmask,offmask,offmask), axis=-1)
        self.greenmask = np.concatenate((offmask,onmask,offmask), axis=-1)
        self.parent = parent
        self.parent.current_stroke = []
        self.dragging = False
        self.clicked = False

    def mouseDragEvent(self, ev):
        if ev.modifiers() == QtCore.Qt.ShiftModifier or self.parent.drawon:
            #starting = self.viewbox.state['mouseEnabled'].copy()[0]  # starting segment
            self.viewbox.setMouseEnabled(x=False,y=False)
            if ev.button() == QtCore.Qt.LeftButton:
                if not self.dragging:
                    self.create_start(ev.pos())
                ev.accept()
                self.parent.stroke_appended = False
                self.dragging = True
                self.clicked = False
                #if self.is_at_start(ev.pos()):
                #    self.end_stroke()
                #else:
                self.drawAt(ev.pos(), ev)
            else:
                ev.ignore()
                return
        else:
            pos = ev.pos()
            lastPos = ev.lastPos()
            dif = pos - lastPos
            dif = dif * -1
            tr = dif
            x = tr.x()
            y = tr.y()
            self.viewbox._resetTarget()
            if x is not None or y is not None:
                self.viewbox.translateBy(x=x, y=y)

    def mouseClickEvent(self, ev):
        if ev.modifiers() == QtCore.Qt.ShiftModifier or self.parent.drawon:
            self.viewbox.setMouseEnabled(x=False,y=False)
            if self.viewbox is not None:
                self.viewbox.setMouseEnabled(x=False,y=False)
            if ev.button() == QtCore.Qt.LeftButton:
                if not self.clicked:
                    ev.accept()
                    if not self.dragging:
                        self.create_start(ev.pos())
                    self.parent.stroke_appended = False
                    self.dragging = True
                    self.clicked = True
                    self.drawAt(ev.pos(), ev)
                else:
                    ev.accept()
                    self.clicked = False
            elif ev.button() == QtCore.Qt.RightButton:
                ev.accept()
                self.remove_point(ev.pos(), ev)
                #self.parent.current_stroke = []
            else:
                ev.ignore()
                return
        else:
            if self.viewbox is not None:
                self.viewbox.setMouseEnabled(x=True,y=True)

    def remove_point(self, pos, ev):
        pos = [int(pos.y()), int(pos.x())]
        #self.parent.current_point_set = gui.get_unique_points(self.parent.current_point_set)
        set = self.parent.current_point_set
        if len(set) > 0:
            deleted = False
            for k,pp in enumerate(set):
                if pp[0]==self.parent.currentZ:
                    if pp[1]==pos[0] and pp[2]==pos[1]:
                        cZ, posy, posx = pp[0], pp[1], pp[2]
                        self.image[posy, posx, :] = 255
                        del set[k]
                        deleted=True
            if not deleted:
                pp = set[-1]
                if pp[0]==self.parent.currentZ:
                    cZ, posy, posx = pp[0], pp[1], pp[2]
                    self.image[posy, posx, :] = 255
                    del set[-1]
            self.updateImage()

    def hoverEvent(self, ev):
        if self.parent.shiftmodifier or self.parent.drawon:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        else:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

        if not ev.isExit() and self.drawKernel is not None and ev.acceptDrags(QtCore.Qt.LeftButton):
            ev.acceptClicks(QtCore.Qt.LeftButton)
            ev.acceptClicks(QtCore.Qt.RightButton)
            if not self.clicked:
                # not in stroke
                self.end_stroke()
            else:
                # continue stroke if not at start
                if self.is_at_start(ev.pos()):
                    self.end_stroke()
                    self.clicked = False
                else:
                    self.drawAt(ev.pos())
        elif not ev.isExit() and self.removable:
            ev.acceptClicks(QtCore.Qt.RightButton)  ## accept context menu clicks

    def create_start(self, pos):
        self.scatter = pg.ScatterPlotItem([pos.x()], [pos.y()], pxMode=False,
                                        color=(255,0,0), size=5, brush=None)
        self.parent.p0.addItem(self.scatter)

    def is_at_start(self, pos):
        # first check if you ever left the start
        if len(self.parent.current_stroke) > 3:
            stroke = np.array(self.parent.current_stroke)
            dist = (((stroke[1:,1:] - stroke[:1,1:][np.newaxis,:,:])**2).sum(axis=-1))**0.5
            dist = dist.flatten()
            #print(dist)
            has_left = (dist > 5).nonzero()[0]
            if len(has_left) > 0:
                first_left = np.sort(has_left)[0]
                has_returned = (dist[max(6,first_left+1):] < 3).sum()
                if has_returned > 0:
                    return True
                else:
                    return False
            else:
                return False

    def end_stroke(self):
        self.dragging = False
        if not self.parent.stroke_appended:
            self.parent.strokes.append(self.parent.current_stroke)
            self.parent.current_stroke = []
            self.parent.stroke_appended = True
            if self.parent.autosave:
                self.parent.add_set()
        if len(self.parent.current_point_set) > 0 and self.parent.autosave:
            self.parent.add_set()

    def tabletEvent(self, ev):
        pass
        #print(ev.device())
        #print(ev.pointerType())
        #print(ev.pressure())

    def drawAt(self, pos, ev=None):
        mask = self.greenmask
        set = self.parent.current_point_set
        stroke = self.parent.current_stroke
        pos = [int(pos.y()), int(pos.x())]
        dk = self.drawKernel
        kc = self.drawKernelCenter
        sx = [0,dk.shape[0]]
        sy = [0,dk.shape[1]]
        tx = [pos[0] - kc[0], pos[0] - kc[0]+ dk.shape[0]]
        ty = [pos[1] - kc[1], pos[1] - kc[1]+ dk.shape[1]]

        if tx[0]<0:
            sx[1] = dk.shape[0] + tx[0] - 1
            sx[0] = 0
            tx[0] = dk.shape[1] + tx[0] - 1
            tx[1] = 1
        if ty[0]<0:
            sy[1] = dk.shape[1] + tx[0] - 1
            sy[0] = 0
            ty[0] = 0
            ty[1] = dk.shape[1] + ty[0] - 1
        if tx[1] > self.parent.Ly-1:
            sx[0] = min(dk.shape[0]-2, tx[1]-self.parent.Ly-1)
            sx[1] = dk.shape[0]
            tx[0] = self.parent.Ly - (sx[1] - sx[0])
            tx[1] = self.parent.Ly
        if ty[1] > self.parent.Lx-1:
            sy[0] = min(dk.shape[1]-2, ty[1]-self.parent.Lx-1)
            sy[1] = dk.shape[1]
            ty[0] = self.parent.Lx - (sy[1] - sy[0])
            ty[1] = self.parent.Lx

        ts = (slice(tx[0],tx[1]), slice(ty[0],ty[1]))
        ss = (slice(sx[0],sx[1]), slice(sy[0],sy[1]))

        if tx[0] >= 0 and tx[0] < self.parent.Ly and ty[0] >= 0 and ty[0] < self.parent.Lx:
            self.image[ts] = mask[ss]
        set.append([self.parent.currentZ, tx[0]+kc[0], ty[0]+kc[1]])
        stroke.append([self.parent.currentZ, tx[0]+kc[0], ty[0]+kc[1]])
        self.updateImage()
        self.dragging=True

    def setDrawKernel(self, kernel=None, mask=None, mode='set'):
        self.drawKernel = kernel
        self.drawKernelCenter = [int(np.floor(kernel.shape[0]/2)),
                                 int(np.floor(kernel.shape[1]/2))]
        self.drawMode = mode
        self.drawMask = mask
