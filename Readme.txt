I'm writing a python script to cut longer MP3 files (i.e. recordings of several songs) into the individual tracks called ReCut. 

So far there are two versions of the program:

First, there is a compiled .exe program which should run on most devices. 
One tiny problem: The .exe is too big to upload it here. I'll see if I can fix this, but until then, I've uploaded it on Google Drive: 
https://drive.google.com/file/d/1tC1vkiggghDv7ikwv2t4MQYxMThKLKNg/view?usp=sharing

There also is a python script version (.py) which you can use if you have a python interpreter installed, and, VERY IMPORTANT, ffmpeg added to your path (for windows, this is how you do it: https://windowsloop.com/install-ffmpeg-windows-10/).


It's a rather simple program with a very non-polished GUI so far. Feel free to use it and report any problems that occur. 

I'm planning to rework the GUI a bit and, if I can do it in a useful way, implement the possibility to record system sound of the computer directly in the program. 
Until then, you'll have to use a program like audacity first to record the original, long MP3.

The maximum length of the input MP3 is, to my knowledge, slightly above five hours. 
I suspect that RAM is the limiting factor, so if you have more than 8 GB of RAM, longer input files may work, too.

