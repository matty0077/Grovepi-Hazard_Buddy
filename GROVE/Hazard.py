'''the updated code with some more polish and detail and the EXSense function
that scans and alerts. a sort of continuous safety scanner'''


import sys
sys.path.append("/home/pi/Desktop/NAVI/SPIRIT/GROVE/LOGIKA")
from grove_rgb_lcd import *
import os
import math
import decimal
import grovepi
from grovepi import *
import random
import time

# Connect the Grove Moisture Sensor to analog port A0
# SIG,NC,VCC,GND
moisture_sensor = 2
#///////rotary SIG,NC,VCC,GND a1
potentiometer = 1
# Connect the Grove Sound Sensor to analog port A0
sound_sensor = 0
threshold_value = 400
#gas leaks a1
MQ9_gas_sensor = 2
# Air Quality  A0 #700+ is dangerous, 400 med, below 300 may as well be fresh#////////////air quality NOTE: # Wait 2 minutes for the sensor to heat-up
air_sensor = 0

#barometer  12c
import hp206c
bar= hp206c.hp206c()
#sun 12c
import SI1145
sensor = SI1145.SI1145()

#temp  d7
dht_sensor_port = 8		# Connect the DHt sensor to port d7
dht_sensor_type = 0             # change this depending on your sensor type - see header comment
#pir d3
motion_sensor=3
#ultrasonac d56
ultrasonic_sensor=5#and 6
#collision d2
collision_sensor = 2
#flame d8
flame_sensor = 4#shares ycable with temp
# Connect the Grove Touch Sensor to digital port D4
touch_sensor = 4
grovepi.pinMode(touch_sensor,"INPUT")
# Connect the Grove Buzzer to digital port D8
buzzer = 6
# The electromagnet can hold a 1KG weight
# Connect the Grove Electromagnet to digital port D4
electromagnet = 6
#mosfet
mosfet =7

class Hazard():
    MAIN=True
    TIMER=0
#//////////////////////////lcd display
    def message(self,message,color):
        MODE=0
        for c in range(0,255):
            if color=='green':
                setRGB(255-c,255,255-c)
            elif color=='gray':
                setRGB(c,c,c)
            elif color=='black':
                setRGB(0,0,0)
            elif color=='teal':
                setRGB(0,0-c,255-c)
            elif color=='magenta':
                setRGB(255,255-c,255)
            elif color=='yellow':
                setRGB(255,255,255-c)
            elif color=='white':
                setRGB(255,255,255)
            elif color=='blak2':
                setRGB(155,155,155)
            elif color=='blue':
                setRGB(255-c,255-c,255)
            elif color=='red':
                setRGB(255,255-c,255-c)
            elif color=='grayblu':
                setRGB(55,55,55)
            else:
                #for i in range(0,51):
                setRGB(random.randint(0,255),random.randint(0,255),random.randint(0,255))
                #time.sleep(.1)
                
        MODE=random.randint(0,0)
        if MODE==0:
            setText(message)

        if MODE==1: 
            for i in range(0,12):
                setText(message[:i])
                time.sleep(.03)
        
        if MODE==2:
            buf=list(message)
            setText("".join(buf))
            time.sleep(.05)
            for i in range(len(buf)):
                    buf[i]="."
                    setText_norefresh("".join(buf))
                    time.sleep(.1)

#///////////////////////buzzer
    def Buzzer(self):
        grovepi.pinMode(buzzer,"OUTPUT")
        try:
            # Buzz for 1 second
            grovepi.digitalWrite(buzzer,1)
            time.sleep(1)
            # Stop buzzing for 1 second and repeat
            grovepi.digitalWrite(buzzer,0)

        except KeyboardInterrupt:
            grovepi.digitalWrite(buzzer,0)
        except IOError:
            grovepi.digitalWrite(buzzer,0)
            print ("Error")
            self.message("Error",'red')
            self.Amain()
