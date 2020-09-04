from PIL import Image
import imagehash
import numpy as np

im = Image.open('images/0/ski.jpg')
ah = imagehash.average_hash(im)
dh = imagehash.dhash(im)
ph = imagehash.phash(im)
wh = imagehash.whash(im) #Haar
wdh = imagehash.whash(im, mode="db4") #Daubechies
ch = imagehash.colorhash(im)
print(ah,ph,dh,wh,wdh,ch)
im2 = Image.open('images/0/ski2.jpg')
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
ch2 = imagehash.colorhash(im2)
print(ah2,ph2,dh2,wh2,wdh2,ch2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2, ch - ch2)
im2 = Image.open('images/0/ski3.jpg')
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
ch2 = imagehash.colorhash(im2)
print(ah2,ph2,dh2,wh2,wdh2,ch2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2, ch - ch2)
im2 = Image.open('images/1/mug.jpg')
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
ch2 = imagehash.colorhash(im2)
print(ah2,ph2,dh2,wh2,wdh2,ch2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2, ch - ch2)
im = Image.open('images/0/ski2.jpg')
ah = imagehash.average_hash(im)
dh = imagehash.dhash(im)
ph = imagehash.phash(im)
wh = imagehash.whash(im)
wdh = imagehash.whash(im, mode="db4")
im2 = Image.open('images/0/ski3.jpg')
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2)
im = Image.open('images/1/mug.jpg')
ah = imagehash.average_hash(im)
dh = imagehash.dhash(im)
ph = imagehash.phash(im)
wh = imagehash.whash(im)
wdh2 = imagehash.whash(im2, mode="db4")
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2)

def alpharemover(image):
    if image.mode != 'RGBA':
        return image
    canvas = Image.new('RGBA', image.size, (255,255,255,255))
    canvas.paste(image, mask=image)
    return canvas.convert('RGB')

def ztransform(image):
    image = alpharemover(image)
    image = image.convert("L").resize((8, 8), Image.ANTIALIAS)
    data = image.getdata()
    quantiles = np.arange(100)
    quantiles_values = np.percentile(data, quantiles)
    zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
    image.putdata(zdata)
    return image

im = Image.open('images/0/ski.jpg')
im = ztransform(im)
ah = imagehash.average_hash(im)
dh = imagehash.dhash(im)
ph = imagehash.phash(im)
wh = imagehash.whash(im)
wdh = imagehash.whash(im, mode="db4")
print(ah,ph,dh,wh,wdh)
im2 = Image.open('images/0/ski2.jpg')
im2 = ztransform(im2)
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
print(ah2,ph2,dh2,wh2,wdh2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2)
im2 = Image.open('images/0/ski3.jpg')
im2 = ztransform(im2)
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
print(ah2,ph2,dh2,wh2,wdh2,ch2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2)
im2 = Image.open('images/1/mug.jpg')
im2 = ztransform(im2)
ah2 = imagehash.average_hash(im2)
ph2 = imagehash.phash(im2)
dh2 = imagehash.dhash(im2)
wh2 = imagehash.whash(im2)
wdh2 = imagehash.whash(im2, mode="db4")
print(ah2,ph2,dh2,wh2,wdh2,ch2)
print(ah - ah2, ph - ph2, dh - dh2, wh - wh2, wdh - wdh2)