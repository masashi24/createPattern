
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import glob
from natsort import natsorted
import threading
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.animation as animation

class SmallPattern(threading.Thread):

    #def __init__(self, size=16):
    def run(self):
        cm_candidates = ["twilight", "viridis", "plasma", "inferno", "magma"]
        _cm = cm_candidates[1]
        self.cm = plt.get_cmap(_cm)

        self.size = 11 # should be Kisuu
        center = int((self.size - 1)/2)
        self.fig=plt.figure()
        self.ax=self.fig.add_subplot(111)
        self.myCanvas = np.zeros((self.size, self.size)) #need tuple for np.zeros
        self.myCanvas[center, center] = 240
        #self.ax.imshow(self.myCanvas)
        self.ax.pcolor(self.myCanvas, edgecolors='k', linewidths=4, cmap=self.cm)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        plt.show()

    def onclick(self, event):
        print ('event.button=%d,  event.x=%d, event.y=%d, event.xdata=%f,event.ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata))
        for i in range(self.size):
            #if(i - 0.5 < event.ydata < i + 0.5):
            if(i < event.ydata < i+1):
                _inteventX = i
            #if(i - 0.5 < event.xdata < i + 0.5):
            if(i < event.xdata < i+1):
                _inteventY = i
        if (self.myCanvas[_inteventX, _inteventY] >= 100):
            self.myCanvas[_inteventX, _inteventY] = 0
            print ('X=%d,  Y=%d, changed to 0'%(_inteventX, _inteventY))
        else:
            self.myCanvas[_inteventX, _inteventY] = 100
            print ('X=%d,  Y=%d, changed to 100'%(_inteventX, _inteventY))
        self.ax.pcolor(self.myCanvas, edgecolors='k', linewidths=4, cmap=self.cm)
        #self.ax.imshow(self.myCanvas)
        plt.draw()

class MyPattern():

    def __init__(self):
        self.ani = None
        self.ims = []
        self.sizeX = 64
        self.sizeY = 64
        self.magnification = 10
        self.loopNum = 1
        self.smallpattern = None

        # settings for matplotlib
        #plt.gray()
        cm_candidates = ["twilight", "viridis", "plasma", "inferno", "magma"]
        _cm = cm_candidates[0]
        self.cm = plt.get_cmap(_cm)

        # prepare UI parts
        self.root = tkinter.Tk()
        self.root.wm_title("Embedding in Tk anim")
        self.fig = Figure(figsize = (10,10))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.graph = self.fig.add_subplot(111)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.canvas.get_tk_widget().pack()

        self.currentPattern = self.createInitPattern()
        im = self.graph.imshow(self.currentPattern, cmap=self.cm, animated=True)
        self.ims.append([im])

        # run UI func
        self.UI()

    def createPattern(self):
        pattern = self.currentPattern
        self.currentPattern[int(self.sizeX/2),int(self.sizeY/2)] += 121
        '''
        for i in range(3):
            self.currentPattern[32*(i+1), 32] += 200
            self.currentPattern[32*(i+1), 32*2] += 200
            self.currentPattern[32*(i+1), 32*3] += 200
        '''
        self.sunayamaModel()
        self.currentPattern = pattern
        #a = np.full((128,128),100)
        return pattern

    def createInitPattern(self):
        pattern = np.zeros((self.sizeX,self.sizeY))
        #pattern = np.full((128,128),100)
        #pattern = np.random.randint(0, 200, (128,128))
        print("initialPattern = ", pattern)
        return pattern

    def saveImage(self, pattern):
        savedImgList_color = glob.glob('colorMap_*')
        saveFileNameGray = None
        saveFileNameColorMap = None
        if(len(savedImgList_color) != 0):
            savedImgList_color = natsorted(savedImgList_color)
            latestColorImg = savedImgList_color[-1]
            latestColorImgNo = latestColorImg.split("_")[1].split(".")[0]
            nextFileNo = int(latestColorImgNo)+1
            saveFileNameGray = "gray_"+str(nextFileNo)+".png"
            saveFileNameColorMap = "colorMap_"+str(nextFileNo)+".png"
        else:
            saveFileNameGray = "gray_0.png"
            saveFileNameColorMap = "colorMap_0.png"
        resizedPattern  = np.array(Image.fromarray(pattern).resize((self.sizeX * self.magnification, self.sizeY * self.magnification), Image.NEAREST))
        
        # saving gray scale image
        pilImg = Image.fromarray(np.uint8(resizedPattern))
        #pilImg = Image.fromarray(pattern)
        #enhancer = ImageEnhance.Sharpness(pilImg)
        #enhancer.enhance(100.0).save('hoge.png')
        #pilImg.show()
        pilImg.save(saveFileNameGray)
        print("latest gray image is saved ! file name = ", saveFileNameGray)

        # saving Matplot Lib color map image
        def minmax(arr):
            arr = (arr - arr.min()) / (arr.max() - arr.min())
            return arr
        cmap = plt.get_cmap(self.cm)
        colorPattern = minmax(resizedPattern)
        img = cmap(colorPattern, bytes=True)
        img = Image.fromarray(img)
        #img = img.resize([220,220], resample=PIL.Image.NEAREST)
        img.save(saveFileNameColorMap)
        print("latest color map image is saved ! file name = ", saveFileNameColorMap)

    def sunayamaModel(self):
        _minRow = 0
        _minCol = 0
        _maxRow = self.sizeX - 1
        _maxCol = self.sizeY - 1
        _pattern = 99 # 99 : use createdPattern
        if(self.smallpattern == None):
            _pattern = 1
        _stepSize = 30
        savedPattern = copy.copy(self.currentPattern)
        pattern = self.currentPattern
        # get index of "value > thresh"
        indexList = np.where(pattern > 200)
        #print("indexList = ",indexList)
        for i in range(len(indexList[0])):
            row = indexList[0][i]
            col = indexList[1][i]
            #print("row, col = ", row, "/", col)
            pattern[row,col] = pattern[row, col] - savedPattern[row, col]

            if(_pattern == 1):
                # pattern1 simple SunaYama
                '''
                  01
                02  03
                  04  
                '''
                if(row > _minRow):
                    pattern[row-1, col] += _stepSize # 01
                if(row < _maxRow):
                    pattern[row+1, col] += _stepSize # 04
                if(col > _minCol):
                    pattern[row, col-1] += _stepSize # 02
                if(col < _maxCol):
                    pattern[row, col+1] += _stepSize # 03

            elif(_pattern == 2):
                # pattern2 
                '''
                            18
                            14
                            09 
                            05
                            01lif
              19 15 10 06 02  03 07 11 16 20
                            04      
                            08      
                            12
                            17
                            21
                '''
                if(row > _minRow):
                    pattern[row-1, col] += _stepSize / 5 # 01
                if(row > _minRow + 1):
                    pattern[row-2, col] += _stepSize / 4 # 05
                if(row > _minRow + 2):
                    pattern[row-3, col] += _stepSize / 3 # 09
                if(row > _minRow + 3):
                    pattern[row-4, col] += _stepSize / 2 # 14
                if(row > _minRow + 4):
                    pattern[row-5, col] += _stepSize / 1 # 18

                if(row < _maxRow):
                    pattern[row+1, col] += _stepSize / 5 # 04
                if(row < _maxRow - 1):
                    pattern[row+2, col] += _stepSize / 4 # 08
                if(row < _maxRow - 2):
                    pattern[row+3, col] += _stepSize / 3 # 12
                if(row < _maxRow - 3):
                    pattern[row+4, col] += _stepSize / 2 # 17
                if(row < _maxRow - 4):
                    pattern[row+5, col] += _stepSize / 1 # 21

                if(col > _minCol):
                    pattern[row, col-1] += _stepSize / 5 # 02
                if(col > _minCol+1):
                    pattern[row, col-2] += _stepSize / 4 # 06
                if(col > _minCol+2):
                    pattern[row, col-3] += _stepSize / 3 # 10
                if(col > _minCol+3):
                    pattern[row, col-4] += _stepSize / 2 # 15
                if(col > _minCol+4):
                    pattern[row, col-5] += _stepSize / 1 # 19

                if(col < _maxCol):
                    pattern[row, col+1] += _stepSize / 5 # 03
                if(col < _maxCol-1):
                    pattern[row, col+2] += _stepSize / 4 # 07
                if(col < _maxCol-2):
                    pattern[row, col+3] += _stepSize / 3 # 11
                if(col < _maxCol-3):
                    pattern[row, col+4] += _stepSize / 2 # 16
                if(col < _maxCol-4):
                    pattern[row, col+5] += _stepSize / 1 # 20
        
            elif(_pattern == 3):
                # pattern2 
                '''
                        09 13 17
                18      05
                14      01
                10 06 02  03 07 11
                        04      15
                        08      19
                  20 16 12
                '''
                if(row > _minRow):
                    pattern[row-1, col] += _stepSize / 5 # 01
                    if(col > _minCol + 2):
                        pattern[row-1, col-3] += _stepSize / 2 # 14
                if(row > _minRow + 1):
                    pattern[row-2, col] += _stepSize / 4 # 05
                    if(col > _minCol + 2):
                        pattern[row-2, col-3] += _stepSize / 1 # 18
                if(row > _minRow + 2):
                    pattern[row-3, col] += _stepSize / 3 # 09
                    if(col < _maxCol):
                        pattern[row-3, col+1] += _stepSize / 2 # 13
                    if(col < _maxCol - 1):
                        pattern[row-3, col+2] += _stepSize / 1# 17

                if(row < _maxRow):
                    pattern[row+1, col] += _stepSize / 5 # 04
                    if(col < _maxCol - 2):
                        pattern[row+1, col+3] += _stepSize / 2 # 15
                if(row < _maxRow - 1):
                    pattern[row+2, col] += _stepSize / 4 # 08
                    if(col < _maxCol - 2):
                        pattern[row+2, col+3] += _stepSize / 1 # 19
                if(row < _maxRow - 2):
                    pattern[row+3, col] += _stepSize / 3 # 12
                    if(col > _minCol):
                        pattern[row+3, col-1] += _stepSize / 2 # 16
                    if(col > _minCol + 1):
                        pattern[row+3, col-2] += _stepSize / 1 # 20

                if(col > _minCol):
                    pattern[row, col-1] += _stepSize / 5 # 02
                if(col > _minCol+1):
                    pattern[row, col-2] += _stepSize / 4 # 06
                if(col > _minCol+2):
                    pattern[row, col-3] += _stepSize / 3 # 10

                if(col < _maxCol):
                    pattern[row, col+1] += _stepSize / 5# 03
                if(col < _maxCol-1):
                    pattern[row, col+2] += _stepSize / 4 # 07
                if(col < _maxCol-2):
                    pattern[row, col+3] += _stepSize / 3 # 11

            elif(_pattern == 99):
                requestedPattern = self.smallpattern.myCanvas
                _size = self.smallpattern.size
                _shiftNum = (_size - 1) / 2 # _size should be Kisuu 
                _patternIndexList = np.where(requestedPattern > 90)
                _patternIndexListX = _patternIndexList[0]
                _patternIndexListY = _patternIndexList[1]
                _soutaiIndexListX = _patternIndexListX - int(_shiftNum)
                _soutaiIndexListY = _patternIndexListY - int(_shiftNum)

                for i in range(len(_soutaiIndexListX)):
                    if(row < _maxRow - _shiftNum and row > _minRow + _shiftNum and col < _maxCol - _shiftNum and col > _minRow + _shiftNum):
                        pattern[row + _soutaiIndexListX[i], col + _soutaiIndexListY[i]] += _stepSize

        self.currentPattern = pattern

    def UI(self):

        # fucntions for UI
        def _quit():
            self.root.quit()     # stops mainloop
            self.root.destroy()  # this is necessary on Windows to prevent
                                 # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        # pause matplotlib anime
        def _pauseAnime():
            if(self.ani != None):
                self.ani.event_source.stop()
            return

        # resume matplotlib anime
        def _resumeAnime():
            if(self.ani != None):
                self.ani.event_source.start()
            return 
            
        # play animation
        def _playAnime():
            if(self.ani == None):
                print("anime start!")
                #l = np.arange(0, 8, 0.01)  #
                #self.ani = animation.FuncAnimation(self.fig, self.ims, l, interval=100, blit=True)
                self.ani = animation.ArtistAnimation(self.fig, self.ims, interval=10, blit=True)

        def _stepToward():
            _loopNum = self.loopNum
            for i in range(_loopNum):
                im = self.graph.imshow(self.createPattern(), cmap=self.cm, animated=True)    
                self.ims.append([im])
                #save latest 60 images
                if(len(self.ims) > 300):
                    self.ims.pop(0)
                #print("image Num =", len(self.ims))

        def _gray():
            plt.gray()

        def _save():
            self.saveImage(self.currentPattern)

        def _createPattern():
            self.smallpattern = SmallPattern()
            self.smallpattern.run()

        # UI design
        pauseAnimeButton = tkinter.Button(master=self.toolbar, text="Pause", command=_pauseAnime)
        pauseAnimeButton.pack(side='left')

        resumeAnimeButton = tkinter.Button(master=self.toolbar, text="Resume", command=_resumeAnime)
        resumeAnimeButton.pack(side='left')

        button = tkinter.Button(master=self.toolbar, text="Play", command=_playAnime) 
        button.pack(side='left')

        button = tkinter.Button(master=self.toolbar, text="Step", command=_stepToward) 
        button.pack(side='left')

        resumeAnimeButton = tkinter.Button(master=self.toolbar, text="Gray", command=_gray)
        resumeAnimeButton.pack(side='left')

        button = tkinter.Button(master=self.toolbar, text="Save", command=_save) 
        button.pack(side='left')

        button = tkinter.Button(master=self.toolbar, text="Create", command=_createPattern) 
        button.pack(side='left')

        button = tkinter.Button(master=self.toolbar, text="Quit", command=_quit) 
        button.pack(side='left')

        self.root.mainloop()
        
def main():
    _mypattern = MyPattern()

if __name__ == "__main__":
    main()

