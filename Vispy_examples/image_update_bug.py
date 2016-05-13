#inspired by: 
#http://vispy.org/examples/basics/scene/image.html
from vispy import scene
from vispy import app
import numpy as np
import time
import sys

class canvasObj(app.Canvas):
    def __init__(self, parent=None):
        #print "Initializing myCanvas object"
        # Create a canvas
        canvas = scene.SceneCanvas(keys='interactive')
        #canvas = app.Canvas()
        canvas.size = 800, 600
        self.canvas=canvas
        
    def addView(self):
        # Set up a viewbox to display the image with interactive pan/zoom
        view = self.canvas.central_widget.add_view()
        self.view=view
        
    def addImage(self):
        # Create the image data
        #img_data = np.random.normal(size=(500, 500, 3), loc=128, scale=50).astype(np.ubyte)
        img_data = np.random.normal(size=(500, 500), loc=128, scale=50).astype(np.ubyte)
        image = scene.visuals.Image(img_data, parent=self.view.scene)
        self.image=image
        
    def makeData(self):
        img_data = np.random.normal(size=(500, 500), loc=128, scale=50).astype(np.ubyte)
        self.image.set_data(img_data)
        
    def showData(self):
        # Show the data
        image=self.image
        # Set the view bounds to show the entire image with some padding
        self.view.camera.rect = (-10, -10, image.size[0]+20, image.size[1]+20) 
        #show current results
        self.canvas.show()
        app.process_events()
        
    def closeCanvas(self):
        self.canvas.close()

if __name__ == '__main__' and sys.flags.interactive == 0:
    
    Nloops=200
    strt=time.time()
    #initialize canvas object
    myCanvas=canvasObj()  #create canvas
    myCanvas.addView()    #create view
    myCanvas.addImage()   #attach image to view
    for i in range(Nloops):
        # print "Loop: ",i+1," of ",Nloops
        #in the loop, just update and show new data
        myCanvas.makeData()      #create new random data for each loop pass
        myCanvas.showData()      #show the result
        
    stp=time.time()
    # print "Elapsed time: ",stp-strt," Seconds"

    app.run()