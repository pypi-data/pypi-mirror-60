#! /usr/bin/env python3

# Copyright (c) 2014-2016 Felix Knopf <e01100101@t-online.de>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License in the LICENSE.txt for more details.
#

from os.path import splitext
import kode256
try:
    from .ModifiedMixin import ModifiedMixin
except (ImportError, SystemError):
    from kode256.tool.ModifiedMixin import ModifiedMixin

try:
    from tkinter import *
    from tkinter import filedialog, messagebox
    from PIL import ImageTk
except ImportError:
    raise ImportError("Please ensure, that tkinter and PIL are available")


filetypes = [("Supported Formats",
              "*.bmp *.dib *.gif *.im *.jpg *.jpe *.jpeg *.pcx *.png *.pbm " \
              "*.pgm *.ppm *.tif *.tiff *.xbm *.xpm *.svg"),
             ("All Files", "*") ]

class TextField(ModifiedMixin, Text):
    def __init__(self, *a, **b):
        Text.__init__(self, *a, **b)
        self._init()

    def beenModified(self, event=None):
        cApply()


def updateDisplay():
    global disp, photo
    
    for i in disp.find_all(): disp.delete(i)
    disp.create_image((0,0), image=photo, anchor=NW)
    disp.update_idletasks()

def scaleImage(rawImage):
    global w,h
    
    scaledImage = rawImage
    scaledImage.thumbnail((w*0.3,h*0.1))
    return ImageTk.PhotoImage(scaledImage)  
            
def cApply():
    global result,T,photo,height,thickness,caption,quiet
    
    result = kode256.image(T.get("1.0", 'end-1c'),height.get(),
                           thickness.get(), caption.get(), quiet.get())
    photo = scaleImage(result.convert("RGB"))
    updateDisplay() 
    
def cSave():
    global result,filetypes,height,thickness,caption,quiet
    cApply()
    
    file = filedialog.asksaveasfilename(parent=disp, title="Save Barcode",
                                        filetypes=filetypes)
    ftype = splitext(file)[1]
    if ftype == ".svg":
        with open(file, "w") as f:
            f.write(kode256.svg(T.get("1.0", 'end-1c'),height.get(),
                                thickness.get(), caption.get(), quiet.get()))

    elif ftype in filetypes[0][1][1:].split(" *"):
        result.save(file)
    else: messagebox.showerror("Not Supported",
                               "The image format *%s is not supported!" % ftype)
    

def gui_main(): 
    global w,h,T,disp,height,thickness,caption,quiet
    
    root = Tk()
    root.title("Code128")
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()

    # Barcode Viewer
    disp = Canvas(root, width=w*0.3, height=h*0.1)
    disp.grid(row=0, column=0, padx=20, pady=20, rowspan=4)

    # Info Text
    l1 = Label(root, text="Type the text you want to enconde below.\n\n" \
               "Adapt the height of the generated picture and the width\n" \
               "trough the thickness of a single bar (both in pixel)")
    l1.grid(row=0, column=1, pady=10)

    # Options
    subWnd2 = Frame(root)
    subWnd2.grid(row=1, column=1, padx=30, pady=40)

    height      = IntVar()
    thickness   = IntVar()
    quiet       = IntVar()
    caption     = IntVar()

    eHeight     = Entry(subWnd2, textvariable=height)
    lHeight     = Label(subWnd2, text="height")
    eThickness  = Entry(subWnd2, textvariable=thickness)
    lThickness  = Label(subWnd2, text="thickness")
    chQuiet     = Checkbutton(subWnd2, text="include quiet zone",
                              variable=quiet)
    chCaption   = Checkbutton(subWnd2, text="add caption",
                              variable=caption)
    height.set("100")
    thickness.set("3")
    quiet.set("1")
    caption.set("1")

    lHeight.grid(row=0, column=0)
    eHeight.grid(row=0, column=1)
    lThickness.grid(row=1, column=0)
    eThickness.grid(row=1, column=1)
    chQuiet.grid(row=2, column=0, columnspan=2, sticky=W)
    chCaption.grid(row=3, column=0, columnspan=2, sticky=W)

    # Input Box
    T = TextField(root, width=60, height=8)
    T.grid(row=2, column=1)

    # Control Buttons
    subWnd2 = Frame(root)
    subWnd2.grid(row=3, column=1, padx=30, pady=30)

    bApply  = Button(subWnd2, text="Apply", width=10, command=cApply)
    bSave   = Button(subWnd2, text="Save", width=10, command=cSave)
    bCancel = Button(subWnd2, text="Cancel",width=10,
                     command=lambda: root.destroy()) 

    bApply.grid(column=0, row=0, padx=10)
    bSave.grid(column=1, row=0, padx=10)
    bCancel.grid(column=2, row=0, padx=10)

    root.mainloop()

if __name__ == "__main__": gui_main()
