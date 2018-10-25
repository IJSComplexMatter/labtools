from labtools.analysis.image.selection import ImageInspections
from labtools.analysis.tools import Filenames
from labtools.analysis.fit import DataFitter, FitFunction, create_fit_data

import numpy, cv
from matplotlib import pyplot as plt

def find_edge(im, rectangle, fitter , direction = 0):
    y = im.sum(direction)
    y = y*1.0/y.max()
    shift = rectangle.width, rectangle.height
    x = numpy.arange(rectangle.top_left[direction],rectangle.top_left[direction]+shift[direction])
    fitter.data.x, fitter.data.y = x, y
    #fitter.configure_traits()    
    fitter.fit()
    rectangle.center[direction] = fitter.function.get_parameters('dict')['x0'][0]
    
def get_length(filenames, selections_name = 'selections.txt', select = True):
    """Fits length
    """
    selections = ImageInspections(filenames = filenames)
    try:
        selections.analysis.from_file(selections_name)
    except:
        pass
    if select:
        if selections.configure_traits():
            selections.analysis.to_file(selections_name)    
        
    fit_f = (FitFunction(name = 'elastomer.gauss1'),
             FitFunction(name = 'elastomer.gauss1'),
             FitFunction(name = 'elastomer.gauss1'))
             
    fitters = [DataFitter(function = fit) for fit in fit_f]
             
    centers = tuple([rect.center.copy() for rect in selections.analysis.selections])
    vshift = 0
    hshift = 0

    fit_f[0].set_parameters(s = 2, a=1 ,x0 = centers[0][0])    
    fit_f[1].set_parameters(s = 2, a=-1, x0 = centers[1][0])     
    fit_f[2].set_parameters(s = 2, a=1, x0 = centers[2][1]) 
    
    
 
    length = []    
    
    cv.NamedWindow('Image') 
    
    for index, fname in enumerate(filenames):
        print('%d of %d' % (index, len(filenames)))
        mat = cv.LoadImageM(fname)
        #mattmp = cv.CreateMat(mat.rows,mat.cols,cv.CV_16SC3)
        #cv.Laplace(mat,mattmp,7)  
        #a = numpy.asarray(mattmp)
        print('%s loaded' % fname)

        for i in range(2):
            rectangle =selections.analysis.selections[i]
            fit = fit_f[i]
            rectangle.center[1] =  centers[i][1] + vshift
            fit.set_parameters(x0 = rectangle.center[0])
            #ims = (rectangle.slice_image(a))[:,:,0]
            matsl = cv.GetSubRect(mat, rectangle.box) 
            mattmp = cv.CreateMat(matsl.rows,matsl.cols,cv.CV_16SC3)
            cv.Laplace(matsl,mattmp,7) 
            ims = numpy.asarray(mattmp)[:,:,0]
            
            find_edge(ims, rectangle, fitters[i], direction = 0)
            
        rect0 = selections.analysis.selections[0]
        rect1 = selections.analysis.selections[1]
        hshift = (( -centers[0][0] + rect0.center[0])  + ( -centers[1][0] + rect1.center[0]))/2 
        
        for i in range(1):
            rectangle =selections.analysis.selections[2+i]
            fit = fit_f[2+i]
            rectangle.center[0] = centers[2][0] + hshift
            fit.set_parameters(x0 = rectangle.center[1])
            #ims = (rectangle.slice_image(a))[:,:,0]
            matsl = cv.GetSubRect(mat, rectangle.box) 
            mattmp = cv.CreateMat(matsl.rows,matsl.cols,cv.CV_16SC3)
            cv.Laplace(matsl,mattmp,7) 
            ims = numpy.asarray(mattmp)[:,:,0]
            find_edge(ims, rectangle, fitters[2+i], direction = 1)
        
        rect2 = selections.analysis.selections[2] 
        vshift = ( -centers[2][1] + rect2.center[1])  
        print('fits done')
        
        cv.Circle(mat, tuple(rect0.center),5,(2**15,0,2**15))
        cv.Circle(mat, tuple(rect1.center),5,(2**15,0,2**15))
        cv.Circle(mat, tuple(rect2.center),5,(2**15,0,2**15))
        cv.ShowImage('Image',mat)
        c = cv.WaitKey(10) #exit on escape key
        if c == 27:
            break       
        w = rect1.center[0]- rect0.center[0]

        length.append(w)
    cv.DestroyWindow('Image')  
    return length

 