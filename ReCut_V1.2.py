######## MP3 SLICER########

import sounddevice as sd
import os
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
import subprocess
import _winapi

from pydub import AudioSegment
from scipy.io.wavfile import write

import pyaudio
import wave

import soundcard as sc

## SETTINGS ##
RECORD_SECONDS = 0.01 ### Lentgh of one "Recording-Chunk" Several chunks will be combined into the complete recording
MaxRecordTime = 18000 ### Maximum Recording time in Seconds
MaxRecordTime = MaxRecordTime/RECORD_SECONDS ### Comvert into number of partial "Recording-Chunks"
RATE = 96000 ### Samplerate of Recording or converted MP3-File (lower value = faster processing & smaller filesize but lower quality)

##Initiate GUI##

fenster = tk.Tk()
fenster.title("ReCut - record and slice MP3-Files into individual songs")
fenster.geometry("920x650")
file = ""
directory = ""

# WHAT TO DO? Convert MP3 (todo = 0) into songs or record directly (todo = 1)? ##

#set up parameters:

todo = 0
recording = 0
data=[]
FORMAT = pyaudio.paInt16
CHANNELS = 2
#WAVE_OUTPUT_FILENAME = "output.wav"
recording = False    
recNr = 0






def read(f, normalized=False):
    print("reading....")
    if todo == 1:
        y = data.reshape((-1, 2))
        y = (y*32768/(y.max())).astype('int')
        return RATE, y
    else:
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
            print(a.frame_rate, y, y.max())
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
    
    AdDeleted = 0

    if file == "" and todo == 0:
        warning.config(text = "SELECT A MP3 FILE!")
        return
    if not np.any(data) and todo == 1:
        warning.config(text = "PLEASE RECORD AUDIO BEFORE TRYING TO CUT IT OR SELECT A PRE-RECORDED MP3-FILE!")
        return
    elif directory == "":
        warning.config(text = "SELECT A DESTINATION FOLDER!")
        return
    
    warning.config(text = "")
        
    tic = time.time()

    if todo == 0:
        TracksSoFar.config(text = "Slicing in progress, reading the MP3-File. This may take a while, depending on the length.")
        fenster.update()
        sr, x = read(file.name)    
    else:
        TracksSoFar.config(text = "Slicing in progress, reading recorded audio. This may take a while, depending on the length.")
        fenster.update()
        sr, x = read("recorded")


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
                TracksSoFar.config(text = "Slicing in progress...   " + str(nr-int(nrEntry.get())) + " Tracks distinguished so far, " + str(AdDeleted) + " Ads deleted.")
                fenster.update()
            elif end-start>delete_length:
                write(directory + "\\" + nameEntry.get() +"_"+str(nr)+".mp3", sr, x[int(start):int(end)])
                nr = nr + 1
                TracksSoFar.config(text = "Slicing in progress...   " + str(nr-int(nrEntry.get())) + " Tracks distinguished so far, " + str(AdDeleted) + " Ads deleted.")
                fenster.update()
            else:
                AdDeleted = AdDeleted+1
                print("Ad deleted!")
        else:
            break
    TracksSoFar.place_forget()
    IdentifiedTracks = tk.Label(master = fenster, font=("Arial", 13), fg = "blue", text = "Done! " + str(nr-int(nrEntry.get())) + " Tracks were distinguished")
    IdentifiedTracks.place(x = 310, y = 585, width = 300, height = 20)
    neededTime = tk.Label(master = fenster, font=("Arial", 9), text = "Time: " + str(time.time()-tic) + " s")
    neededTime.place(x = 310, y = 605, width = 300, height = 20)


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

def switchToRecord():
    global recNr
    global todo
    global speakers
    global default_speaker
    global mics
    global default_mic
    global data
    todo = 1
    buttonRecord.configure(bg = "green")
    buttonMp3.configure(bg = "grey")

    buttonStartRecording.place(x=55, y=130, width = 150, height = 50)
    buttonStopRecording.place(x=250, y=130, width = 150, height = 50)
    buttonFile.place_forget()
    showFile.place_forget()

    
    available_outputs.place(x=55, y=190, width = 150, height = 50)
    
    # get a list of all speakers:
    speakers = sc.all_speakers()
    # get the current default speaker on your system:
    default_speaker = sc.default_speaker()

    # get a list of all microphones:v
    mics = sc.all_microphones(include_loopback=True)
    # get the current default microphone on your system:
    default_mic = mics[0]

    # make a list to select a different mic, if needed:
    for i in range(len(mics)):
        listbox.insert(i, mics[i].name)
    listbox.place(x=250, y=190, width = 400, height = 50)

    for i in range(len(mics)):
        try:
            print(f"{i}: {mics[i].name}")
        except Exception as e:
            print(e)

    while recording == False:
        fenster.update()
        if listbox.curselection():
            default_mic = mics[listbox.curselection()[0]]

    with default_mic.recorder(samplerate=RATE, blocksize = RECORD_SECONDS*RATE*2) as mic, \
                    default_speaker.player(samplerate=RATE) as sp:        

    ### MAIN RECORDING LOOP ###
        while True:
            if recNr % 100 == 0:
                fenster.update()
                if todo == 0:
                    break
            if recording and recNr < MaxRecordTime:
                bit = mic.record(numframes=int(RECORD_SECONDS*RATE))
                data.append(bit)
                recNr+=1
            elif recording == False and recNr > 0:
                print("Done recording!")
                data = np.stack(data)
                #print(data)
                break
            

