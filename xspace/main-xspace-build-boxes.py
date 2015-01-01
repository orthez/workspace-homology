import random as rnd
from math import cos,sin,tan,pi,asin,acos,atan2,atan
import pickle
import numpy as np
from src.robotspecifications import *

from pylab import *
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import os

def memory_usage_psutil():
    # return the memory usage in MB
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.get_memory_info()[0] / float(2 ** 20)
    return mem

dankle=ROBOT_DIST_FOOT_SOLE
d0=ROBOT_DIST_KNEE_FOOT
d1=ROBOT_DIST_HIP_KNEE
d2=ROBOT_DIST_WAIST_HIP 
d3=ROBOT_DIST_NECK_WAIST
d4=ROBOT_DIST_HEAD_NECK

## real limits from the hardware
#qL = np.array((-1.31,-0.03,-2.18,-0.09,-0.52))
#qU = np.array((0.73,2.62,0.73,1.05,0.79))
## artificial limits imposed by tangens (-pi/2,pi/2)
tlimit = pi/3
qaL = np.array((-tlimit,-tlimit,-tlimit,-tlimit,-tlimit))
qaU = np.array((tlimit,tlimit,tlimit,tlimit,tlimit))

###############################################################################
## X \in \R^Npts, the space of points, 
## each constraint to one environment (E) box
###############################################################################
Npts = 40

## h3 is the height of the head, which we fix here to investigate the factors
## which define the surface which induces the same linear subspace in X
## Let h1 be the height of the hip

static = 0
q = np.array((0.0,0.0,0.0,0.0,0.0))
minH1 = 100000
maxH1 = 0
minH2 = 100000
maxH2 = 0
minH3 = 100000
maxH3 = 0

h1low = 0.305
h1high = 0.620
h2low = -0.425
h2high = 0.435
h3low = 0.950
h3high = 1.520

h1step = 0.005
h2step = 0.005
h3step = 0.005

