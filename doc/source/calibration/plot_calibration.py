import matplotlib.pyplot as plt 
import numpy as  np 
import scipy.optimize as opt

def lin(x,k,n):
    return x * k + n

WEIGHT = 0.682/1000 #kilograms
T1 = 0
T2 = 120
G = 9.81
a = np.loadtxt('calibration.txt')
x = a[0::2,2]
y = -a[0::2,3]+a[1::2,3]
p,cov = opt.curve_fit(lin,x,y)

c1 = 1./lin(T1,*p)*WEIGHT*G
c2 = 1./lin(T2,*p)*WEIGHT*G

#print 'CGAI: %f,  CT1 = %f, CTG1 = 0, CT2 = %f, CTG2 = %f' % (c1, T1, T2, (c2/c1-1)*1000000)
plt.plot(x,y,'o')
plt.plot([T1,T2],lin(np.array([T1,T2]),*p),'k-', linewidth = 2)
plt.xlabel('T [C]')
plt.ylabel('strain delta')
plt.title('Calibration curve (%s g weight)' % WEIGHT)
plt.show()


