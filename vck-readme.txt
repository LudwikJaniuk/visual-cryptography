Visual Cryptography Kit
http://www.cl.cam.ac.uk/~fms27/vck/
(c) 1998 Olivetti Oracle Research Laboratory (ORL)

Written by Frank Stajano,
Olivetti Oracle Research Laboratory <http://www.orl.co.uk/~fms/> and
Cambridge University Computer Laboratory <http://www.cl.cam.ac.uk/~fms27/>.

Visual cryptography concept invented by Moni Naor & Adi Shamir

VCK is copyrighted free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
VCK is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.
You should have received a copy of the GNU General Public License along
with VCK; see the file COPYING.  If not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
USA or, more sensibly, go to their web site at http://www.gnu.org/.

The Python Imaging Library (available from
http://www.pythonware.com/products/pil/ and necessary to use this
module), is Copyright (c) 1995-7 Fredrik Lundh, Copyright (c) 1997-8
Secret Labs AB.  All rights reserved.

------------------------------------------------------------

Visit the VCK home page at http://www.cl.cam.ac.uk/~fms27/vck/ for some
background information. From there, get my poster for a quick introduction
and the original paper by Naor & Shamir for all the theoretical background.

If you don't have them already, get PIL from http://www.pythonware.com/ and
Python from http://www.python.org (or, if you're on win 32, get both in a
convenient precompiled package from Pythonware -- this is what I've used to
develop this module and the only PIL implementation I've ever worked with).


To play around with your own pictures: run 

   python vck-split-mono.py mypicture.tif

to have mypicture.tif (which must be a 1-bit-deep bitmap, but doesn't have
to be tif) split into two bitmap "shares" that will recreate the original
when superimposed. (You must photocopy them onto transparency first.) The
program will not only generate the two shares as files but will also
display them in little windows for you. It will also show a third window
with what you should ideally obtain by overlapping the transparencies.

Note that, due to limitations in the process of photocopying onto
transparency, the best results are obtained with comparatively low
resolution pictures (of the order of 50 pixels across), since these suffer
less from alignment problems.


For greyscale, do

   python vck-split-grey.py mypicture.tif

to have mypicture.tif (which now must be a 256-bit-deep greyscale image,
but again doesn't have to be tif) split into two postscript "shares".


For more experiments (including viewing the intermediate results and so on)
run

    python vck.py

on its own; it will perform one of its many self-tests/demos. To choose
another one, edit the source (you can do this even if you don't speak
Python) and, at the very bottom of vck.py, in the bit that looks like this...

if __name__ == "__main__":
#    mainApp(testBooleanOps)
    mainApp(testEncryptDecrypt)
#    mainApp(testAllIntermediateValues)
#    mainApp(testGrey)
#    mainApp(testSplitImage)
#    mainApp(testSplitImageG)

...add a # to the mainApp line that doesn't have one, and remove it from
another one of your choice. (Be sure NOT to insert any tab characters in
the file or you may regret it.)


To peek under the hood: read the source code, which contains lots of
documentation.

------------------------------------------------------------

I cannot promise updates or new releases of VCK, but I'll still be pleased
to read your comments and ideas. Write to fstajano@orl.co.uk.
