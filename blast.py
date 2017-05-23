import os, signal, subprocess
import pygame

#constants  

#Main Class
class blast:
    def __init__(self):
        self.player = pygame.mixer
        self.player.init()
        self.volume = .5
        self.mediaFolder = "./media"
        self.currentAlbum = ""
        self.currentAlbumPath = ""
        self.tracks = []
        self.join = os.path.join
        self.ls = os.listdir
        self.currentTrack = None
        self.playing = None
        self.channel = self.player.Channel(0)
        self.pause = False
        
        self.clock = .2
        self.volstep = .05
        
        if self.readQR():
            self.play()
        self.mainloop()
    
    def readQR(self):
        os.system("echo 1 > /sys/devices/platform/soc/20980000.usb/buspower")
        qr=""
        zbarcam = subprocess.Popen("zbarcam --raw --nodisplay /dev/video0", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        for i in range(5):
            qr=zbarcam.stdout.readline()
            if qrcodetest !="":
                break
        if not qr:
            return False
        else:        
            os.killpg(zbarcam.pid, signal.SIGTERM)
            os.system("echo 0 > /sys/devices/platform/soc/20980000.usb/buspower")
            self.currentAlbum = qr
            self.artist = qr.split("-")[0].strip()
            self.album = qr.split("-")[1].strip()
            self.currentAlbumPath = self.join(self.mediaFolder,self.artist,self.album)
            self.tracks = [self.join(self.currentAlbumPath,track) for track in self.ls(self.currentAlbumPath)) if track.endswith(".mp3")].sort()
            self.currentTrack = 0
        return True       
        
    def play(self):
        self.pause = False
        self.playing = self.player.Sound(self.tracks[self.currentTrack])
        self.channel.set_volume(self.volume)
        self.channel.play(self.playing)
        
    def mainloop(self):
        while True:
            if self.channel.get_busy():
                if not self.channel.get_volume() == self.volume:
                    self.channel.set_volume(self.volume)
                sleep(self.clock)
                continue
            elif self.tracks[]
                if self.currentTrack < len(self.tracks)-1:
                    self.tracks+=1
                    self.play()
                    sleep(self.clock)
                    continue
                else:
                    sleep(self.clock)
                    continue
            else:
                sleep(self.clock)
                continue
    
    def pause(self):
        self.pause = self.pause == False
        if self.pause:
            self.channel.unpause()
        else:
            self.channel.pause()
            
    def cardInserted(self):
        self.readQR()
        self.play()
        
    def cardRemoved(self):
        self.channel.stop()
        self.currentAlbum = ""
        self.currentAlbumPath = ""
        self.tracks = []
        self.join = os.path.join
        self.ls = os.listdir
        self.currentTrack = None
        self.playing = None
        self.pause = False
    
    def volUp(self):
        self.volume += self.volStep
        if self.volume > 1.0:
            volume = 1.0
        self.setVol()
    
    def volDown(self):
        self.volume -= self.volStep
        if self.volume < 0.0:
            self.volume = 0.0
        self.setVol()
            
    def setVol(self):
        self.channel.set_volume(self.volume)
        
   