def switchToMp3():
    global todo
    todo = 0
    buttonMp3.configure(bg = "green")
    buttonRecord.configure(bg = "grey")
    buttonStartRecording.place_forget()
    buttonStopRecording.place_forget()
    listbox.place_forget()
    available_outputs.place_forget()
    
    buttonFile.place(x=540, y=150, width = 300, height = 30)
    showFile.place(x=540, y=200, width = 300, height = 30)

def stopRecording():
    global recording
    if recording:
        buttonStopRecording.configure(bg = "grey", text = "Done Recording!")
        buttonStartRecording.place_forget()
        recording = False

def startRecording():
    global recording
    buttonStartRecording.configure(bg = "grey", text = "recording...")
    recording = True




labelType = tk.Label(master = fenster,  font=("Arial", 14), text = "Do you want to record audio now or use an existing .mp3-file?")
labelType.place(x=110, y=20, width = 700, height = 30)

buttonRecord = tk.Button(master = fenster, font=("Arial", 13), bg = "grey", text = "Record Audio now", command = switchToRecord)
buttonRecord.place(x=80, y=70, width = 300, height = 50)
buttonMp3 = tk.Button(master = fenster, font=("Arial", 13), bg="grey", text = "Slice pre-recorded Mp3", command = switchToMp3)
buttonMp3.place(x=540, y=70, width = 300, height = 50)

buttonStartRecording = tk.Button(master = fenster, bg = "green", text = "Start Recording", command=startRecording)
#buttonStartRecording.place(x=55, y=150, width = 200, height = 50)
buttonStopRecording = tk.Button(master = fenster, bg = "red", text = "Stop Recording", command=stopRecording)
#buttonStopRecording.place(x=540, y=150, width = 200, height = 50)
    
labelName = tk.Label(master = fenster, font=("Arial", 11), text = "Name of the resulting MP3's:")
labelName.place(x=55, y=305, width = 300, height = 30)
nameEntry = tk.Entry(bg = "white", master = fenster)
nameEntry.place(x=364, y=305, width = 150, height = 30)
nameEntry.insert(-1, "Track")

labelNr = tk.Label(master = fenster , font=("Arial", 11), text = "MP3s will be numbered, start with this number:")
labelNr.place(x=55, y=346, width = 300, height = 30)
nrEntry = tk.Entry(bg = "white", master = fenster)
nrEntry.place(x=364, y=346, width = 150, height = 30)
nrEntry.insert(-1, "1")

labelLength = tk.Label(master = fenster,  font=("Arial", 11), text = "Minimum length of tracks in s: ")
labelLength.place(x=55, y=387, width = 300, height = 30)
lengthEntry = tk.Entry(bg = "white", master = fenster)
lengthEntry.place(x=364, y=387, width = 150, height = 30)
lengthEntry.insert(-1, "90")

buttonFile = tk.Button(master = fenster,  font=("Arial", 11), bg="yellow", text = "Select MP3 which should be sliced", command = getFile)
#buttonFile.place(x=540, y=150, width = 300, height = 30)
showFile = tk.Label(master = fenster, bg='white', text='')
#showFile.place(x=540, y=200, width = 300, height = 30)

buttonDirectory = tk.Button(master = fenster,  font=("Arial", 11), bg="yellow", text = "Select destination folder", command = getDirectory)
buttonDirectory.place(x=55, y=264, width = 300, height = 30)
showDir = tk.Label(master = fenster, bg='white', text='')
showDir.place(x=364, y=264, width = 500, height = 30)

buttonStart = tk.Button(master = fenster, font=("Arial", 13), bg = "green", text = "Start slicing", command = start)
buttonStart.place(x= 240, y = 471, width = 200, height = 100)

buttonQuit =tk.Button(master = fenster, font=("Arial", 13), bg = "red", text = "QUIT", command = sys.exit)
buttonQuit.place(x= 480, y = 496, width = 100, height = 50)

warning = tk.Label(master = fenster, font=("Arial", 14), text = "", bd = 0, fg = "red")
warning.place(x = 10, y = 600, width = 900, height = 50)

deleteAds = tk.IntVar()
deleteAdsButton = tk.Checkbutton(master = fenster, font=("Arial", 11), text = "Delete ads (shorter than minimum track length)", variable = deleteAds)
deleteAdsButton.place(x = 55, y = 428)


available_outputs = tk.Label(master = fenster, text = "Available Sound outputs \n (default is the first option):")
listbox = tk.Listbox(master=fenster, width=40, height=10, selectmode="SINGLE")

TracksSoFar = tk.Label(master = fenster, font=("Arial", 11), fg = "blue", text = "")
TracksSoFar.place(x = 110, y = 585, width = 700, height = 20)

fenster.mainloop()