#/////////////////////////////air quality
    def airval(self):
        grovepi.pinMode(air_sensor,"INPUT")
        grovepi.pinMode(mosfet,"OUTPUT")

        if self.TIMER>0:
            try:
                air_value = grovepi.analogRead(air_sensor)
                if air_value>=0 and air_value<350:#green if air clean
                    self.message("clean air "+str(air_value),'green')

                elif air_value>=350 and air_value<650:#grey if air polluted
                    grovepi.analogWrite(mosfet,128)#255 max speed
                    self.message("dirty air "+str(air_value),'grey')

                elif air_value>=650:#black if airs getting dangerous
                    grovepi.analogWrite(mosfet,255)
                    self.message("dangerous air levels "+str(air_value),'black')
                else:
                    grovepi.analogWrite(mosfet,0)
   
                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
                    
            except IOError:
                grovepi.analogWrite(mosfet,0)
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()
            
  #///////////////////////gas
    def gasval(self):
        grovepi.pinMode(MQ9_gas_sensor,"INPUT")
        grovepi.pinMode(mosfet,"OUTPUT")

        if self.TIMER>0:
            try:
                gas_value = grovepi.analogRead(MQ9_gas_sensor)
                if gas_value>=350 and gas_value<650:#grey if some gas
                    grovepi.analogWrite(mosfet,128)
                    self.message("gas levels stronger"+str(gas_value),'gray')

                elif gas_value>=650:#black if saturated in gas
                    grovepi.analogWrite(mosfet,255)
                    self.message("gas level source"+str(gas_value),'black')
                else:
                    grovepi.analogWrite(mosfet,0)

                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
                    
            except IOError:
                grovepi.analogWrite(mosfet,0)
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()

#///////////////////////////////air pressure/alt
    def pressureval(self):#
        while True:
            try:
                altitude=bar.ReadAltitude()
                pressure=bar.ReadPressure()
                if pressure>=0 and pressure<350:#green if air clean
                    self.message("standard air pressure"+ str(pressure)+str(altitude)+'above sea level','green')
                    
                elif pressure>=350 and pressure<900:#green if air clean
                    self.message("hard air pressure"+ str(pressure)+str(altitude)+'above sea level',gray)

                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

#/////////////////////sun
    def sunval(self):
        if self.TIMER>0:
            try:
                vis = sensor.readVisible()
                IR = sensor.readIR()
                UV = sensor.readUV()
                uvIndex = UV / 100.0
                print('Vis:             ' + str(vis))
                print('IR:              ' + str(IR))
                print('UV Index:        ' + str(uvIndex))
                
                #visible light levels
                if self.MAIN==True:
                    if vis>=0 and vis <10:
                            self.message("night time " + str(vis),'magenta')
                    if vis >=10 and vis<=265:
                            self.message("natural/indoor " + str(vis),'white') 
                    if vis>265 and vis < 500:
                            self.message("nice day" + str(vis),'yellow')
                time.sleep(1)
                #ultraviolet levels   
                if uvIndex>0 and uvIndex<3:
                        self.message("safe uv levels " + str(uvIndex),'green')
                if uvIndex>=3 and uvIndex <6:
                        self.message("recommend sunscreen or hat " + str(uvIndex),'yellow')
                if uvIndex >=6 and uvIndex<8:
                        self.message("less than 30 min till sunburn protect yourself " + str(uvIndex),'red') 
                if uvIndex >=10:
                        self.message("less than 15 min till sunburn protect yourself " + str(uvIndex),'white') 

                time.sleep(1)
                #infrared index(ghost hunting tool?)
                if self.MAIN==True:
                    if IR>=0:
                            self.message("sunny " + str(IR),'yellow')
                    if IR>=0 and IR <10:
                            self.message("night time " + str(IR),'magenta')
                    if IR >=10 and IR<=265:
                            self.message("natural/indoor " + str(IR),'white') 
                    if IR>265 and IR < 500:
                            self.message("nice day " + str(IR),'yellow')
                    if IR>500:
                            self.message("sunny " + str(IR),'yellow')
                            
                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()

##///////////////////////////////////temp humid
    def temphumidval(self):#add time, date
        while True:
            try:
                [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)		#Get the temperature and Humidity from the DHT sensor
                #print("temp =", str(temp *1.8+32), "C\thumidity =", hum,"%") 	
                t = str(temp *1.8+32)
                h = str(hum)
                setText("Temp: " + t + "F")
                for i in t:
                    for c in range(0,255):
                        setRGB(255,255-c,255-c)
                time.sleep(.5)
                setText("Humidity :" + h + "%")
                for u in h:
                    for c in range(0,255):
                        setRGB(255-c,255,255-c)
                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except (IOError,TypeError) as e:
                self.Buzzer()
                print("Error")
                self.message("Error",'red')
                self.Amain()

