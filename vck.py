# $Id: vck.py,v 1.26 1998/11/04 00:05:16 fms Exp fms $
#
# Visual Cryptography Kit
# (c) 1998 Olivetti Oracle Research Laboratory (ORL)
#
# Written by Frank Stajano,
# Olivetti Oracle Research Laboratory <http://www.orl.co.uk/~fms/> and
# Cambridge University Computer Laboratory <http://www.cl.cam.ac.uk/~fms27/>.
#
# Visual cryptography concept invented by Moni Naor & Adi Shamir
#
# VCK is copyrighted free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
# VCK is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along
# with VCK; see the file COPYING.  If not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA or, more sensibly, go to their web site at http://www.gnu.org/.
#
# The Python Imaging Library (available from
# http://www.pythonware.com/products/pil/ and necessary to use this
# module), is Copyright (c) 1995-7 Fredrik Lundh, Copyright (c) 1997-8
# Secret Labs AB.  All rights reserved.

"""The vck.py module (Visual Cryptography Kit,
http://www.cl.cam.ac.uk/~fms27/vck/) implements the primitives of visual
cryptography.

For more on visual cryptography read the seminal paper by Naor and Shamir
(1994), available from
http://www.wisdom.weizmann.ac.il/~naor/PAPERS/vis.ps.

The purpose of the kit is to let the reader explore this fascinating idea
in a practical hands-on fashion. The user can play around with her own
pictures, see the intermediate results of the various operations and
combine the operations in the desired way using her own python script.

Readability of the source code was a primary goal and many image
manipulation operations are implemented with very little respect for
efficiency, with the aim of simply making the algorithms obvious. It is not
expected that this kit will be used for actual encryption and so
facilitating exploration and exporting an obvious API was deemed to be more
important than making the program fast.
"""

import Tkinter
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
#import whrandom
import random
import string
import pickle
import sys

class bitmap:
    """A two-dimensional one-bit-deep bitmap suitable for VCK operations.
    The coordinate system has 0,0 at NW and xmax, ymax at SE. The external
    representation of the pixels, accessed via get() and set(), has white
    paper as 0 and black ink as 1."""

    # Protected static constants for the internal representation of the
    # pixel colours. The internal representation for pixels is that of
    # PIL's "1" format, where 0x00 is black and 0xff is white. No other
    # pixel values are allowed. Yeah, this gives a conversion for every
    # pixel access: so sue me! I just found it too confusing to have paper
    # as 1 and ink as 0, especially when it came to doing the boolean ops
    # on the images.
    _pixelBlack = 0x00
    _pixelWhite = 0xff

    # Private members:
    # __image = the image
    # __draw = the PIL gadget you use to write on the image

    def __init__(self, arg1, arg2=None):
        """The allowed forms for the constructor are:
        1- vck.bitmap("image.tif")
            ...i.e. from a file name;
        2-  vck.bitmap((x,y))
            ...ie from a 2-tuple with the size; picture will be all white."""

        self.__image = None
        self.__draw = None
        if type(arg1) == type(""):
            # form 1
            raw = Image.open(arg1)
            self.__image = raw.convert("1")
        elif type(arg1) == type((1,2)):
            if arg2 == None:
                # form 2
                self.__image = Image.new("1", arg1, bitmap._pixelWhite)

        if not self.__image:
            raise TypeError, "Give me EITHER a filename OR a " \
                  "(width, height) pair and an optional string of binary data."

        self.__draw = ImageDraw.ImageDraw(self.__image)


    def set(self, x, y, colour=1):
        """Set the pixel at x, y to be of colour colour (default 1 = black
        ink). Any colour value other than 0 (white paper) is taken to be 1
        (black ink)."""

        inkCol = None
        if colour == 0:
            # self.__draw.setink(bitmap._pixelWhite)
            inkCol = bitmap._pixelWhite
        else:
            # self.__draw.setink(bitmap._pixelBlack)
            inkCol = bitmap._pixelBlack
        self.__draw.point((x, y), fill=inkCol)

    def get(self, x, y):
        """Return the value of the pixel at x, y"""
        return not self.__image.getpixel((x, y))

    def size(self):
        """Return a 2-tuple (width, height) in pixels."""
        return self.__image.size

    def view(self, root, title="No name"):
        """Display this image in a toplevel window (optionally with the
        given title). Precondition: Tk must have been initialised (the
        caller must supply Tk's root window). Return the toplevel window,
        which the caller must hold on to otherwise it will disappear from
        the screen for various PIL/Tkinter/refcount quirks."""

        return _bitmapViewer(root, self.__image, title)

    def write(self, filename):
        """Write this bitmap to a file with the given filename. File type
        is deduced from the extension (exception if it can't be figured
        out)."""

        self.__image.save(filename)

    def pixelcode(self):
        """Return a new bitmap, twice as big linearly, by pixelcoding every
        pixel of bmp into a grid of 4 pixels. Pixelcoding means translating
        each pixel into a grid of pixels in a clever way which is the core
        idea of visual cryptography. Read the poster for more on that."""

        maxX, maxY = self.size()
        result = bitmap((2*maxX, 2*maxY))
        for x in range(maxX):
            for y in range(maxY):
                pixel = self.get(x,y)
                result.set(2*x,2*y, pixel)
                result.set(2*x,2*y+1, not pixel)
                result.set(2*x+1,2*y, not pixel)
                result.set(2*x+1,2*y+1, pixel)
        return result



