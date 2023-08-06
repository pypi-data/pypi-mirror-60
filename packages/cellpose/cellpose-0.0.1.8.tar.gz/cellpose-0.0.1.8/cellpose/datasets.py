import sys
import numpy as np
from skimage import draw
from glob import glob
from xml.etree import ElementTree as ET
from skimage.external import tifffile
from skimage import transform
import urllib.request
import zipfile
import imageio
import os
from tqdm import tqdm_notebook as tqdm
import cv2
import subprocess
from multiprocessing import Pool
from skimage import io
import pickle

try:
    from medpy.io import load
    MEDPY=True
except:
    MEDPY=False


def diameters(masks):
    unique, counts = np.unique(np.int32(masks), return_counts=True)
    counts = counts[1:]
    md = np.median(counts**0.5)
    if np.isnan(md):
        md = 0
    return md, counts**0.5

def load_pickle(filename, filecell, cyto=True, specialist=False):        
    with open(filename, 'rb') as pickle_in:
        V=pickle.load(pickle_in)

    np.random.seed(101)
    r = np.random.rand(10000)
        
    if cyto:
        r[610] = 0. # put one of kenneth's images in test
        iscell = np.load(filecell)
        ls = [1,2,3,4,5,0,6]
        if specialist:
            ls = [1]
            iscell[140:] = -1
        print(ls)
        vf=[]
        type_cell=[]
        for k in range(len(ls)):
            irange = list((iscell==ls[k]).nonzero()[0])
            type_cell.extend(list(np.ones(len(irange))*ls[k]))
            vf.extend([V[k] for k in irange])
        diam_mean = 27.
        
    else:
        iscell = np.load(filecell)
        ls = [1,2,3,4]
        vf = []
        type_cell = []
        for k in range(len(ls)):
            irange = list((iscell==ls[k]).nonzero()[0])
            type_cell.extend(list(np.ones(len(irange))*ls[k]))
            vf.extend([V[k] for k in irange])
        diam_mean = 15.
        
    type_cell = np.array(type_cell)
    train_cell = type_cell[r[:len(type_cell)]>.1]
    test_cell = type_cell[r[:len(type_cell)]<.1]
    print(train_cell.shape)

    vft = [vf[k] for k in (r[:len(vf)]<.1).nonzero()[0]]
    vf  = [vf[k] for k in (r[:len(vf)]>.1).nonzero()[0]]

    train_data = []
    train_labels = []
    nimg = len(vf)
    for n in range(nimg):
        img = vf[n][0][:1]
        if cyto:
            if len(vf[n][1])>0:
                img = np.concatenate((img, vf[n][1][np.newaxis,...]), axis=0)
            else:
                img = np.concatenate((img, np.zeros_like(img)), axis=0)
        diam = diameters(vf[n][2])[0]
        if diam>0:
            train_data.append(img)
            if cyto:
                train_labels.append(vf[n][2][np.newaxis,...]+1)
            else:
                train_labels.append(vf[n][2][np.newaxis,...])
        
    test_data = []
    test_labels = []
    for n in range(len(vft)):
        img = vft[n][0][:1]
        if cyto:
            if len(vft[n][1])>0:
                img = np.concatenate((img, vft[n][1][np.newaxis,...]), axis=0)
            else:
                img = np.concatenate((img, np.zeros_like(img)), axis=0)
        test_data.append(img)
        test_labels.append(vft[n][2][np.newaxis,...])
    
    print(r[0], len(train_data), len(vft))

    return train_data, train_labels, train_cell, test_data, test_labels, test_cell

def gabors(npix):
    ''' npix - size of gabor patch (should be ODD)'''
    y,x=np.meshgrid(np.arange(npix),np.arange(npix))
    sigma = 1
    f = 0.1
    theta = np.linspace(0, 2*np.pi, 33)[:-1]
    theta = theta[:,np.newaxis,np.newaxis]
    ycent,xcent = y.mean(), x.mean()
    yc = y - ycent
    xc = x - xcent
    ph = np.pi/2

    xc = xc[np.newaxis,:,:]
    yc = yc[np.newaxis,:,:]
    G = np.exp(-(xc**2 + yc**2) / (2*sigma**2)) * np.cos(ph + f * (yc*np.cos(theta) + xc*np.sin(theta)))

    return G

