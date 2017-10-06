#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, signal, subprocess
import pygame
from time import sleep
import qrtools
import RPi.GPIO as GPIO
from KY040 import KY040
#constants  
DATA = 2
CLK = 3
SW = 4
LED = 14 
SLOT = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(SLOT, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

SERVER = "..."
PATH = "..."
USER = "..."
PW = "..."

#Main Class
class blast:
    def __init__(self):
        self.checkForWiFiFile()
        self.ky = KY040(CLK,DATA,SW,self.setVol, self.funcpause)
        self.ky.start()
        self.mplayer = False
        self.volume = 15
        self.mediaFolder = "./media"
        self.currentAlbum = ""
        self.currentAlbumPath = ""
        self.tracks = []
        self.join = os.path.join
        self.ls = os.listdir
        self.pause = False
        self.skipped = False
        self.clock = .2
        self.volstep = 5
        self.noCard = True
        self.rename(self.mediaFolder)
        if GPIO.input(SLOT):
            self.noCard = False
            if self.readQR():
                self.play()
        self.mainloop()
    
    def checkForWiFiFile(self):
        if os.path.isfile("./media/wlan.txt"):
            with open("./media/wlan.txt", "r") as f:
                wlanStr = f.read()
                wlanStrList = wlanStr.split("\n")
                ssid = wlanStrList[0]
                pw = wlanStrList[1]
            os.system("rm ./media/wlan.txt")
            os.system("sudo cp /etc/network/interfaces ./interfaces")
            os.system("sudo cp /etc/wpa_supplicant/wpa_supplicant.conf ./wpa_supplicant.conf")
            
            os.system("sudo chmod 0777 ./interfaces")
            os.system('echo \"iface %s inet dhcp\" >> ./interfaces'%ssid.replace(" ",""))
            os.system("sudo chmod 0644 ./interfaces")
            os.system("sudo cp ./interfaces /etc/network/interfaces")

            os.system("sudo chmod 0777 ./wpa_supplicant.conf")
            lineList = ['network={',
                        'ssid=\"%s\"'%ssid,
                        'psk=\"%s\"'%pw,
                        'id_str=\"%s\"'%ssid.replace(" ",""),
                        '}']
            with open("./wpa_supplicant.conf","a") as f:
                f.write("\n")
                for l in lineList:
                    f.write(l+"\n")
            os.system("sudo chmod 0600 ./wpa_supplicant.conf")
            os.system("sudo cp ./wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf")

    def switchLED(self,on = 0):
        if on:
            GPIO.output(LED,GPIO.HIGH)
        else:
            GPIO.output(LED,GPIO.LOW)
        

    def readQR(self):
        qr=""
        for i in range(5):
            if not GPIO.input(SLOT):
                 return False
                 break
            self.switchLED(on = 1)
            sleep(1)
            os.system("raspistill --timeout 100 --exposure sports -o qr.png")
            self.switchLED()
            decoder = qrtools.QR()
            decoder.decode("qr.png")
            qr=decoder.data
            print qr
            if not qr == "NULL":
                break
        if not qr:
            return False
        else:        
            self.currentAlbum = qr
            self.artist = qr.split(" - ")[0].strip()
            self.album = qr.split(" - ")[1].strip()
            print "Artist: " + self.artist
            print "Album: " + self.album
            self.artistEsc = self.artist.replace(" ", "\ ")
            self.albumEsc = self.album.replace(" ", "\ ")
            self.artistNoWS = self.artist.replace(" ","_")
            self.albumNoWS = self.album.replace(" ","_")
            if not os.path.isdir("./media/%s"%(self.artistNoWS,)):
                os.system("mkdir ./media/%s"%(self.artistNoWS,))
            self.currentAlbumPath = self.join(self.mediaFolder,self.artistNoWS,self.albumNoWS)
            if not os.path.isdir(self.currentAlbumPath):
                try:
                    print "Album not found, trying to download from server."
                    serverStr = USER + "@" + SERVER + ":" + self.join(PATH,self.artistEsc,self.albumEsc)
                    os.system("sshpass -p '%s' scp -r '/%s' ./media/%s"%(PW,serverStr,self.artistNoWS))
                    print "Download successful!"
                    os.rename(os.path.join(self.mediaFolder,self.artistNoWS,self.album),os.path.join(self.mediaFolder,self.artistNoWS,self.albumNoWS))
                    self.rename(self.mediaFolder)
                except:
                    print "Album not found on SD card or on server."
                    return False

            self.tracks = [str(str(track.encode("utf-8"))) for track in self.ls(self.currentAlbumPath) if str(track.encode("utf-8")).lower().endswith(".mp3")]
            self.tracks.sort()
            
            if not os.path.isfile(self.currentAlbum.replace(" ","") + "pl.m3u"):
                with open(self.join(self.currentAlbumPath, "pl.m3u"),"w") as f:
                    for t in self.tracks:
                        f.write(t + "\n")
            
        return True       
    
    def rename(self,dir):
        args = [["ä","ae"],["ö","oe"],["ü","ue"],[" ","_"],["ß","ss"]]
        for f in os.listdir(dir):
            if os.path.isdir(os.path.join(dir,f)) and not f.startswith("."):
                self.rename(os.path.join(dir,f))
            if not f.startswith("."):
                newname = f
                for a in args:
                    newname = newname.replace(*a)
                os.rename(os.path.join(dir,f),os.path.join(dir,newname))
        
    def play(self):
        self.pause = False
        self.playlist = self.join(self.currentAlbumPath,"pl.m3u")#.replace(" ","\\ ")
        self.playlistRep = self.join(self.currentAlbumPath,"pl.m3u").replace(" ","\\ ")
        print "Playlist: " + self.playlist
        print "PlaylistRep: " + repr(self.playlistRep)
        print "After Print"
        if self.mplayer:
            os.system('echo loadlist "%s"> mplayerfifo'%self.playlistRep)
        else:
            self.mplayer = subprocess.Popen(["mplayer","-playlist",self.playlist])
        os.system('echo "set_property volume %d" > mplayerfifo'%self.volume)
        
        
    def mainloop(self):
        counter = 0
        while True:
            if GPIO.input(SLOT):
                if self.tracks:
                    sleep(self.clock)
                    continue
                else:
                    self.cardInserted()
                    sleep(self.clock)
                    continue
            else:
                if not self.noCard:
                    self.cardRemoved()
                sleep(self.clock)
                continue

    def funcpause(self,pin):
        os.system('echo pause > mplayerfifo')
        self.pause = self.pause == False
        
            
    def cardInserted(self):
        self.noCard = False
        if self.readQR():
            self.play()
        
    def cardRemoved(self):
        print "Karte entfernt"
        self.noCard=True
        os.system("echo pause > mplayerfifo")
        
        print("mplayer gestoppt")
        self.currentAlbum = ""
        self.currentAlbumPath = ""
        self.tracks = []
        self.join = os.path.join
        self.ls = os.listdir
        self.currentTrack = None
        self.playing = None
        self.pause = False

    def readVol(self):
        value = os.popen("amixer get PCM|grep -o [0-9]*%|sed 's/%//'").read()
        return int(value)
        
    def setVol(self,direction):
        if self.pause:
            print "Pause festgestellt"
            self.skip(direction)
            return 0
        if direction == 1:
            os.system('echo volume 1 > mplayerfifo')
            self.volume+=1
            self.volume = min(100,self.volume)
        else:
            print "Volume DOWN!"
            os.system('echo volume -1 > mplayerfifo')
            self.volume-=1
            self.volume = max(1,self.volume)

    def skip(self,direction):
        print "Skipping"
        sleep(.5)
        if direction == 1:
            os.system('echo pt_step 1 > mplayerfifo \n echo pause > mplayerfifo')
        else:
            os.system('echo pt_step -1 > mplayerfifo \n echo pause > mplayerfifo')
        
   
test = blast()