#//////////////////////////////moisture sensor
    def moisture(self):
        while True:
            try:
                soil=grovepi.analogRead(moisture_sensor)
                #print(str(soil))
                time.sleep(.5)
                if soil==0:
                    self.message("dry as a bone " +str(soil),'black')
                elif soil>0 and soil<300:
                    self.message("not enough moisture "+str(soil),'yellow')
                elif soil>375 and soil<600:
                    self.message("perfect planting conditions "+str(soil),'green')
                elif soil>600 and soil<690:
                    self.message("higher moisture "+str(soil),'teal')
                elif soil>=690:
                    self.message("water source "+str(soil),'blue')
                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except KeyboardInterrupt:
                break
                self.Amain()
            except IOError:
                print ("Error")
                self.message("Error",'red')
                self.Amain()
            
#////////////////////////motion
    def motionval(self):
        grovepi.pinMode(motion_sensor,"INPUT")
        if self.TIMER>0:
            try:
                motion_value = grovepi.digitalRead(motion_sensor)
                if motion_value == 1:#teal lcd if motion detected
                    self.message("motion detected",'teal')
                    self.Buzzer()
                else:
                    self.message("scanning for life",'white')
                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()
                
        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()
            
#//////////////////////ranger
    def rangerval(self):#add buzzer frequency if edge=true
        grovepi.pinMode(ultrasonic_sensor,"INPUT")
        if self.TIMER>0:
            try:
                sonic_value = grovepi.ultrasonicRead(ultrasonic_sensor)
                if sonic_value>0 and sonic_value<75: 
                    self.message("Too close!! "+str(sonic_value),'white')

                elif sonic_value>=75 and sonic_value<175:
                    self.message("pretty close.."+str(sonic_value),'gray')

                elif sonic_value>=175:
                    self.message("safe!! "+str(sonic_value),'green')
                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()
            
#///////////////////////////feur
    def fireval(self):
        grovepi.pinMode(flame_sensor,"INPUT")
        if self.TIMER>0:
            try:
                flame_value = grovepi.digitalRead(flame_sensor)
                if flame_value == 1:
                    self.message("fire!",'red')
                    self.Buzzer()
                    time.sleep(1)
                else:
                    self.message("searching for fire",'teal')
                if grovepi.digitalRead(touch_sensor)==1:
                    self.Amain()
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()
                
        if self.TIMER<=0:
            if self.MAIN==True:
                self.Amain()
            else:
                self.EXSense()

#//////////////////////mosfet
    def Mosfet(self):
        pwr=0
        grovepi.pinMode(mosfet,"OUTPUT")
        while True:
            try:
                if grovepi.digitalRead(touch_sensor)==1:
                    pwr=+1
                    if pwr>2:
                        pwr=0
                # Full speed
                if pwr==2:
                    grovepi.analogWrite(mosfet,255)
                    self.message ("full speed",'green')

                # Half speed
                if pwr==1:
                    grovepi.analogWrite(mosfet,128)
                    self.message ("half speed",'teal')

                # Off
                if pwr==0:
                    grovepi.analogWrite(mosfet,0)
                    self.message ("off",'red')
                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except KeyboardInterrupt:
                grovepi.analogWrite(mosfet,0)
                break
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

#///////////////////////////////sound sensor
    def soundval(self):
        grovepi.pinMode(sound_sensor,"INPUT")
        while True:
            try:
                # Read the sound level
                sensor_value = grovepi.analogRead(sound_sensor)

                # If loud, illuminate LED, otherwise dim
                if sensor_value > threshold_value:
                    self.message('loud noise detected','random')
                    #grovepi.digitalWrite(led,1)
                else:
                    #grovepi.digitalWrite(led,0)
                    self.message('quiet','black')
                #print("sensor_value = %d" %sensor_value)
                time.sleep(.5)
                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

