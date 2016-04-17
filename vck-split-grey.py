#$Id: vck-split-grey.py,v 1.1 1998/11/04 01:41:53 fms Exp $
# This file is part of the vck distribution: get the rest from
# http://www.cl.cam.ac.uk/~fms27/vck/

import vck
import sys
import os

def quit(msg=""):
    print "USAGE: python %s mypicture.tif\n Error: %s.\n" % (sys.argv[0], msg)
    sys.exit()

try:
    filename = sys.argv[1]
except:
    quit("missing filename")

basename, ext = os.path.splitext(filename)
if ext == "":
    quit("Filename has no extension")
    
def doit(root, image=filename, base=basename):
    # The function you pass to mainApp, which takes care of all the Tkinter
    # black magic, must take "root" (Tk's root window) as a parameter. It
    # must also return a tuple with all the windows it created.

    s1, s2, w1, w2 = vck.splitImageG(
        root, filename, base + "_1.ps", base + "_2.ps")
    wBoth = s1.view(root)
    s2.renderOnCanvas(wBoth.canvas())
    return w1, w2, wBoth
    
vck.mainApp(doit)


