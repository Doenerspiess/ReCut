######## MP3 SLICER########

import sys
import pydub 
import numpy as np
import audio2numpy as a2n
import ffmpeg
import time
import gc
import tkinter as tk
import tkinter.filedialog
import tkinter.simpledialog

##### IMPORTANT: If you run this code, you have to add FFMPEG to Path first!####

fenster = tk.Tk()
fenster.title("MP3 Slicer")
fenster.geometry("920x450")
file = ""
directory = ""

def read(f, normalized=False):
    """MP3 to numpy array"""
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        framerate = a.frame_rate
        del a
        gc.collect()
        return framerate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y

def write(f, sr, x, normalized=False):
    """numpy array to MP3"""
    channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
    if normalized:  # normalized array - each item should be a float in [-1, 1)
        y = np.int16(x * 2 ** 15)
    else:
        y = np.int16(x)
    song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
    song.export(f, format="mp3", bitrate="320k")

def goToNextPause(arr):
    global act
    start = act
    act = act+min_length
    if act > length:
        return -1, -1
    c = 0
    while c < 1:
        while np.any(x[int(act)]):
            if act + (sr/20) < length:
                act = act+ (sr/20)
            else:
                c = 3
                end = act
                break
        counter1 = 0
        while np.any(x[int(act)]) == 0:
            counter1 = counter1 + int(sr/1000)
            if act + sr/1000 < length:
                act = act+ int(sr/1000)
            else:
                c = 4
                end = act
                break
        if counter1 > sr/10:
            c = 2
            end = act
    return start, end


def start():
    global act
    global length
    global sr
    global x
    global min_length
    global warning

    if file == "":
        warning.config(text = "SELECT A MP3 FILE!")
        return
    elif directory == "":
        warning.config(text = "SELECT A DESTINATION FOLDER!")
        return
    
    warning.config(text = "")
        
    tic = time.time()

    sr, x = read(file.name)

    min_length = int(lengthEntry.get())*sr
    act = 0
    nr = int(nrEntry.get())
    length = x.size/2

    if deleteAds.get() == 1:
        delete_length = min_length
        min_length = 1*sr

    while act<length:
        start, end = goToNextPause(x)
        print(start, end)
        if end != -1:
            if deleteAds.get() == 0:
                write(directory + "\\" + nameEntry.get() +"_"+str(nr)+".mp3", sr, x[int(start):int(end)])
                nr = nr + 1
            elif end-start>delete_length:
                write(directory + "\\" + nameEntry.get() +"_"+str(nr)+".mp3", sr, x[int(start):int(end)])
                nr = nr + 1
            else:
                print("Ad deleted!")
        else:
            break
    IdentifiedTracks = tk.Label(master = fenster, bg = "green", text = "Done! " + str(nr-int(nrEntry.get())) + " Tracks were distinguished")
    IdentifiedTracks.place(x = 55, y = 380, width = 300, height = 30)
    neededTime = tk.Label(master = fenster, bg = "white", text = "Time: " + str(time.time()-tic) + " s")
    neededTime.place(x = 364, y = 380, width = 300, height = 30)


def getFile():
    global file
    file = tkinter.filedialog.askopenfile(mode = "r", title = "Select the MP3 to be cut into tracks", multiple = "False", master = fenster, filetypes = [("mp3", ".mp3")])
    showFile.config(text=file.name)
    warning.config(text = "")


def getDirectory():
    global directory
    directory = tkinter.filedialog.askdirectory(master=fenster)
    showDir.config(text=directory)
    warning.config(text = "")

    
labelName = tk.Label(master = fenster , bg = "white", text = "Name of the resulting MP3's:")
labelName.place(x=55, y=105, width = 300, height = 30)
nameEntry = tk.Entry(bg = "white", master = fenster)
nameEntry.place(x=364, y=105, width = 150, height = 30)
nameEntry.insert(-1, "Track")

labelNr = tk.Label(master = fenster , bg = "white", text = "MP3's will be numbered, start with this number:")
labelNr.place(x=55, y=146, width = 300, height = 30)
nrEntry = tk.Entry(bg = "white", master = fenster)
nrEntry.place(x=364, y=146, width = 150, height = 30)
nrEntry.insert(-1, "1")

labelLength = tk.Label(master = fenster , bg = "white", text = "Minimum length of tracks in s: ")
labelLength.place(x=55, y=187, width = 300, height = 30)
lengthEntry = tk.Entry(bg = "white", master = fenster)
lengthEntry.place(x=364, y=187, width = 150, height = 30)
lengthEntry.insert(-1, "90")

buttonFile = tk.Button(master = fenster, bg="yellow", text = "Select MP3 which should be sliced", command = getFile)
buttonFile.place(x=55, y=25, width = 300, height = 30)
showFile = tk.Label(master = fenster, bg='white', text='')
showFile.place(x=364, y=25, width = 500, height = 30)

buttonDirectory = tk.Button(master = fenster, bg="yellow", text = "Select destination folder", command = getDirectory)
buttonDirectory.place(x=55, y=64, width = 300, height = 30)
showDir = tk.Label(master = fenster, bg='white', text='')
showDir.place(x=364, y=64, width = 500, height = 30)

buttonStart = tk.Button(master = fenster, bg = "green", text = "Start slicing", command = start)
buttonStart.place(x= 250, y = 271, width = 200, height = 100)

buttonQuit =tk.Button(master = fenster, bg = "red", text = "QUIT", command = sys.exit)
buttonQuit.place(x= 500, y = 296, width = 100, height = 50)

warning = tk.Label(master = fenster, text = "", bd = 0, fg = "red")
warning.place(x = 300, y = 400, width = 300, height = 50)

deleteAds = tk.IntVar()
deleteAdsButton = tk.Checkbutton(master = fenster, text = "Delete ads (shorter than minimum track length)", variable = deleteAds)
deleteAdsButton.place(x = 55, y = 228)

fenster.mainloop()