#////////////////////////////////electromagnet
    def emagnet(self):
        pwr=0
        grovepi.pinMode(electromagnet,"OUTPUT")
        while True:
            try:
                if grovepi.digitalRead(touch_sensor)==1:
                    pwr=+1
                    if pwr>1:
                        pwr=0
                # Switch on electromagnet
                if pwr==1:
                    grovepi.digitalWrite(electromagnet,1)
                    self.message ("on",'white')

                # Switch off electromagnet
                elif pwr==0:
                    grovepi.digitalWrite(electromagnet,0)
                    self.message ("off",'black')
                if grovepi.digitalRead(touch_sensor)==1:
                    break
                    self.Amain()

            except KeyboardInterrupt:
                grovepi.digitalWrite(electromagnet,0)
                break
                self.Amain()
            except IOError:
                grovepi.digitalWrite(electromagnet,0)
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                self.Amain()

#//////////////////////////////////////////spidey sense
    def EXSense(self):
        self.MAIN=False
        self.TIMER=60
        while True:
            total=[self.sunval,self.gasval,self.airval,self.fireval,self.rangerval,self.motionval]
            SCAN=random.randint(0,len(total)-1)
            total[int(SCAN)]()

#///////////////////////////////////////////rotary
    def Amain(self):#for menu options and adjusting output levels brightness sensitivity etc
        # Reference voltage of ADC is 5v
        grovepi.pinMode(potentiometer,"INPUT")
        #grovepi.pinMode(collision_sensor,"INPUT")
        adc_ref = 5
        # Vcc of the grove interface is normally 5v
        grove_vcc = 5
        # Full value of the rotary angle is 300 degrees, as per it's specs (0 to 300)
        full_angle = 300
        self.MAIN=True
        self.TIMER=9000
        SLOT=0
        collection=[self.temphumidval,self.sunval,self.moisture,self.pressureval,self.gasval,self.airval,self.fireval,self.rangerval,self.motionval,self.soundval,self.emagnet,self.Mosfet,self.EXSense]
        while True:
            try:
                #collision_value = grovepi.digitalRead(collision_sensor)
                # Read sensor value from potentiometer
                sensor_value = grovepi.analogRead(potentiometer)
                # Calculate voltage
                voltage = round((float)(sensor_value) * adc_ref / 1023, 2)

                # Calculate rotation in degrees (0 to 300)
                degrees = round((voltage * full_angle) / grove_vcc, 2)

                # Calculate LED brightess (0 to 255) from degrees (0 to 300)
                power = int(degrees / full_angle * 255)

                if degrees>0 and degrees<20:
                    SLOT=0
                    self.message("Temp/Humid",'grayblu')
                elif degrees>20 and degrees<40:
                    SLOT=1
                    self.message("sunshine",'yellow')
                elif degrees>40 and degrees<60:
                    SLOT=2
                    self.message("soil moisture",'teal')
                elif degrees>60 and degrees<80:
                    SLOT=3
                    self.message("air pressure-altitude",'grayblu')
                elif degrees>80 and degrees<100:
                    SLOT=4
                    self.message("harmful gases",'magenta')
                elif degrees>120 and degrees<140:
                    SLOT=5
                    self.message("air quality",'white')
                elif degrees>140 and degrees<160:
                    SLOT=6
                    self.message("fire detection",'red')
                elif degrees>160 and degrees<180:
                    SLOT=7
                    self.message("directed sonar",'teal')
                elif degrees>180 and degrees<200:
                    SLOT=8
                    self.message("motion detection",'teal')
                elif degrees>200 and degrees<220:
                    SLOT=9
                    self.message("sound check",'black')
                elif degrees>220 and degrees<240:
                    SLOT=10
                    self.message("electro magnet",'yellow')
                elif degrees>240 and degrees<260:
                    SLOT=11
                    self.message("mosfet",'green')
                elif degrees>265 and degrees<285:
                    SLOT=12
                    self.message("Spidey-Sense",'yellow')
                    
                '''elif collision_value == 0:#yellow lcd if collision detected
                    setText("ouch!")
                    for c in range(0,255):
                        setRGB(255,155-c,255-c)'''
                        
                if grovepi.digitalRead(touch_sensor)==1:
                    collection[int(SLOT)]()
                print("sensor_value = %d voltage = %.2f degrees = %.1f power = %d" %(sensor_value, voltage, degrees, power))
            except KeyboardInterrupt:
                self.message("exiting",'random')
                sys.exit()
                break
            except IOError:
                self.Buzzer()
                print ("Error")
                self.message("Error",'red')
                sys.exit()
            
H=Hazard()
H.Amain()

#work mode drills
# def date time/buzzer alarm
