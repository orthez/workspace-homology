import random as rnd
from math import cos,sin,tan,pi,asin,acos,atan2
import pickle
import numpy as np
from src.robotspecifications import *

from pylab import *
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

d0=ROBOT_DIST_KNEE_FOOT
d1=ROBOT_DIST_HIP_KNEE
d2=ROBOT_DIST_WAIST_HIP 
d3=ROBOT_DIST_NECK_WAIST
d4=ROBOT_DIST_HEAD_NECK

q = np.array((0.0,0.0,0.0,0.0,0.0))
## real limits from the hardware
#qL = np.array((-1.31,-0.03,-2.18,-0.09,-0.52))
#qU = np.array((0.73,2.62,0.73,1.05,0.79))
## artificial limits imposed by tangens (-pi/2,pi/2)
tlimit = pi/3
qaL = np.array((-tlimit,-tlimit,-tlimit,-tlimit,-tlimit))
qaU = np.array((tlimit,tlimit,tlimit,tlimit,tlimit))

###############################################################################
## X \in \R^Npts, the space of points, each constraint to one environment (E) box
Npts = 40

## L is the height of the head, which we fix here to investigate the factors
## which define the surface which induces the same linear subspace in X
## Let h1 be the height of the hip
Xarray = []


##iterate over homotopy classes (HC)
for k in range(0,4):
        asign = 1
        bsign = 1
        if k==0:
                asign=1
                bsign=1
        if k==1:
                asign=1
                bsign=-1
        if k==2:
                asign=-1
                bsign=-1
        if k==3:
                asign=-1
                bsign=1

        L = 1.4
        h1 = 0.0
        hmin=1000
        hmax=0

        while h1 <= d0+d1:
                h1 = h1+0.005
                ###############################################################################
                ## Find the max and min h1, such that there is still at least one valid
                ## configuration inside X

                ## upper bounds: h1 <= d0+d1
                ###############################################################################

                ## given h1, compute the 
                ## a : distance from knee to the main axis through foot, hip and waist.
                ## b : distance from neck to the main axis through foot, hip and waist.

                ## http://mathworld.wolfram.com/Circle-CircleIntersection.html
                h2 = L - h1 - d2
                a=asign*0.5*(1/h1)*sqrt(4*h1*h1*d0*d0-pow(h1*h1-d1*d1+d0*d0,2)) 
                b=bsign*0.5*(1/h2)*sqrt(4*h2*h2*d3*d3-pow(h2*h2-d4*d4+d3*d3,2)) 

                qh1 = np.array((0.0,0.0,0.0,0.0,0.0))
                if abs(-a/d0) > 1 or abs(a/d1) > 1:
                        print "fatal error: knee must be below foot, not allowed"
                        continue

                qh1[0] = asin(-a/d0)
                qh1[1] = asin(a/d1)
                qh1[2] = 0.0

                if abs(-b/d3) > 1 or abs(b/d4) > 1:
                        print "fatal error: knee must be below foot, not allowed"
                        continue

                qh1[3] = asin(-b/d3)
                qh1[4] = asin(b/d4)

                q = qh1
                ###############################################################################
                ## generate X and visualize
                ###############################################################################

                if not((q<=qaU).all() and (q>=qaL).all()):
                        #print "not in range of tan configuration"
                        continue
                if h1 < hmin:
                        hmin = h1
                if h1 >= hmax:
                        hmax = h1

                ## compute q -> x

                x = np.zeros((Npts,1))
                heights = np.zeros((Npts,1))
                heights[0]=0
                heights[1]=ROBOT_FOOT_HEIGHT

                for i in range(1,len(heights)):
                        heights[i] = VSTACK_DELTA+heights[i-1]

                knee_height = d0*cos(q[0])
                hip_height = knee_height+d1*cos(q[1])
                waist_height = hip_height+d2*cos(q[2])
                neck_height = waist_height+d3*cos(q[3])
                head_height = neck_height+d4*cos(q[4])

                xctr=1
                xd=0

                x[0]=0
                t0 = tan((q[0]))
                t1 = tan((q[1]))
                t2 = tan((q[2]))
                t3 = tan((q[3]))
                t4 = tan((q[4]))
                ###############################################################################
                ### foot-to-knee path
                ###############################################################################
                while heights[xctr] <= knee_height:
                        x[xctr] = heights[xctr]*t0
                        xctr=xctr+1

                ################################################################################
                #### knee-to-hip path
                ################################################################################
                offset = knee_height*t0
                kneepos = offset
                while heights[xctr] < hip_height:
                        x[xctr] = (heights[xctr]-knee_height)*t1+offset
                        xctr=xctr+1

                ################################################################################
                #### hip-to-waist path
                ################################################################################

                offset = knee_height*t0+(hip_height-knee_height)*t1
                hippos = offset

                while heights[xctr] < waist_height:
                        x[xctr] = (heights[xctr]-hip_height)*t2+offset
                        xctr=xctr+1

                ################################################################################
                #### waist-to-neck path
                ################################################################################
                offset = knee_height*t0\
                                +(hip_height-knee_height)*t1\
                                +(waist_height-hip_height)*t2

                waistpos = offset

                while heights[xctr] < neck_height:
                        x[xctr] = (heights[xctr]-waist_height)*t3+offset
                        xctr=xctr+1
                ################################################################################
                #### neck-to-head path
                ################################################################################
                offset = knee_height*t0\
                                +(hip_height-knee_height)*t1\
                                +(waist_height-hip_height)*t2\
                                +(neck_height-waist_height)*t3
                neckpos = offset


                while xctr<len(heights) and heights[xctr] < head_height:
                        x[xctr] = (heights[xctr]-neck_height)*t4+offset
                        xctr=xctr+1

                headpos = knee_height*t0\
                                +(hip_height-knee_height)*t1\
                                +(waist_height-hip_height)*t2\
                                +(neck_height-waist_height)*t3\
                                +(head_height-neck_height)*t4

                if abs(hippos) >= 0.005:
                        exit
                if abs(waistpos) >= 0.005:
                        exit

                Xarray.append(x)

                ### display x
                fig=figure(1)
                fig.clf()
                ax = fig.gca()


                plot([0,-a],[0,knee_height],'-b',linewidth=5.0)
                plot([-a,0],[knee_height,hip_height],'-b',linewidth=5.0)
                plot([0,0],[hip_height,waist_height],'-b',linewidth=5.0)
                plot([0,-b],[waist_height,neck_height],'-b',linewidth=5.0)
                plot([-b,headpos],[neck_height,head_height],'-b',linewidth=5.0)
                print q[4]

                y=heights
                ax.scatter(x,y,marker='o',c='r')
                plot(x,y,'-r')
                lenlines=0.6
                plot([-lenlines,lenlines],[head_height,head_height],'-k',linewidth=3.0)
                plot([-lenlines,lenlines],[neck_height,neck_height],'-k',linewidth=2.0)
                plot([-lenlines,lenlines],[waist_height,waist_height],'-k',linewidth=2.0)
                plot([-lenlines,lenlines],[hip_height,hip_height],'-k',linewidth=2.0)
                plot([-lenlines,lenlines],[knee_height,knee_height],'-k',linewidth=2.0)

                for i in range(0,len(heights)):
                        plot([-lenlines,lenlines],[heights[i],heights[i]],'-b')
                plt.pause(0.1)

