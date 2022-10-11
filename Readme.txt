I'm writing a python script to record and cut longer MP3 files (i.e. recordings of several songs) into the individual tracks. 

It's a rather simple program with a very non-polished GUI so far. Feel free to use it and report any problems that occur. 

There are two ways to use this program: 

The first option is to record audio directly inside the program. Make sure to select the correct audio output of your PC to record from.
This is simply the speaker you are hearing the output from, be it the integrated speaker or headphones.
Then you can record the audio and stop the recording whenever you want (the master volume of your speaker or device doesn't matter here,
it can also be muted, but make sure the program you record from, i.e. YouTube, outputs audio to your PC). Resuming a stopped recording 
is not possible (yet).

The second option is to slice an already existing MP3-File. You can select any MP3-recording you want from your PC, but be aware that 
i.e. live recordings don't work, because there needs to be at least a short amount of complete silence between the songs or parts 
of audio you want to separate.

The final step is identical for both ways: Select the destination folder, Track names, starting number and minimum track length 
and click the "start slicing" button. It can, depending on the length of the recording and the PC, take from a few seconds up to an hour.
Then, you will get a message about the number of cut tracks, which means the program ran successfully! 

The maximum length of the input MP3 is, to my knowledge, slightly above five hours. 
I suspect that RAM is the limiting factor, so if you have more than 8 GB of RAM, longer input files may work, too. The maximum recording time 
if you choose to record inside the program might be shorter.


Further plans are to improve the GUI and usability, and hopefully reduce the filesize of the program.


If you have python and choose to run the program directly from the .py-code instead from the .exe, be aware that you have to have all the
used modules installed, i.e. using pip install. 
Also, it is necessary that you have ffmpeg installed and added to your path. For windows, this is how you do it:
https://windowsloop.com/install-ffmpeg-windows-10/
If you don't have ffmpeg installed, the code won't run! 
Also, add the ffmpeg, ffplay and ffprobe - files you obtain by downloading and installing ffmpeg to the folder the .py-file of ReCut is in (if you donwload the .zip-folder from the release, those files are already included).