def boolean(operation, bitmaps):
    """Apply the boolean operation 'operation' (a binary function of two
    integers returning an integer) to the list of bitmaps in 'bitmaps'
    (precondition: the list can't be empty and the bitmaps must all have
    the same size) and return the resulting bitmap."""

    maxX, maxY = size = bitmaps[0].size()
    result = bitmap(size)
    for x in range(maxX):
        for y in range(maxY):
            pixel = bitmaps[0].get(x,y)
            for b in bitmaps[1:]:
                pixel = apply(operation, (pixel, b.get(x,y)))
            result.set(x,y,pixel)
    return result

# Doc string for the following three functions:
# Take an arbitrary number (>=1) of bitmap arguments, all of the same size,
# and return another bitmap resulting from their pixel-by-pixel AND, OR or
# XOR as appropriate.
def AND(*args): return boolean(lambda a,b:a&b, args)
def OR(*args): return boolean(lambda a,b:a|b, args)
def XOR(*args): return boolean(lambda a,b:a^b, args)


def NOT(bmp):
    """Take a bitmap and return its negative (obtained by swopping white
    and black at each pixel)."""

    maxX, maxY = size = bmp.size()
    result = bitmap(size)
    for x in range(maxX):
        for y in range(maxY):
            result.set(x,y, not bmp.get(x,y))
    return result



def randomBitmap(size):
    """Take a size (2-tuple of x and y) and return a bitmap of that size
    filled with random pixels. WARNING! THE CODE HERE IS ONLY FOR
    DEMONSTRATION PURPOSES, SINCE IT CALLS THE STANDARD PYTHON RANDOM
    NUMBER GENERATOR, which is fine for statistics but not good enough for
    crypto. For real use, substitute this with really random data from an
    external source, or at least with a properly seeded cryptographically
    strong RNG."""

    b = bitmap(size)
    xmax, ymax = size
    for x in xrange(xmax):
        for y in xrange(ymax):
            b.set(x, y, random.randint(0,1))
    return b


