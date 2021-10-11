# Running battles from Hash IDs

Confused? You should probably watch the [accompanying video](https://www.youtube.com/watch?v=247qD1qulSQ) first.

## Introduction 

These instructions will attempt to walk you through running the project locally so you can watch battles from Hash IDs at your leisure. I've tried to make them as easy to follow as possible, but there are quite a few steps and if you miss anything it won't work. Please ***read all the instructions*** carefully and be prepared to Google things if you have trouble. 

If you're sure you've done everything right and you've exhausted your Google abilities, or especially if you think there's an issue in my instructions, please open a GitHub issue on this project.

## Prerequisites

First off, you'll need **Windows** (probably 10 or 11). The emulator this project uses (BGB) is a Windows executable, so that's out of my hands. You might be able to use Wine on Linux or MacOS, but I can't help you with that. 

Second, install Python 3.8 or newer. You can get Python from python.org or from the Microsoft Store. If you need help, Google how to install Python on Windows. 

Third, with Python installed, use pip to install the Hash ID library. If Python is set up correctly, you should be able to open a Command Prompt and type `pip install hashids`. If that doesn't work, try `python -m pip install hashids`. If that still doesn't work, Google how to install Python libraries with pip on Windows. 

Fourth, install ffmpeg, and make sure it's on your path. [This WikiHow article](https://www.wikihow.com/Install-FFmpeg-on-Windows) seems like a reasonable set of instructions.

Fifth, download BGB version 1.5.8 32 bit. That's no longer the newest version, so you can find a mirror [here](https://emutopia.com/index.php?option=com_cobalt&task=files.download&tmpl=component&id=27384&fid=2&fidx=0&rid=2063&return=aHR0cHM6Ly9lbXV0b3BpYS5jb20vaW5kZXgucGhwL2l0ZW0vMjA2My1iZ2ItMS01LTg%3D). You might be able to get away with a newer version, but I haven't tested them, so you're on your own. 

Sixth, download and install the [CamStudio Lossless codec](https://www.free-codecs.com/download_soft.php?d=a05ef709ad3c01e27214a4e83297821f&s=551&r=&f=camstudio_lossless_codec.htm). If you skip this step, everything will seem to work until it doesn't. 

Lastly, obtain a copy of the ROM image `Pokemon Red (UE) [S][!].gb`. It needs to be that exact version of the game with that exact filename. This shouldn't be hard to do, but since downloading ROMs off the internet is not entirely legal, I can't help you with this step. 

## Setting up the folder structure

First, [download the zip folder for this project](https://github.com/jsettlem/elo_world_pokemon_red/archive/refs/heads/master.zip) (or clone the git repo if you know what you're doing) and extract it somewhere on your computer. By default, the script will also use this as a temporary scratch folder, so maybe don't put it on something like Dropbox or Google Drive that's going to try to sync a bunch of files over the network. 

Put the `Pokemon Red (UE) [S][!].gb` ROM in that folder.

Make a folder called `bgb`, and put `bgb.exe` in there.  

The end result should be a folder structure like this: 

```
elo_world_pokemon_red
├─── bgb
│    └─── bgb.exe
├── Pokemon Red (UE) [S][!].gb
├── battle_x_as_y.py
└── ...a bunch of other files

```

## Run the script

Run `battle_x_as_y.py`. If you've set up Python correctly, you should be able to just double-click on the .py file. If that doesn't work, you can open a command prompt window and run `python battle_x_as_y.py`. If that still doesn't work, Google how to run Python scripts in Windows.

If a window appears and immediately closes when you double-click, that's probably Python erroring out because you didn't install the hashids library correctly. 

If all goes well, the script will run and automatically check most of the dependencies. Read the output carefully, it's there to help you. 

If it doesn't detect any problems, It will prompt you to enter a Hash ID. Type in a Hash ID from the video (space don't matter) and press enter. A bunch of garbage will print out and a few minutes later the battle should be complete. Find the final video file in the `output\movies` folder. 

Windows Media Player seems to struggle with these video files, so consider using VLC or something. 
