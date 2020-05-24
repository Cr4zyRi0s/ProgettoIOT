# Membrane switch
# Created at 2020-04-28 15:28:37.207189
import timers
import streams 
from servo import servo
import pwm
import lcd
import avoidance

streams.serial()

state = 0

access = False

display=lcd.SmartDoorLCD(I2C0)
'''
portaServo = servo.Servo(D19.PWM,500,2500,2350,20000)
portaServo.attach()
'''
serraturaServo = servo.Servo(D19.PWM,500,2500,2350,20000)
serraturaServo.attach()

ultrasonic = 

echo_timer=timers.timer()

s=""
password="1234"
keymap =[
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
    ]
rows=[D23,D22,D21,D5]
columns=[D16,D4,D0,D2]

#Setup Buzzer
pin_buzzer=D13
pinMode(pin_buzzer,OUTPUT)


    
def buffer():
    global s
    print("Resetto buffer")
    s=""

def codice_corretto():
    print("Codice corretto")
    
    display.display_access(1)
    #Sblocco serratura
    serraturaServo.moveToDegree(90)
    #Suono apertura corretta
    pwm.write(pin_buzzer,2000,1000,MICROS)
    sleep(500)
    pwm.write(pin_buzzer,0,0,MICROS)

def codice_errato():
    print("Codice errato")
    display.display_access(0)
    pwm.write(pin_buzzer,10000,5000,MICROS)
    sleep(500)
    pwm.write(pin_buzzer,0,0,MICROS)
    sleep(2000)
    display.display_clear()

def leggi_tastierino():
    checktastierino=False
    for j in range (4):
        digitalWrite(columns[j], LOW)
        for i in range (4):
            if (digitalRead(rows[i])== LOW):
                while (digitalRead(rows[i])==LOW):
                    sleep(1)
                #display.display_password_update(len(s))
                echo_timer.one_shot(5000,buffer)
                if(keymap[i][j]=='#'):
                    print("Stringa inviata:",s)
                    if(s==password):
                        codice_corretto()
                        checktastierino=True
                    else:
                        codice_errato()
                        checktastierino=False
                    s=""
                else:
                    if(keymap[i][j]=='C'):
                       x=len(s)
                       s=s[0:x-1]
                    else:
                       s+=keymap[i][j]
                    print (s)
        digitalWrite(columns[j], HIGH)
    return checktastierino

for j in range (4):
    pinMode(columns[j],OUTPUT)
    digitalWrite(columns[j],HIGH)
for i in range (4):
    pinMode(rows[i],INPUT_PULLUP)
    digitalWrite(rows[i],HIGH)
    
while True:
    if state == 0:
        pass
    elif state == 1:
        access = leggi_tastierino()
    elif state == 2:
        pass
    elif state == 3:
        pass
    elif state == 4:
        pass
    checkTransizioni()
    

def checkTransizioni():
    if state == 0:
        pass
    elif state == 1:
        if access:
            state = 2
            return
    elif state == 2:
        pass
    elif state == 3:
        pass
    elif state == 4:
        pass