def get_batch(all_data, idx, augment=False):
    k=0
    data = []
    for i in idx:
        data.append(all_data[i])
    if augment:
        with Pool(10) as p:
            out = p.map(transform, data)
        #out = nd.array(out)
    else:
        out = nd.array(np.transpose(data[:self.npix,:self.npix,:], (2,0,1)))
    return out

def augment(data):
    xy = [224, 224]
    Ly, Lx, nchan = data.shape

    flip = np.random.rand()>.5
    theta = np.random.rand() * np.pi * 2
    scale = .9 + np.random.rand()/5
    dxy = np.maximum(0, np.array([Lx*scale-xy[1],Ly*scale-xy[0]]))
    dxy = (np.random.rand(2,) - .5) * dxy

    cc = np.array([Lx/2, Ly/2])
    cc1 = cc + dxy
    if flip:
        data = data[:,::-1,:]
        data[:,:,1] = - data[:,:,1]

    pts1 = np.float32([cc,cc + np.array([1,0]), cc + np.array([0,1])])
    pts2 = np.float32([cc1,
            cc1 + scale*np.array([np.cos(theta), np.sin(theta)]),
            cc1 + scale*np.array([np.cos(np.pi/2+theta), np.sin(np.pi/2+theta)])])
    M = cv2.getAffineTransform(pts1,pts2)

    augdata = np.zeros((4, xy[0], xy[1]), dtype=np.float32)
    xi = cv2.warpAffine(data[:,:,:3], M, (xy[0],xy[1]), flags=cv2.INTER_LINEAR)
    augdata[3]  = cv2.warpAffine(data[:,:,3], M,(xy[0],xy[1]), flags=cv2.INTER_NEAREST)
    augdata[0] = xi[:,:,0]
    # rotate flow field arrows
    augdata[1] = scale * (xi[:,:,1] * np.cos(-theta) + xi[:,:,2] * np.sin(-theta))
    augdata[2] = scale * (-xi[:,:,1] * np.sin(-theta) + xi[:,:,2] * np.cos(-theta))
    return augdata


def imgs_masks_to_pngs(dataroot=None):
    if dataroot is None:
        dataroot = os.getcwd()
    saveroot = os.path.join(dataroot, 'flows/')
    if not os.path.isdir(saveroot):
        os.makedirs(saveroot)

    files_imgs = sorted(glob(os.path.join(dataroot, 'images/*.tif')))
    files_masks = sorted(glob(os.path.join(dataroot, 'masks/*.tif')))

    nimgs = len(files_imgs)
    print('converting images and masks to 4D pngs with flows')
    pbar = tqdm(total=nimgs)

    for i in range(nimgs):
        img = tifffile.imread(files_imgs[i])
        mask = tifffile.imread(files_masks[i])
        filename = os.path.splitext(os.path.split(files_imgs[i])[1])[0]
        V = img_to_flow(img, mask)
        # save to png
        imageio.imsave(os.path.join(saveroot, filename+'.jpg'), V[:,:,:3], compress_level=0)
        pbar.update(1)
    pbar.close()

def cells_vs_background(im, m):
    return np.median(im[m>0]) < np.median(im[m==0])

def remove_overlaps(masks, cellpix, medians):
    """ replace overlapping mask pixels with mask id of closest mask
        masks = Nmasks x Ly x Lx
    """
    overlaps = np.array(np.nonzero(cellpix>1.5)).T
    dists = ((overlaps[:,:,np.newaxis] - medians.T)**2).sum(axis=1)
    tocell = np.argmin(dists, axis=1)
    masks[:, overlaps[:,0], overlaps[:,1]] = 0
    masks[tocell, overlaps[:,0], overlaps[:,1]] = 1

    # labels should be 1 to mask.shape[0]
    masks = masks.astype(int) * np.arange(1,masks.shape[0]+1,1,int)[:,np.newaxis,np.newaxis]
    masks = masks.sum(axis=0)
    return masks

