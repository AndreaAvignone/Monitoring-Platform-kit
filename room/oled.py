
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from conf.MyMQTT import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import sys
import json
import requests

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

class OLED():
    def __init__(self,filename,clientID):
        self.temp=0
        self.wind=0
        self.hum=0
        self.pmv=0
        self.PMV="NONE"
        
        self.db_filename=filename
        self.roomContent=json.load(open(self.db_filename,"r"))
        self.room_ID=self.roomContent['room_info']['room_ID']
        self.room_name=self.roomContent['room_info']['room_name']
        self.hubAddress=self.roomContent["hub_catalog"]
        self.clientID=clientID
        
        
    def configuration(self):
        try:
            print("Connecting to Central HUB...")
            time.sleep(1)
            r=requests.get(self.hubAddress+'/hub_ID')
            if r.status_code==200:
                print("Connection performed.")
                self.hub_ID=r.json()
                self.clientID=self.clientID+"_"+self.hub_ID+"_"+self.room_ID
                broker=requests.get(self.hubAddress+'/broker').json()
                self.broker_IP=broker[0].get('IP_address')
                self.broker_port=broker[0].get('port')
                return True
            else:
                print("Central HUB connection failed.\n")
        except IndexError as e:
            print(e)
            print("No Central HUB connection available.\n")
    def run(self):
        self.client=MyMQTT(self.clientID,self.broker_IP,self.broker_port,self)
        self.client.start()
        print('{} has started'.format(self.clientID))
        
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def notify(self,topic,msg):
        try:
            payload=json.loads(msg)
            parameter=payload['parameter']
            value=payload['value']
            unit=payload['unit']
            timestamp=payload['timestamp']
                    
            print(f'{parameter}:{value} {unit} - {timestamp}')
            if(parameter=="temperature"):
                self.temp=round(value,2)
                #self.draw.text((self.x+6, self.top+8),     str("Temp.")+ "   " + str(value)+"°"+unit, font=self.font, fill=255)
            if(parameter=="wind"):
                self.wind=value
            if(parameter=="humidity"):
                self.hum=round(value,2)
                #self.draw.text((self.x+6, self.top+16),    str("Hum.")+ "    " + str(value)+unit,  font=self.font, fill=255)
            if(parameter=="pmv"):
                self.pmv=round(value,2)
                if(value>=-0.5 and value <=0.5):
                    self.PMV="GOOD"
                elif(value<-0.5 and value >=-1.5):
                    self.PMV="COOL"
                elif(value<-1.5):
                    self.PMV="COLD"
                elif(value>-0.5 and value <=1.5):
                    self.PMV="WARM"
                elif(value>1.5):
                    self.PMV="HOT"
                else:
                    self.PMV="NONE"
            self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
            self.draw.text((self.x+6, self.top+8),     str("Temp.")+ "   " + str(self.temp)+"°C", font=self.font, fill=255)
            self.draw.text((self.x+6, self.top+25),    str("Wind")+ "    " + str(self.wind)+" "+"kmH",  font=self.font, fill=255)        
            self.draw.text((self.x+6, self.top),       "PMV:    " +str(self.pmv)+"  "+ str(self.PMV),  font=self.font, fill=255)
            self.draw.text((self.x+6, self.top+16),    str("Hum.")+ "    " + str(self.hum)+"%",  font=self.font, fill=255)
            # Display image.
            self.disp.image(self.image)
            self.disp.display()
            time.sleep(.1)
        except:
            pass
            

    def initializeDisplay(self):
        RST = None     # on the PiOLED this pin isnt used
        # Note the following are only used with SPI:
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()
        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))
        
        self.draw = ImageDraw.Draw(self.image)


        self.draw.rectangle((0,0,width,height), outline=0, fill=0)
        
        padding = -2
        self.top = padding
        self.bottom = height-padding
        
        self.x = 0

        self.font = ImageFont.load_default()

        self.draw.rectangle((0,0,width,height), outline=0, fill=0)
        self.draw.text((self.x+6, self.top+8), "Connecting...", font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(.1)
        
        
if __name__=='__main__':
    
    
    filename=sys.argv[1]
    myOLED=OLED(filename,"DISPLAY")
    myOLED.initializeDisplay()
    if myOLED.configuration():
        myOLED.run()
        time.sleep(1)
        myOLED.follow(myOLED.hub_ID+"/"+myOLED.room_ID+"/#")

    while True:
        time.sleep(3)
    myOLED.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
    myOLED.disp.display()
    myOLED.stop()