class _viewer:
    """A toplevel window with a canvas."""

    def __init__(self, root, width, height, title="Unnamed VCK image"):
        self.__width = width
        self.__height = height
        self._t = Tkinter.Toplevel(root)
        Tkinter.Wm.title(self._t, title)
        self._c = Tkinter.Canvas(self._t, width=width, height=height,
                                 border=0, highlightthickness=0,
                                 background="White")
        self._c.pack()
        self._t.update()


    def psprint(self, filename):
        """Write a postscript representation of the canvas to the specified
        file."""

        # The portrait A4 page is, in mm, WxH=210x297. Let's have a safety
        # margin of 7mm all around it, and the usable area becomes 196x283.
        W = 196.0
        H = 283.0
        x1, y1, x2, y2 = self._c.bbox("all")
        options = {
            "pageanchor": "sw",
            "x": "%fp" % x1,
            "y": "%fp" % y1,
            "height": "%fp" % (y2-y1),
            "width": "%fp" % (x2-x1),
            "pagex":  "0",
            "pagey": "0",
            "file": filename,
            "colormode": "mono",
            }
        # ??? I think I'm doing all this viewport math sensibly, BUT I
        # still get a weird asymmetric margin around the thing, and I
        # haven't got a clue how to get rid of it.
        yscale = (y2-y1) / H
        xscale = (x2-x1) / W
        # The direction with the greater scaling factor is the limiting one
        if xscale > yscale:
            options["pagewidth"] = "%fm" % W
        else:
            options["pageheight"] ="%fm" % H
        self._c.update()
        apply(self._c.postscript, (), options)



    def canvas(self):
        """Return the canvas."""

        return self._c

    def __del__(self):
        self._t.destroy()


class _bitmapViewer(_viewer):
    """A viewer for bitmaps."""

    def __init__(self, root, image, title="Unnamed VCK image"):
        width, height = image.size
        _viewer.__init__(self, root, width, height, title)
        self.__photo = ImageTk.BitmapImage(
            image, background="Black", foreground="White")
        self._c.create_image(0, 0, anchor=Tkinter.NW, image=self.__photo)
        self._t.update()


def encrypt(rawPlaintext, rawPad = None):
    """Take a plaintext bitmap and, optionally, a supposedly random pad of
    the same size (one will be made up on the spot if not supplied). Return
    a 2-tuple containing the large pixelcoded versions of ciphertext and
    pad."""

    # The raw versions are the same size as the original rawPlaintext
    if not rawPad:
        rawPad = randomBitmap(rawPlaintext.size())
    rawCiphertext = XOR(rawPlaintext, rawPad)

    # The final versions are linearly twice as big due to pixelcoding
    ciphertext = rawCiphertext.pixelcode()
    pad = rawPad.pixelcode()

    return ciphertext, pad

def decrypt(ciphertext, pad):
    """Actually the decription ought to be performed without a computer
    (the whole point of visual cryptography), by just superimposing the
    transparencies of the ciphertext and pad. This is a simulation of this
    process."""

    return OR(ciphertext, pad)

def mainApp(function):
    """Execute the supplied function. The function may create new windows
    by calling bitmap.view() or by making instances of viewer, but it must
    return a list of any such windows it makes. The point of this wrapper
    is merely to shield the caller away from the quirks of initialising
    Tkinter, running its main loop and ensuring that windows don't
    disappear unexpectedly."""

    root = Tkinter.Tk()
    quit = Tkinter.Button(root, text="Quit", command=root.quit)
    quit.pack()
    Tkinter.Wm.title(root, "VCK main")

    windows = function(root)

    root.update()
    root.mainloop()

# --------------------------------------------------------------
# Analog (greyscale) version



class moonfieldViewer(_viewer):
    """A toplevel window with a canvas, suitable for viewing a moonfield."""

    R = 9 # default radius

    def __init__(self, root, mf, title="Unnamed moonfield", radius=R):
        """Precondition: the moonfield mf must be filled."""

        xmax, ymax = mf.size()
        _viewer.__init__(self, root, xmax*2*radius, ymax*2*radius, title)
        mf.renderOnCanvas(self._c, radius)
        self._t.update()

class photoViewer(_viewer):
    """A viewer for greyscale images."""

    def __init__(self, root, image, title="Unnamed VCK image"):
        width, height = image.size
        _viewer.__init__(self, root, width, height, title)
        self.__photo = ImageTk.PhotoImage(
            image)
        self._c.create_image(0, 0, anchor=Tkinter.NW, image=self.__photo)
        self._t.update()