def list_to_masks(img, files_masks):
    """ list of *.png files with masks to single image"""
    masks = []
    k=0
    shape = img.shape[:2]
    cellpix = np.zeros(shape)
    medians=[]
    for f in files_masks:
        mask = imageio.imread(f)>0
        cellpix += mask
        masks.append(mask)
        ypix, xpix = mask.nonzero()
        medians.append(np.array([ypix.mean(), xpix.mean()]))
        k+=1
    masks=np.array(masks)
    medians=np.array(medians)

    masks = remove_overlaps(masks, cellpix, medians)

    return masks

def xml_to_masks(img, xml_file):
    ''' parse XML file for MoNuSeg data - converts outlines to masks'''
    tree = ET.parse(xml_file)
    root = tree.getroot()

    shape = img.shape[:2]
    vrc = []
    for r in root.findall('.//Region'):
        vertex_row_coords, vertex_col_coords = [], []
        for v in r.find('Vertices'):
            vertex_row_coords.append(int((float(v.get('Y')))-1))
            vertex_col_coords.append(int((float(v.get('X')))-1))
        vrc.append(np.array([vertex_row_coords, vertex_col_coords]).T)
    masks = outlines_to_masks(vrc, shape)
    return masks

def outlines_to_masks(vrc, shape):
    masks = []
    medians=[]
    cellpix = np.zeros(shape)

    for k in range(len(vrc)):
        vr = vrc[k][:,1]
        vc = vrc[k][:,2]
        fill_row_coords, fill_col_coords = draw.polygon(vr, vc, shape)
        mask = np.zeros(shape, np.bool)
        mask[fill_row_coords, fill_col_coords] = True
        masks.append(mask)
        medians.append(np.array([fill_row_coords.mean(), fill_col_coords.mean()]))
        cellpix[fill_row_coords, fill_col_coords]+=1

    masks=np.array(masks)
    medians=np.array(medians)

    masks = remove_overlaps(masks, cellpix, medians)

    return masks

def download_masks_monuseg(dataroot=None):
    ''' download and compute masks for MoNuSeg data '''
    if dataroot is None:
        dataroot = os.getcwd()
    # if not downloaded
    if not os.path.isdir(os.path.join(dataroot, 'MoNuSeg')):
        print('downloading zip file...')
        urllib.request.urlretrieve('https://www.dropbox.com/s/d2d9ffdkvgb1h0u/MoNuSeg%20Training%20Data.zip?dl=1',
                               os.path.join(dataroot, 'MoNuSeg.zip'))
        print('extracting zip file...')
        with zipfile.ZipFile(os.path.join(dataroot, 'MoNuSeg.zip'), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(dataroot, 'MoNuSeg'))
    else:
        print('data already downloaded')

    files_imgs = sorted(glob(os.path.join(dataroot, 'MoNuSeg/MoNuSeg Training Data/Tissue Images/*.png')))
    files_outlines = sorted(glob(os.path.join(dataroot, 'MoNuSeg/MoNuSeg Training Data/Annotations/*.xml')))
    if len(files_imgs) != len(files_outlines):
        print('ERROR: different number of images and outlines (pngs and xmls)')
        return

    imgs, masks = [], []
    print('converting outlines to masks...')
    nimgs = len(files_imgs)
    pbar = tqdm(total=nimgs)

    for i in range(nimgs):
        img = imageio.imread(files_imgs[i])
        mask = xml_to_masks(img, files_outlines[i])

        imgs.append(img.astype(np.float32).mean(axis=-1).astype(np.uint8))
        masks.append(mask)
        pbar.update(1)
    pbar.close()

    print('saving images and masks as tiffs')
    prefix = 'MNS'
    save_images_masks_split(dataroot, prefix, imgs, masks)
    return imgs, masks