h3=h3low
NCtr = 0
NfeasibleCtr = 0
Xarray = []
while h3 < h3high:
        h3 = h3+h3step

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

                h2 = h2low
                while h2<=h2high:
                        h2=h2+h2step
                        h1 = h1low
                        while h1 <= h1high:
                                NCtr = NCtr+1
                                h1 = h1+h1step
                                ###############################################################################
                                ## Find the max and min h1, such that there is still at least one valid
                                ## configuration inside X

                                ## upper bounds: h1 <= d0+d1
                                ###############################################################################

                                ## given h1, compute the 
                                ## a : distance from knee to the main axis through foot, hip and waist.
                                ## b : distance from neck to the main axis through foot, hip and waist.

                                ## http://mathworld.wolfram.com/Circle-CircleIntersection.html
                                t2 = h3 - h1 - d2
                                d5 = sqrt(h2*h2+t2*t2)

                                sqrtA = 4*h1*h1*d0*d0-pow(h1*h1-d1*d1+d0*d0,2)
                                sqrtB = 4*d5*d5*d3*d3-pow(d5*d5-d4*d4+d3*d3,2)
                                if sqrtA < 0:
                                        continue
                                if sqrtB < 0:
                                        continue
                                a=asign*0.5*(1/h1)*sqrt(sqrtA) 
                                b=bsign*0.5*(1/d5)*sqrt(sqrtB) 

                                if math.isnan(b):
                                        #print "triangle inequality d3+d4 > d5 is not fulfilled"
                                        #print d3,d4,d5
                                        continue
                                if math.isnan(a):
                                        #print "triangle inequality d0+d1 > dist(foot,hip) is not fulfilled"
                                        #print d0,d1
                                        continue

                                qh1 = np.array((0.0,0.0,0.0,0.0,0.0))
                                if abs(-a/d0) > 1 or abs(a/d1) > 1:
                                        print "fatal error: knee must be below foot, not allowed"
                                        continue

                                qh1[0] = asin(-a/d0)
                                qh1[1] = asin(a/d1)
                                qh1[2] = 0.0

                                qh1[3] = asin(h2/d5)+asin(b/d3)
                                v = np.array((h2-d3*sin(qh1[3]),t2-d3*cos(qh1[3])))
                                zaxis = np.array((0,1))
                                vn = v/np.linalg.norm(v)

                                qh1[4]=acos(np.dot(zaxis,vn))*vn[0]/abs(vn[0])

                                q = qh1
                                ###############################################################################
                                ## generate X and visualize
                                ###############################################################################

                                if not((q<=qaU).all() and (q>=qaL).all()):
                                        #print "not in range of tan configuration",q
                                        continue

                                ## compute q -> x

                                x = np.zeros((Npts,1))
                                heights = np.zeros((Npts,1))
                                heights[0]=0
                                #heights[1]=ROBOT_FOOT_HEIGHT

                                for i in range(1,len(heights)):
                                        heights[i] = VSTACK_DELTA+heights[i-1]

                                knee_height = d0*cos(q[0])+dankle
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
                                while heights[xctr] <= dankle:
                                        x[xctr] = x[0]
                                        xctr=xctr+1

                                while heights[xctr] <= knee_height:
                                        x[xctr] = (heights[xctr]-dankle)*t0
                                        xctr=xctr+1

                                ################################################################################
                                #### knee-to-hip path
                                ################################################################################
                                offset = (knee_height-dankle)*t0
                                kneepos = offset
                                while heights[xctr] < hip_height:
                                        x[xctr] = (heights[xctr]-knee_height)*t1+offset
                                        xctr=xctr+1

                                ################################################################################
                                #### hip-to-waist path
                                ################################################################################

                                offset = (knee_height-dankle)*t0+(hip_height-knee_height)*t1
                                hippos = offset

                                while heights[xctr] < waist_height:
                                        x[xctr] = (heights[xctr]-hip_height)*t2+offset
                                        xctr=xctr+1

                                ################################################################################
                                #### waist-to-neck path
                                ################################################################################
                                offset = (knee_height-dankle)*t0\
                                                +(hip_height-knee_height)*t1\
                                                +(waist_height-hip_height)*t2

                                waistpos = offset

                                while heights[xctr] < neck_height:
                                        x[xctr] = (heights[xctr]-waist_height)*t3+offset
                                        xctr=xctr+1
                                ################################################################################
                                #### neck-to-head path
                                ################################################################################
                                offset = (knee_height-dankle)*t0\
                                                +(hip_height-knee_height)*t1\
                                                +(waist_height-hip_height)*t2\
                                                +(neck_height-waist_height)*t3
                                neckpos = offset


                                while xctr<len(heights) and heights[xctr] < head_height:
                                        x[xctr] = (heights[xctr]-neck_height)*t4+offset
                                        xctr=xctr+1

                                headpos = (knee_height-dankle)*t0\
                                                +(hip_height-knee_height)*t1\
                                                +(waist_height-hip_height)*t2\
                                                +(neck_height-waist_height)*t3\
                                                +(head_height-neck_height)*t4

                                if h2 >= maxH2:
                                        maxH2 = h2
                                if h2 <= minH2:
                                        minH2 = h2
                                if h1 >= maxH1:
                                        maxH1 = h1
                                if h1 <= minH1:
                                        minH1 = h1
                                Xarray.append(x)
                                NfeasibleCtr=NfeasibleCtr+1

                                #### display x
                                #fig=figure(1)
                                #fig.clf()
                                #ax = fig.gca()

                                #plot([0,0],[0,dankle],'-b',linewidth=5.0)
                                #plot([0,-a],[dankle,knee_height],'-b',linewidth=5.0)
                                #plot([-a,0],[knee_height,hip_height],'-b',linewidth=5.0)
                                #plot([0,0],[hip_height,waist_height],'-b',linewidth=5.0)
                                #plot([0,sin(q[3])*d3],[waist_height,neck_height],'-b',linewidth=5.0)
                                #plot([sin(q[3])*d3,headpos],[neck_height,head_height],'-b',linewidth=5.0)

                                #y=heights
                                #ax.scatter(x,y,marker='o',c='r')
                                #plot(x,y,'-r')
                                #lenlines=0.6
                                #plot([-lenlines,lenlines],[head_height,head_height],'-k',linewidth=3.0)
                                #plot([-lenlines,lenlines],[neck_height,neck_height],'-k',linewidth=2.0)
                                #plot([-lenlines,lenlines],[waist_height,waist_height],'-k',linewidth=2.0)
                                #plot([-lenlines,lenlines],[hip_height,hip_height],'-k',linewidth=2.0)
                                #plot([-lenlines,lenlines],[knee_height,knee_height],'-k',linewidth=2.0)

                                #plt.gca().set_aspect('equal', adjustable='box')
                                #for i in range(0,len(heights)):
                                #        plot([-lenlines,lenlines],[heights[i],heights[i]],'-b')
                                #plt.pause(0.1)

        #print "for h1 in",hmin,hmax
        Nsamples=len(Xarray)
        print "h3=",h3," and points=",len(Xarray)," (memory usage:",memory_usage_psutil(),")"

Xname = "data/xspacemanifold-same-axes/xsamples.dat"
pickle.dump( Xarray, open( Xname, "wb" ) )

print "======================================================================="
print "Samples:"
print "  N   = "+str(NCtr)
print "  N_f = "+str(NfeasibleCtr)
#print "  N_m = "+str(Nmerged)
print "======================================================================="
print "interval of H values"
print "h1=\["+str(minH1)+","+str(maxH1)+"\]"
print "h2=\["+str(minH2)+","+str(maxH2)+"\]"
print "h3=\["+str(minH3)+","+str(maxH3)+"\]"
print "======================================================================="