class moonfield:
    """A 2d array of angles. Items in the array are indexed by integers in
    0..xmax, 0..ymax, with 0,0 being the NW corner. Each angle specifies
    the phase (rotation) of a black halfmoon around its centre (determined
    by its place in the array) and is represented by an integer in the
    range 0..509"""

    # Why that strange range?  Well, since we are going to use two rotated
    # halfmoons to display a luminosity, and since the luminosity of the
    # gap between the two halfmoons ranges from 255 (white) when they're 0
    # radians apart (i.e. superimposed, leaving a half-moon of white) to 0
    # (black) when they're pi radians apart (i.e. non-overlapping, covering
    # the whole disc with black), this means that there are 255 discrete
    # steps in pi (not 256, because the 256th step is already "the first of
    # the other half"), and 2*255 in 2*pi. So the integers in a moonfield
    # range from 0 to 2*255-1 = 509. And we use arithmetic modulo 510 on
    # them.

    discretePi = 255
    mod = discretePi*2
    i2d = 360.0 / mod # integer to degree conversion factor

    def __init__(self, size, filler=None):
        """Make a moonfield of the specified size. If a filler function is
        specified, fill it with it, otherwise leave the data
        uninitialised."""

        self.__data = {}
        self.__xmax, self.__ymax = size
        if filler:
            self.fill(filler)

    def size(self):
        """Return a 2-tuple with the dimensions of the moonfield."""
        return self.__xmax, self.__ymax

    def fill(self, filler):
        """Take a function f(x,y) that accepts a position in the moonfield
        and returns an integer value. Fill every cell in the moonfield with
        the value returned by the filler (taken modulo mod)."""

        for x in range(self.__xmax):
            for y in range(self.__ymax):
                self.__data[(x,y)] = filler(x,y) % self.mod

    def randomFill(self, low=0, high=mod-1):
        """Fill the moonfield with random values in the range min..max
        inclusive. WARNING: NOT GOOD FOR REAL CRYPTO USE. Use a
        cryptographically strong RNG instead of the library's unless you're
        just playing around."""

        def randomFiller(x,y, low=low, high=high):
            return random.randint(low, high)

        self.fill(randomFiller)

    def imageComplement(self, img):
        """Precondition: self must have been filled already. Take a
        greyscale image (PIL type "L"), which must have the same size as
        self. Return a new moonfield such that, if that new moonfield and
        the current one were superimposed, one would "see" the supplied
        image. NB: if the supplied image parameter is a string, an attempt
        is made to open the file of that name."""

        if type(img) == type(""):
            img = Image.open(img).convert("L")
        assert self.size() == img.size
        result = moonfield(size=(self.__xmax, self.__ymax))
        def filler(x,y,i=img, d=self.__data, pi=self.discretePi, m=self.mod):
            return (d[(x,y)] - (pi - i.getpixel((x,y)))) % m
        result.fill(filler)
        return result

    def renderOnCanvas(self, canvas, radius=moonfieldViewer.R):
        """Take a canvas and render the moonfield on it. The radius of the
        halfmoons must be specified in canvas units."""

        for x in range(self.__xmax):
            for y in range(self.__ymax):
                # Make the halfmoon at x,y
                canvas.create_arc(
                    radius*2*x, radius*2*y, radius*2*(x+1)-1, radius*2*(y+1)-1,
                    start = self.__data[(x,y)] * self.i2d, extent = 180.0,
                    fill="Black")

    def view(self, root, title="No name", radius=moonfieldViewer.R):
        """Display this image in a toplevel window (optionally with the
        given title). Preconditions: the moonfield must be filled; Tk must
        have been initialised (the caller must supply Tk's root
        window). Return the toplevel window, which the caller must hold on
        to otherwise it will disappear from the screen for various
        PIL/Tkinter/refcount quirks."""

        return moonfieldViewer(root, self, title, radius)

    def __repr__(self):
        if self.__data == {}:
            return "<uninitialised>"
        result = ""
        for y in range(self.__ymax):
            for x in range(self.__xmax):
                result = result + "%3d " % self.__data[(x,y)]
            result = result + "\n"
        return result

    def dump(self, filename):
        """Dump yourself to a file in the internal .mfd format (another
        moonfield object can later be made from such a file)."""

        pickle.dump(self, open(filename, "w"))

def moonfield_undump(filename):
    """Return a moonfield obtained by rebuilding the one that had been
    dumped to the given file."""

    return pickle.load(open(filename))
# --------------------------------------------------------------
# File-based mode of operation

