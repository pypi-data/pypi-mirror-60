from mxnet import gluon, nd
from mxnet.gluon import nn
import numpy as np

nfeat = 128
sz  = [3, 3, 3, 3, 3]
sz2 = [3, 3, 3, 3, 3]
szf = [1]

class SZnet(gluon.HybridBlock):
    def __init__(self, **kwargs):
        super(SZnet, self).__init__(**kwargs)
        with self.name_scope():
            self.full0    = nn.Dense(4)
            #self.batchnorm0 = nn.BatchNorm(axis=1)
            self.full1    = nn.Dense(1)
            #self.do       = nn.Dropout(0.5)

    def hybrid_forward(self, F, x):
        x0 = self.full0(x)
        x0 = F.relu(x0)#self.batchnorm0(x0))
        #x0 = F.relu(x0)
        #x1 = self.full1(self.do(x0))
        x1 = self.full1(x0)
        return x1

class MASKnet(gluon.HybridBlock):
    def __init__(self, **kwargs):
        super(MASKnet, self).__init__(**kwargs)
        with self.name_scope():
            nconv = 32
            sz = 3
            sz2= 3
            self.down0 = downblock(nconv, sz, sz2, pool=False)
            self.down1 = downblock(nconv, sz, sz2)
            self.down2 = downblock(nconv, sz, sz2)
            self.pool_all = nn.GlobalAvgPool2D()
            self.dense    = nn.Dense(1)

    def hybrid_forward(self, F, x):
        x = self.down0(x)
        x = self.down1(x)
        x = self.down2(x)
        x1 = self.pool_all(x)
        x2 = self.dense(x1)
        return x2