print "for h1 in",hmin,hmax
print "sampled",len(Xarray),"points"
Nsamples=len(Xarray)
###############################################################################
## PCA on xpoints, visualizing in 3d
###############################################################################
from matplotlib.mlab import PCA

## Xarray to MxN numpy array
xx = np.zeros((Npts,len(Xarray)))
for i in range(0,len(Xarray)):
        for j in range(0,Npts):
                xx[j,i] = Xarray[i][j]

for i in range(0,Npts):
        xd = 0
        for j in range(0,len(Xarray)):
                xd = xd+xx[i,j]
        xd = xd/Npts
        for j in range(0,len(Xarray)):
                xx[i,j]=xx[i,j]-xd

[U,S,V]=np.linalg.svd(xx)
print np.around(S,2)
uu = np.around(U,2)


##take the first three orthonormal bases
X1 = uu[:,0]
X2 = uu[:,1]
X3 = uu[:,2]

Xproj = np.zeros((3,Nsamples))
for i in range(0,Nsamples):
        x = np.dot(X1.T,xx[:,i])
        y = np.dot(X2.T,xx[:,i])
        z = np.dot(X3.T,xx[:,i])
        Xproj[0,i] = x
        Xproj[1,i] = y
        Xproj[2,i] = z

X = Xproj[0,:]
Y = Xproj[1,:]
Z = Xproj[2,:]

pickle.dump( S, open( "data/cspaceEigenvalues.dat", "wb" ) )
pickle.dump( X, open( "data/cspaceX.dat", "wb" ) )
pickle.dump( Y, open( "data/cspaceY.dat", "wb" ) )
pickle.dump( Z, open( "data/cspaceZ.dat", "wb" ) )

print "wrote data to data/cspace*"