def download_masks_dsb2018(dataroot=None):
    if dataroot is None:
        dataroot = os.getcwd()
    # if not downloaded
    if not os.path.isdir(os.path.join(dataroot, 'raw/DSB2018')):
        print('downloading zip file...')
        urllib.request.urlretrieve('https://github.com/lopuhin/kaggle-dsbowl-2018-dataset-fixes/archive/master.zip',
                               os.path.join(dataroot, 'raw/DSB2018.zip'))
        print('extracting zip file...')
        with zipfile.ZipFile(os.path.join(dataroot, 'DSB2018.zip'), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(dataroot, 'raw/DSB2018'))
    else:
        print('data already downloaded')


    datafolder = os.path.join(dataroot, 'raw/DSB2018/kaggle-dsbowl-2018-dataset-fixes-master/stage1_train/')
    folders = sorted(glob(os.path.join(datafolder, '*/')))
    nimgs = len(folders)
    pbar = tqdm(total=nimgs)

    print('processing masks')
    imgs,masks,names=[],[],[]
    for i in range(nimgs):
        file_img = glob(os.path.join(folders[i], 'images/*.png'))[0]
        files_masks = glob(os.path.join(folders[i], 'masks/*.png'))
        img = imageio.imread(file_img)[:,:,:3]
        mask = list_to_masks(img, files_masks)
        imgs.append(img.astype(np.float32).mean(axis=-1).astype(np.uint8))
        masks.append(mask)
        names.append(os.path.basename(folders[i][:-1]))
        pbar.update(1)
    pbar.close()

    print('saving images and masks as tiffs')
    prefix = 'DSB'
    imgs, masks = save_images_masks(dataroot, names, imgs, masks)
    return imgs, masks

def download_masks_BBBC032(dataroot=None):
    if dataroot is None:
        dataroot = os.getcwd()
    if not os.path.isdir(os.path.join(dataroot, 'raw/')):
        os.makedirs(os.path.join(dataroot, 'raw/'))
    # if not downloaded
    if not os.path.isdir(os.path.join(dataroot, 'raw/BBBC032')):
        os.makedirs(os.path.join(dataroot, 'raw/BBBC032'))
        print('downloading zip file...')
        urllib.request.urlretrieve('https://data.broadinstitute.org/bbbc/BBBC032/BBBC032_v1_dataset.zip',
                               os.path.join(dataroot, 'raw/BBBC032.zip'))
        urllib.request.urlretrieve('https://data.broadinstitute.org/bbbc/BBBC032/BBBC032_v1_DatasetGroundTruth.tif',
                               os.path.join(dataroot, 'raw/BBBC032/', 'masks.tif'))
        print('extracting zip file...')
        with zipfile.ZipFile(os.path.join(dataroot, 'raw/BBBC032.zip'), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(dataroot, 'raw/BBBC032/'))
    else:
        print('data already downloaded')
    if not os.path.isdir(os.path.join(dataroot, 'images/')):
        os.makedirs(os.path.join(dataroot, 'images/'))
    if not os.path.isdir(os.path.join(dataroot, 'masks/')):
        os.makedirs(os.path.join(dataroot, 'masks/'))

    img = tifffile.imread(os.path.join(dataroot, 'raw/BBBC032/BMP4blastocystC3.tif'))
    masks = tifffile.imread(os.path.join(dataroot, 'raw/BBBC032/masks.tif'))

    # only take range with nuclei
    xmin = ((masks>0).sum(axis=(0,2))>0).nonzero()[0].min()
    xmax = ((masks>0).sum(axis=(0,2))>0).nonzero()[0].max() + 1
    ymin = ((masks>0).sum(axis=(0,1))>0).nonzero()[0].min()
    ymax = ((masks>0).sum(axis=(0,1))>0).nonzero()[0].max() + 1
    zmin = ((masks>0).sum(axis=(1,2))>0).nonzero()[0].min()
    zmax = ((masks>0).sum(axis=(1,2))>0).nonzero()[0].max() + 1
    img = img[zmin:zmax, xmin:xmax, ymin:ymax]
    masks = masks[zmin:zmax, xmin:xmax, ymin:ymax]

    # resize and save as Zx256x256
    dtype = type(img[0,0,0])
    img = np.transpose(transform.resize(np.transpose(img,(1,2,0)), (256,256), preserve_range=True), (2,0,1)).astype(dtype)
    masks = np.transpose(transform.resize(np.transpose(masks,(1,2,0)), (256,256), order=0, preserve_range=True), (2,0,1)).astype(dtype)
    _,masks = np.unique(masks, return_inverse=True)
    tifffile.imsave(os.path.join(dataroot, 'images/BBBC032_000.tif'), img)
    tifffile.imsave(os.path.join(dataroot, 'masks/BBBC032_000.tif'), masks.astype(mdtype))

    return img, masks


