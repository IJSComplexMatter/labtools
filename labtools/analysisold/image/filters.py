from enthought.traits.api import HasTraits,  Range, Bool, Property, Str, Dict
import scipy.ndimage as nd

class BaseFilter(HasTraits):
    kw = Dict({}, desc = 'additional keyword arguments to nd filter')
    name_ = Property(Str)
    def process(self, image):
        return image            
    def _get_name_(self):
        return self.__class__.__name__

class RotateFilter(BaseFilter):
    """Image rotation filter
    
    >>> import scipy
    >>> a = scipy.lena()
    >>> r = RotateFilter()
    >>> r.name == 'Rotate'
    True
    >>> r.angle = 4.
    >>> b = r.process(a) #rotate by 4 degrees
    """
    angle = Range(-180,180.,0.)
    
    def process(self, image):
        if self.angle != 0.:
            image = nd.rotate(image, angle = self.angle, **self.kw)
        return image

Rotate = RotateFilter        
                        
class GaussianFilter(BaseFilter):
    sigma = Range(0.,100, 0.)
    
    def process(self, image):
        if self.sigma != 0.:
            print('processing gaussian')
            image = nd.gaussian_filter(image, self.sigma, **self.kw)
        return image
        
#class Contrast(BaseFilter):
#    sigma = Range(0.,100, 0.)
#    
#    def process(self, image):
#        if self.sigma != 0.:
#            print 'processing gaussian'
#            image = nd.gaussian_filter(image, self.sigma, **self.kw)
#        return image        

if __name__ == '__main__':
    import doctest
    doctest.testmod()

