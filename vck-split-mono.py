#$Id: vck-split-mono.py,v 1.2 1998/11/04 01:31:38 fms Exp $
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
    
s1, s2 = vck.splitImage(filename, basename + "_1" + ext, basename + "_2" + ext)

def display(root, share1=s1, share2=s2):
    # The function you pass to mainApp, which takes care of all the Tkinter
    # black magic, must take "root" (Tk's root window) as a parameter. It
    # must also return a tuple with all the windows it created.

    window1 = share1.view(root)
    window2 = share2.view(root)
    result = vck.OR(share1, share2)
    windowResult = result.view(root)
    return window1, window2, windowResult
    
vck.mainApp(display)