def download_masks_BBBC024(dataroot=None):
    if dataroot is None:
        dataroot = os.getcwd()
    if not os.path.isdir(os.path.join(dataroot, 'raw/')):
        os.makedirs(os.path.join(dataroot, 'raw/'))
    # if not downloaded
    if not os.path.isdir(os.path.join(dataroot, 'raw/BBBC024')):
        os.makedirs(os.path.join(dataroot, 'raw/BBBC024'))
        print('downloading zip file...')
        urllib.request.urlretrieve('https://data.broadinstitute.org/bbbc/BBBC024/BBBC024_v1_c75_highSNR_images_TIFF.zip',
                               os.path.join(dataroot, 'raw/BBBC024.zip'))
        print('extracting zip file...')
        with zipfile.ZipFile(os.path.join(dataroot, 'raw/BBBC024.zip'), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(dataroot, 'raw/BBBC024/'))
    else:
        print('data already downloaded')
    if not os.path.isdir(os.path.join(dataroot, 'images/')):
        os.makedirs(os.path.join(dataroot, 'images/'))
    if not os.path.isdir(os.path.join(dataroot, 'masks/')):
        os.makedirs(os.path.join(dataroot, 'masks/'))

    files_imgs = glob(os.path.join(dataroot, 'raw/BBBC024/image-final_*.tif'))
    files_masks = glob(os.path.join(dataroot, 'raw/BBBC024/image-labels_*.tif'))
    if len(files_imgs) != len(files_masks):
        print('ERROR: different number of images and masks')
        return False

    print('resizing masks and saving')
    nimgs = len(files_imgs)
    pbar = tqdm(total=nimgs)
    for i in range(nimgs):
        img = tifffile.imread(files_imgs[i])
        masks = tifffile.imread(files_masks[i])
        idtype = type(img[0,0,0])
        mdtype = type(masks[0,0,0])
        nx = 512
        ny = int(img.shape[1]/img.shape[2] * nx)
        img = np.transpose(transform.resize(np.transpose(img,(1,2,0)), (ny,nx), preserve_range=True), (2,0,1)).astype(idtype)
        masks = np.transpose(transform.resize(np.transpose(masks,(1,2,0)), (ny,nx), order=0, preserve_range=True), (2,0,1)).astype(mdtype)
        _,masks = np.unique(masks, return_inverse=True)
        tifffile.imsave(os.path.join(dataroot, 'images/BBBC024_%03d.tif'%i), img)
        tifffile.imsave(os.path.join(dataroot, 'masks/BBBC024_%03d.tif'%i), masks.astype(mdtype))
        pbar.update(1)
    pbar.close()
    return img,masks

