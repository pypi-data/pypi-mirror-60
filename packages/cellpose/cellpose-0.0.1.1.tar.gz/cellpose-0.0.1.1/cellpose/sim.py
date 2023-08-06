import numpy as np
import cv2
from mxnet import nd, gpu

def run_simulations(ishape, ncells=600, R=8):
    nimg, Lz, Ly, Lx = ishape

    xm, ym, zm = np.meshgrid(np.arange(Lx),  np.arange(Ly), np.arange(Lz))
    xd, yd,zd  = np.meshgrid(np.arange(-R,R+1),  np.arange(-R,R+1), np.arange(-R,R+1))
    rd = (xd**2 + yd**2 + zd**2)**.5

    lbl = np.zeros((nimg,3,Lz, Ly,Lx), 'float32')
    img = np.zeros((nimg,1,Lz, Ly,Lx), 'float32')

    xs  = np.arange(21)
    xs  = xs - np.mean(xs)
    xs = xs[:,np.newaxis,np.newaxis]
    sig = 3
    w   = np.exp(-np.abs(xs)**2/sig**2).astype('float32')
    w = nd.array(w, ctx=gpu(0)).expand_dims(0).expand_dims(0)
    w = w/nd.sum(w)
    b = nd.zeros(1, ctx=gpu(0))


    for k in range(nimg):
        t = 0
        xs, ys, zs = [],[],[]
        while True:
            x0,y0,z0 = np.random.rand(3) * np.array([Lx, Ly, Lz])
            d = (x0 - np.array(xs))**2
            d += (y0 - np.array(ys))**2
            d += (z0 - np.array(zs))**2

            if len(xs)==0 or np.min(d**.5)> R * 4/3:
                xs.append(x0)
                ys.append(y0)
                zs.append(z0)

            if len(xs)==ncells:
                break

        xs = np.array(xs).astype('int32')
        ys = np.array(ys).astype('int32')
        zs = np.array(zs).astype('int32')

        for j in range(ncells):
            R0 = R * (.5 + .5 * np.random.rand())
            amp = .25 + 1.5 * np.random.rand()
            ix = rd < R0 +1.
            xc = xs[j] + xd[ix]
            yc = ys[j] + yd[ix]
            zc = zs[j] + zd[ix]
            igood = np.logical_and(np.logical_and(xc>=0, xc<Lx), np.logical_and(yc>=0, yc<Ly))
            igood = np.logical_and(igood, np.logical_and(zc>=0, zc<Lz)).flatten()

            xc,yc,zc = xc[igood], yc[igood], zc[igood]
            taper = 1./(1.+np.exp((rd[ix][igood]) - R0) / 5)

            img[k,0,zc,yc,xc] += amp * taper #* np.exp(-rd[ix][igood]/R0) #1/(1+np.exp(-rd[ix][igood]/R)) - .5

            taper = 1./(1.+np.exp((rd[ix][igood]) - R0) / 20.)
            #img[k,0,zc,yc,xc] = 1/(1+np.exp(-rd[ix][igood]/R)) - .5
            lbl[k,0,zc, yc,xc] = -xd[ix][igood] * taper
            lbl[k,1,zc, yc,xc] = -yd[ix][igood] * taper
            lbl[k,2,zc, yc,xc] = -zd[ix][igood] * taper

    out = np.concatenate((img, lbl), axis=1)
    out = nd.array(out, ctx=gpu(0))
    out[:,:1,:,:,:] = nd.Convolution(out[:,:1,:,:,:], w, b, kernel = [21,1,1], num_filter=1, pad=[10,0,0])

    return out


def run_sim2D(ishape, ncells=150, R=8):
    nimg, Ly, Lx = ishape

    xm, ym = np.meshgrid(np.arange(Lx),  np.arange(Ly))
    xd, yd = np.meshgrid(np.arange(-R,R+1),  np.arange(-R,R+1))
    rd = (xd**2 + yd**2)**.5

    lbl = np.zeros((nimg,2,Ly,Lx), 'float32')
    img = np.zeros((nimg,1,Ly,Lx), 'float32')

    img = []

    for k in range(nimg):
        xs = (np.random.rand(ncells,) * Lx).astype('int32')
        ys = (np.random.rand(ncells,) * Ly).astype('int32')

        img.append(np.zeros((3, Ly, Lx), 'float32'))
        for j in range(ncells):
            ix = rd < R * (.75 + .25 * np.random.rand())
            xc = xs[j] + xd[ix].flatten()
            yc = ys[j] + yd[ix].flatten()
            igood = np.logical_and(np.logical_and(xc>=0, xc<Lx), np.logical_and(yc>=0, yc<Ly)).flatten()

            xc,yc = xc[igood], yc[igood]

            img[k][0,yc,xc] = np.exp(-rd[ix][igood]/R) #1/(1+np.exp(-rd[ix][igood]/R)) - .5
            #img[k,0,yc,xc] = 1/(1+np.exp(-rd[ix][igood]/R)) - .5
            img[k][1, yc,xc] = xd[ix][igood]
            img[k][2, yc,xc] = yd[ix][igood]

    return img


def new_batch3D(img, xy = (24, 224,224)):
    nchan, Lz, Ly, Lx = img.shape

    theta = np.random.rand() * np.pi * 2
    scale = .9 + np.random.rand()/5
    dxy = (np.random.rand(2,) - .5) * np.array([Lx*scale-xy[-2] - 200,Ly*scale-xy[-1] - 200])

    cc = np.array([Lx/2, Ly/2])
    cc1 = cc + dxy

    pts1 = np.float32([cc,cc + np.array([1,0]), cc + np.array([0,1])])
    pts2 = np.float32([cc1, cc1 + np.array([scale * np.cos(theta), scale *np.sin(theta)]),
                       cc1 + np.array([scale * np.cos(np.pi/2+theta),scale*np.sin(np.pi/2+theta)])])
    M = cv2.getAffineTransform(pts1,pts2)

    imgi = np.zeros((nchan,) + xy, 'float32')
    for k in range(Lz):
        xi = np.transpose(img[:,k,:,:], (1,2,0))
        xc = np.zeros((xy[-2], xy[-1],nchan), 'float32')
        xc[:,:,0]   = cv2.warpAffine(xi[:,:,0],M,(xy[-2],xy[-1]), flags=cv2.INTER_LINEAR)
        xc[:,:,1:] = cv2.warpAffine(xi[:,:,1:],M,(xy[-2],xy[-1]), flags=cv2.INTER_NEAREST)

        xc = np.transpose(xc, (2, 0, 1))

        imgi[0, k,:,:] = xc[0]
        imgi[3, k,:,:] = xc[3]
        imgi[4, k,:,:] = xc[4]
        imgi[1, k,:,:] = scale * (xc[1] * np.cos(-theta)  + xc[2] * np.sin(-theta))
        imgi[2, k,:,:] = scale * (-xc[1] * np.sin(-theta) + xc[2] * np.cos(-theta))


    return imgi