def makePad(size, expandedPadFile="pad.tif", dumpFile="rawpad.pbm"):
    """Generate a random pad. (NB: remember that the RNG used here is only
    good for demos since it's not cryptographically strong!) Write out two
    files with the supplied names, one with the dump of the pad in raw form
    (necessary for encrypting later, to be kept at the agency) and one with
    the pad in expanded form, ready for use, to be given to 007. Return the
    raw and expanded bitmaps."""

    rawPad = randomBitmap(size)
    rawPad.write(dumpFile)
    expandedPad = rawPad.pixelcode()
    expandedPad.write(expandedPadFile)
    return rawPad, expandedPad

def makeCryptograph(imageFile, codedFile="coded.tif", dumpFile="rawpad.pbm"):
    """Generate a cryptograph. Take a monochrome image (the filename of a
    PIL type "1") and a file with a dump of a raw pad (Precondition: image
    and raw pad must be of the same size in pixels.)  Write out the
    cryptograph as an image file. Return the bitmap for the cryptograph."""

    pad = bitmap(dumpFile)
    plaintext = bitmap(imageFile)
    ciphertext = XOR(pad, plaintext)
    expandedCiphertext = ciphertext.pixelcode()
    expandedCiphertext.write(codedFile)
    return expandedCiphertext

def splitImage(image, shareFile1="share1.tif", shareFile2="share2.tif"):
    """Not for spies, really, just for cute demos. Take a monochrome image
    (a PIL type "1" or its filename) and produce two image files that, when
    superimposed, will yield the image. Return the bitmaps for the two
    shares."""

    _, expandedPad = makePad(Image.open(image).size, shareFile1)
    expandedCiphertext = makeCryptograph(image, shareFile2)
    return expandedPad, expandedCiphertext

# And same again for greyscale... Note that here we HAVE to use windows,
# even if we want to run in batch mode, because without drawing the stuff
# on the canvas we can't generate the postscript (actually, seeing how
# messy it is to get the margins to come out right, I'm thinking that I
# perhaps ought to generate the postscript by hand, without any canvas,
# like I used to do in the old, deprecated C++ version of VCK...)

def makePadG(root, size, expandedPadFile="pad.ps", dumpFile="rawpad.mfd"):
    """Generate a random pad. (NB: remember that the RNG used here is only
    good for demos since it's not cryptographically strong!) Write out two
    files with the supplied names, one with the dump of the pad in raw form
    (necessary for encrypting later, to be kept at the agency) and one with
    the pad in expanded form, ready for use, to be given to 007. Return a
    pair made of the moonfield for the pad and a viewer on it."""

    raw = moonfield(size)
    raw.randomFill()
    raw.dump(dumpFile)
    v = raw.view(root)
    v.psprint(expandedPadFile)
    return raw, v

def makeCryptographG(root, image, codedFile="coded.ps", dumpFile="rawpad.mfd"):
    """Generate a cryptograph. Take an image (either a PIL image of type
    "L" or a filename) and a file with a dump of a raw pad moonfield
    (Precondition: image and raw pad must be of the same size in pixels.)
    Write out the cryptograph as a postscript file of halfmoons. Return a
    pair made of the moonfield for the cryptograph and a viewer on it."""

    pad = moonfield_undump(dumpFile)
    ciphertext = pad.imageComplement(image)
    v = ciphertext.view(root)
    v.psprint(codedFile)
    return ciphertext, v

def splitImageG(root, image, shareFile1="share1.ps", shareFile2="share2.ps"):
    """Not for spies, really, just for cute demos. Take a greyscale image
    (either an "L" image object or a filename) and produce two postscript
    files of halfmoons that, when superimposed, will yield the
    image. Return a quadruple made of the two shares and two viewers
    showing them."""

    if type(image) == type(""):
        image = Image.open(image).convert("L")
    p, v1 = makePadG(root, image.size, shareFile1)
    c, v2 = makeCryptographG(root, image, shareFile2)
    return p, c, v1, v2

# --------------------------------------------------------------
# Self-test
# Activate the test you want (one at a time) by uncommenting it in main().