def batchconv(nconv, sz):
    conv = nn.HybridSequential()
    with conv.name_scope():
        conv.add(
                nn.Conv2D(nconv, kernel_size=sz, padding=sz // 2),
                nn.BatchNorm(axis=1),
                nn.Activation('relu'),
        )
    return conv

def batchdense(nfeat):
    conv = nn.HybridSequential()
    with conv.name_scope():
        conv.add(
                nn.Dense(nfeat),
                #nn.BatchNorm(axis=1),
                nn.Activation('relu'),
        )
    return conv

def downblock(nconv, sz, sz2, pool=True):
    conv = nn.HybridSequential()
    if pool:
        conv.add(nn.AvgPool2D(pool_size=(2,2), strides=(2,2)))
    conv.add(batchconv(nconv, sz))
    conv.add(batchconv(nconv, sz2))
    return conv

class densedownsample(nn.HybridBlock):
    def __init__(self, nbase2, **kwargs):
        super(densedownsample, self).__init__(**kwargs)
        with self.name_scope():
            self.down = nn.HybridSequential()
            self.pool = nn.AvgPool2D(pool_size=(2,2), strides=(2,2))
            for n in range(len(nbase2)):
                self.down.add(batchconv(nbase2[n], 3))

    def hybrid_forward(self, F, x):
        xd = self.pool(x)
        for n in range(len(self.down)):
            y = self.down[n](xd)
            xd = F.concat(xd, y, dim=1)
        return y


class downsample(nn.HybridBlock):
    def __init__(self, nbase, sz, sz2, **kwargs):
        super(downsample, self).__init__(**kwargs)
        with self.name_scope():
            self.down = nn.HybridSequential()
            for n in range(len(nbase)):
                if n==1:
                    self.down.add(densedownsample([16, 32, 64, 128, 256]))
                else:
                    self.down.add(downblock(nbase[n], sz[n], sz2[n], n>0))


    def hybrid_forward(self, F, x):
        xd = [self.down[0](x)]
        for n in range(1, len(self.down)):
            xd.append(self.down[n](xd[n-1]))
        return xd

class upblock(nn.HybridBlock):
    def __init__(self, nconv, sz, **kwargs):
        super(upblock, self).__init__(**kwargs)
        with self.name_scope():
            self.conv0 = batchconv(nconv, sz)
            self.conv1 = batchconv(nconv, sz)
            self.full = nn.Dense(nconv)

    def hybrid_forward(self, F, y, x, style):
        y = self.conv0(y)
        y = x + y #F.concat(x, y, dim=1)
        y = self.conv1(y)
        y = F.broadcast_add(y , self.full(style).expand_dims(-1).expand_dims(-1))
        y = F.relu(y)
        return y

class upsample(nn.HybridBlock):
    def __init__(self, nbase, sz, **kwargs):
        super(upsample, self).__init__(**kwargs)
        with self.name_scope():
            self.up = nn.HybridSequential()
            for n in range(len(nbase)):
                self.up.add(upblock(nbase[n], sz[n]))

    def hybrid_forward(self, F, style, xd):#x0, x1, x2, x3, style):
        y = self.up[-1](xd[-1], xd[-1], style)
        for n in range(len(self.up)-2,-1,-1):
            y = F.UpSampling(y, scale=2, sample_type='nearest')
            y = self.up[n](y, xd[n], style)
        return y

class output(nn.HybridBlock):
    def __init__(self, nfeat, szf, **kwargs):
        super(output, self).__init__(**kwargs)
        with self.name_scope():
            self.full0    = nn.Dense(nfeat)
            self.uconv0   = nn.Conv2D(channels=nfeat,      kernel_size=szf[0],  padding = szf[0]//2)
            self.ubatchnorm0 = nn.BatchNorm(axis=1)
            self.oconv1   = nn.Conv2D(channels=3,    kernel_size=szf[0],  padding = szf[0]//2)

    def hybrid_forward(self, F, y0, style):
        y = self.ubatchnorm0(self.uconv0(y0))
        feat = self.full0(style)
        y = F.broadcast_add(y, feat.expand_dims(-1).expand_dims(-1))
        y = F.relu(y)
        y = self.oconv1(y)
        return y


class make_style(nn.HybridBlock):
    def __init__(self, nbase, **kwargs):
        super(make_style, self).__init__(**kwargs)
        with self.name_scope():
            self.pool_all = nn.GlobalAvgPool2D()
            #self.flatten = nn.Flatten()
            #self.full = nn.HybridSequential()
            #for j in range(len(nbase)):
        #        self.full.add(batchdense(nbase[j]))

    def hybrid_forward(self, F, x0):
        style = self.pool_all(x0)
        svar  = self.pool_all(x0**2)
        #style = self.flatten(style)
        style = F.broadcast_div(style, F.sum(style**2, axis=1).expand_dims(1)**.5)
        svar  = F.broadcast_div(svar,  F.sum(svar**2, axis=1).expand_dims(1)**.5)

        #for j in range(len(self.full)):
        #    y = self.full[j](style)
        #    style = F.concat(style, y, dim=1)
        return style, svar

class CPnet(gluon.HybridBlock):

    def __init__(self, nbase, **kwargs):
        super(CPnet, self).__init__(**kwargs)
        with self.name_scope():
            self.downsample = downsample(nbase, sz, sz2)
            self.upsample = upsample(nbase, sz)
            self.output = output(nfeat, szf)
            self.make_style = make_style([64, 128, 256])

    def hybrid_forward(self, F, data):
        xd    = self.downsample(data)
        style, svar = self.make_style(xd[-1])
        y0    = self.upsample(style, xd)
        T0    = self.output(y0, style)
        style = F.concat(style, svar, dim=1)
        return T0, style

class Net2D(gluon.HybridBlock):

    def __init__(self, **kwargs):
        super(Net2D, self).__init__(**kwargs)
        with self.name_scope():

            self.conv1  = nn.Conv2D(channels=nbase[0],  kernel_size=sz[0],  padding = sz[0]//2)
            self.conv11 = nn.Conv2D(channels=nbase[0],  kernel_size=sz2[0],  padding = sz2[0]//2)
            self.batchnorm1 = nn.BatchNorm(axis=1)

            self.conv2  = nn.Conv2D(channels=nbase[1],  kernel_size=sz[1],  padding = sz[1]//2)
            self.conv21 = nn.Conv2D(channels=nbase[1],  kernel_size=sz2[1],  padding = sz2[1]//2)
            self.batchnorm2 = nn.BatchNorm(axis=1)

            self.conv3  = nn.Conv2D(channels=nbase[2],  kernel_size=sz[2],  padding = sz[2]//2)
            self.conv31 = nn.Conv2D(channels=nbase[2],  kernel_size=sz2[2],  padding = sz2[2]//2)
            self.batchnorm3 = nn.BatchNorm(axis=1)

            self.conv4  = nn.Conv2D(channels=nbase[3],  kernel_size=sz[3],  padding = sz[3]//2)
            self.conv41 = nn.Conv2D(channels=nbase[3],  kernel_size=sz2[3],  padding = sz2[3]//2)
            self.batchnorm4 = nn.BatchNorm(axis=1)


            self.uconv4  = nn.Conv2D(channels=nbase[3],   kernel_size=sz[3],  padding = sz[3]//2)
            self.uconv41 = nn.Conv2D(channels=nbase[3],   kernel_size=sz2[3],  padding = sz2[3]//2)
            self.ubatchnorm4 = nn.BatchNorm(axis=1)

            self.uconv3  = nn.Conv2D(channels=nbase[2],   kernel_size=sz[2],  padding = sz[2]//2)
            self.uconv31 = nn.Conv2D(channels=nbase[2],   kernel_size=sz2[2],  padding = sz2[2]//2)
            self.ubatchnorm3 = nn.BatchNorm(axis=1)

            self.uconv2  = nn.Conv2D(channels=nbase[1],   kernel_size=sz[1],  padding = sz[1]//2)
            self.uconv21 = nn.Conv2D(channels=nbase[1],   kernel_size=sz2[1],  padding = sz2[1]//2)
            self.ubatchnorm2 = nn.BatchNorm(axis=1)

            self.uconv1  = nn.Conv2D(channels=nbase[0],   kernel_size=sz[0],  padding = sz[0]//2)
            self.uconv11 = nn.Conv2D(channels=nbase[0],   kernel_size=sz2[0],  padding = sz2[0]//2)
            self.ubatchnorm1 = nn.BatchNorm(axis=1)

            self.ubatchnorm11 = nn.BatchNorm(axis=1)
            self.ubatchnorm21 = nn.BatchNorm(axis=1)
            self.ubatchnorm31 = nn.BatchNorm(axis=1)
            self.ubatchnorm41 = nn.BatchNorm(axis=1)
            self.batchnorm11 = nn.BatchNorm(axis=1)
            self.batchnorm21 = nn.BatchNorm(axis=1)
            self.batchnorm31 = nn.BatchNorm(axis=1)
            self.batchnorm41 = nn.BatchNorm(axis=1)

            self.pool_all = nn.GlobalAvgPool2D()
            self.full0    = nn.Dense(nfeat)
            self.full1    = nn.Dense(nbase[0])
            self.full2    = nn.Dense(nbase[1])
            self.full3    = nn.Dense(nbase[2])
            self.full4    = nn.Dense(nbase[3])

            self.uconv0   = nn.Conv2D(channels=nfeat,      kernel_size=szf[0],  padding = szf[0]//2)
            self.ubatchnorm0 = nn.BatchNorm(axis=1)
            self.oconv1   = nn.Conv2D(channels=4,    kernel_size=szf[0],  padding = szf[0]//2)

            #self.drop = nn.Dropout(0.5)#, axes = (2,3))
            #self.oconv0   = nn.Conv2D(channels=1,    kernel_size=1,  padding = 0)


    def upsamp(self, x):
        return nd.UpSampling(x, scale=2, sample_type='nearest')

    def pool(self, x):
        return nd.Pooling(x, kernel=(2,2), stride = (2,2), pool_type='avg')

    def combine(self, x, y):
        return x + y
        #return nd.concat(x, y, dim=1)

    def forward(self, x):
        x1 = self.conv1(x)
        x1 = nd.relu(self.batchnorm11(x1))
        x1 = self.conv11(x1) #+ x1
        x1 = nd.relu(self.batchnorm1(x1))

        x2 = self.conv2(self.pool(x1))
        x2 = nd.relu(self.batchnorm21(x2))
        x2 = self.conv21(x2)
        x2 = nd.relu(self.batchnorm2(x2))

        x3 = self.conv3(self.pool(x2))
        x3 = nd.relu(self.batchnorm31(x3))
        x3 = self.conv31(x3)
        x3 = nd.relu(self.batchnorm3(x3))

        x4 = self.conv4(self.pool(x3))
        x4 = nd.relu(self.batchnorm41(x4))
        x4 = self.conv41(x4)
        x4 = nd.relu(self.batchnorm4(x4))

        # toptop
        xp = self.pool_all(x4)
        xp = xp / nd.sum(xp**2, axis=1).expand_dims(1)**.5

        # layer 4
        X4 = self.uconv4(x4)
        X4 = nd.relu(self.ubatchnorm41(X4))
        X4 = self.uconv41(X4)
        X4 = self.ubatchnorm4(X4)
        X4 = X4 + self.full4(xp).expand_dims(-1).expand_dims(-1)
        X4 = nd.relu(X4)

        # layer 3
        X3 = self.upsamp(X4)
        #X3 = nd.concat(X3, x3, dim=1)
        X3 = self.uconv3(X3)
        X3 = nd.relu(self.ubatchnorm31(X3))
        X3 = self.combine(x3, X3)
        X3 = self.uconv31(X3)
        X3 = self.ubatchnorm3(X3)
        X3 = X3 + self.full3(xp).expand_dims(-1).expand_dims(-1)
        X3 = nd.relu(X3)

        # layer 2
        X2 = self.upsamp(X3)
        #X2 = nd.concat(X2, x2, dim=1)
        X2 = self.uconv2(X2)
        X2 = nd.relu(self.ubatchnorm21(X2))
        X2 = self.combine(x2, X2)
        X2 = self.uconv21(X2)
        X2 = self.ubatchnorm2(X2)
        X2 = X2 + self.full2(xp).expand_dims(-1).expand_dims(-1)
        X2 = nd.relu(X2)

        # layer 1
        X1 = self.upsamp(X2)
        #X1 = nd.concat(X1, x1, dim=1)
        X1 = self.uconv1(X1)
        X1 = nd.relu(self.ubatchnorm11(X1))
        X1 = self.combine(x1, X1)
        X1 = self.uconv11(X1)
        X1 = self.ubatchnorm1(X1)
        X1 = X1 + self.full1(xp).expand_dims(-1).expand_dims(-1)
        X1 = nd.relu(X1)

        # output
        #X0 = self.oconv1(X1)

        X0 = self.ubatchnorm0(self.uconv0(X1))
        #X0 = self.drop(X0)
        X0 = X0 + self.full0(xp).expand_dims(-1).expand_dims(-1)
        X0 = nd.relu(X0)
        T0 = self.oconv1(X0)
        #lbl = self.oconv0(T0**2)

        return T0, xp, X0