def download_masks_ACME(dataroot=None):
    if MEDPY:
        if dataroot is None:
            dataroot = os.getcwd()
        if not os.path.isdir(os.path.join(dataroot, 'raw/')):
            os.makedirs(os.path.join(dataroot, 'raw/'))
        # if not downloaded
        if not os.path.isdir(os.path.join(dataroot, 'raw/ACME')):
            os.makedirs(os.path.join(dataroot, 'raw/ACME'))
            print('downloading zip files...')
            urllib.request.urlretrieve('https://doi.org/10.1371/journal.pcbi.1002780.s001',
                                   os.path.join(dataroot, 'raw/ACME_S1.zip'))
            urllib.request.urlretrieve('https://doi.org/10.1371/journal.pcbi.1002780.s002',
                                   os.path.join(dataroot, 'raw/ACME_S2.zip'))
            print('extracting zip files...')
            with zipfile.ZipFile(os.path.join(dataroot, 'raw/ACME_S1.zip'), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(dataroot, 'raw/ACME/'))
            with zipfile.ZipFile(os.path.join(dataroot, 'raw/ACME_S2.zip'), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(dataroot, 'raw/ACME/'))
        else:
            print('data already downloaded')

        if not os.path.isdir(os.path.join(dataroot, 'images/')):
            os.makedirs(os.path.join(dataroot, 'images/'))
        if not os.path.isdir(os.path.join(dataroot, 'masks/')):
            os.makedirs(os.path.join(dataroot, 'masks/'))

        img, image_header = load(os.path.join(dataroot, 'raw/ACME/DatasetS1/PresomiticMesoderm/Somite0.mha'))
        masks, image_header = load(os.path.join(dataroot, 'raw/ACME/DatasetS1/PresomiticMesoderm/Somite0-segment.mha'))
        masks -= 1
        img = np.transpose(img, (2,0,1))
        masks = np.transpose(masks, (2,0,1))
        tifffile.imsave(os.path.join(dataroot, 'images/ACME_%03d.tif'%0), img)
        tifffile.imsave(os.path.join(dataroot, 'masks/ACME_%03d.tif'%0), masks)

        nimgs = 10
        for i in range(nimgs):
            img, image_header = load(os.path.join(dataroot, 'raw/ACME/DatasetS2/Synthetic/raw/%d.mha'%(i+1)))
            masks, image_header = load(os.path.join(dataroot, 'raw/ACME/DatasetS2/Synthetic/manual/%d.mha'%(i+1)))
            masks -= 1
            img = np.transpose(img, (2,0,1))
            masks = np.transpose(masks, (2,0,1))
            tifffile.imsave(os.path.join(dataroot, 'images/ACME_%03d.tif'%(i+1)), img)
            tifffile.imsave(os.path.join(dataroot, 'masks/ACME_%03d.tif'%(i+1)), masks)

    else:
        print("ERROR: need to 'pip install medpy' ")


def save_images_masks(dataroot, names, imgs, masks):
    if not os.path.isdir(os.path.join(dataroot, 'images/')):
        os.makedirs(os.path.join(dataroot, 'images/'))
    if not os.path.isdir(os.path.join(dataroot, 'masks/')):
        os.makedirs(os.path.join(dataroot, 'masks/'))
    nimgs = len(imgs)
    pbar = tqdm(total=nimgs)
    i=0
    for i in range(nimgs):
        isdark = cells_vs_background(imgs[i], masks[i])
        if isdark:
            imgs[i] = 255 - imgs[i]
            imgs[i] = np.clip(imgs[i], 0, 255)
        im = imgs[i]
        m = masks[i].astype(np.uint16)
        name = names[i]+'.tif'
        save_tifs(dataroot, name, im, m)
        pbar.update(1)
    pbar.close()
    return imgs, masks


def save_images_masks_split(dataroot, prefix, imgs, masks):
    if not os.path.isdir(os.path.join(dataroot, 'images/')):
        os.makedirs(os.path.join(dataroot, 'images/'))
    if not os.path.isdir(os.path.join(dataroot, 'masks/')):
        os.makedirs(os.path.join(dataroot, 'masks/'))
    nimgs = len(imgs)
    pbar = tqdm(total=nimgs)
    i=0
    ii=0
    for i in range(nimgs):
        isdark = cells_vs_background(imgs[i], masks[i])
        if isdark:
            imgs[i] = 255 - imgs[i]
            imgs[i] = np.clip(imgs[i], 0, 255)
        for j in range(3):
            for k in range(3):
                im = imgs[i][k*333:(k+1)*333, j*333:(j+1)*333]
                m = masks[i][k*333:(k+1)*333, j*333:(j+1)*333]
                name = '%s_%03d.tif'%(prefix,ii)
                save_tifs(dataroot, name, im, m)
                ii+=1
        pbar.update(1)
    pbar.close()
    return imgs, masks

def save_tifs(dataroot, name, im, m):
    tifffile.imsave(os.path.join(dataroot, 'images/', name), im)
    _, mask = np.unique(m, return_inverse=True)
    mask = np.reshape(mask, im.shape)
    tifffile.imsave(os.path.join(dataroot, 'masks/', name), mask)