def testEncryptDecrypt(root):
    """Encrypt a monochrome image and decrypt it, showing the results on
    screen (work in memory, don't save to files)."""

    plaintext = bitmap("vck.gif")
    ciphertext, pad = encrypt(plaintext)
    decryptedResult = decrypt(ciphertext, pad)

    v1 = plaintext.view(root, "plaintext")
    v2 = pad.view(root, "pad (pixelcoded)")
    v3 = ciphertext.view(root, "ciphertext (pixelcoded)")
    v4 = decryptedResult.view(root, "decrypted result")
    return v1, v2, v3, v4

def testAllIntermediateValues(root):
    """Encrypt a monochrome image and decrypt it, but do it all "by hand"
    and show all the intermediate results at each step."""

    rawPlaintext = bitmap("vck.gif")
    v1 = rawPlaintext.view(root, "raw plaintext")

    rawPad = randomBitmap(rawPlaintext.size())
    v2 = rawPad.view(root, "raw pad")

    rawCiphertext = XOR(rawPlaintext, rawPad)
    v3 = rawCiphertext.view(root, "raw ciphertext")

    pad = rawPad.pixelcode()
    v4 = pad.view(root, "pixelcoded pad")

    ciphertext = rawCiphertext.pixelcode()
    v5 = ciphertext.view(root, "pixelcoded ciphertext")

    decryptedResult = OR(ciphertext, pad)
    v6 = decryptedResult.view(root, "decrypted result")

    return v1, v2, v3, v4, v5, v6


def testBooleanOps(root):
    """Demonstrate the boolean operations available in VCK by combining an
    image (vck.tif must be in the current directory) with a diagonal
    cross."""

    letters = bitmap("vck.tif")
    v1 = letters.view(root, "vck")

    cross = bitmap(letters.size())
    xmax, ymax = cross.size()
    r = ymax*1.0/xmax
    for x in range(xmax):
        cross.set(x, x*r)
        cross.set(x, x*r+1)
        cross.set(x, x*r-1)
        cross.set(x, ymax-x*r)
        cross.set(x, ymax-x*r+1)
        cross.set(x, ymax-x*r-1)
    v2 = cross.view(root, "cross")

    xorResult = XOR(letters, cross)
    v3 = xorResult.view(root, "vck XOR cross")

    orResult = OR(letters, cross)
    v4 = orResult.view(root, "vck OR cross")

    andResult = AND(letters, cross)
    v5 = andResult.view(root, "vck AND cross")

    notResult = NOT(letters)
    v6 = notResult.view(root, "NOT vck")

    return v1, v2, v3, v4, v5, v6

def testGrey(root):
    """Look at how the pie slices appear for a test card with all the
    possible grey tones."""

    # Make a greyscale test card: a 16x16 square going from black to white
    t = open("testcard.pgm", "wb")
    t.write("P5\n16 16\n255\n")
    for i in range(256):
        t.write(chr(i))
    t.close()

    plaintext = Image.open("testcard.pgm")
    plaintext.convert("L")

    mx,my = plaintext.size
    pad = moonfield(size=(mx,my))
    pad.randomFill()
    v1 = pad.view(root, "random junk")

    ciphertext = pad.imageComplement(plaintext)
    v2 = ciphertext.view(root, "ciphertext")

    v3 = ciphertext.view(root, "decrypted ciphertext")
    pad.renderOnCanvas(v3.canvas())
    return v1, v2, v3

def testSplitImage(root):
    """Split a monochrome image into two shares and write these to two
    files that can be viewed externally."""

    s1, s2 = splitImage("vck.tif")
    v = OR(s1, s2).view(root)
    return v

def testSplitImageG(root):
    """Split a greyscale image into two shares (postscript files)."""

    p, c, v1, v2 = splitImageG(root, "guido.tif")
    p.renderOnCanvas(v2.canvas())
    v2.psprint("guido-decrypted.ps")
    return v2

if __name__ == "__main__":
#    mainApp(testBooleanOps)
    mainApp(testEncryptDecrypt)
#    mainApp(testAllIntermediateValues)
#    mainApp(testGrey)
#    mainApp(testSplitImage)
#    mainApp(testSplitImageG)
