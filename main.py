# Membrane switch
# Created at 2020-04-28 15:28:37.207189
from servo import servo
import timers
import streams 
import pwm

from hcsr04 import hcsr04
import lcd
import avoidance

streams.serial()

DISTANZA_APERTURA_PORTA = 5.0

PORTA_SERVO_APERTO = 90
PORTA_SERVO_CHIUSO = 0

SERRATURA_SERVO_APERTO = 90
SERRATURA_SERVO_CHIUSO = 0

TEMPO_SERRATURA_CHIUSURA = 10.0
TEMPO_PORTA_CHIUSURA = 10.0
TEMPO_TASTIERINO_INSERIMENTO = 5.0



state = 0

#Flags
access = False
tempo_serratura_finito = False
tempo_porta_finito = False

display=lcd.SmartDoorLCD(I2C0)
'''
portaServo = servo.Servo(D19.PWM,500,2500,2350,20000)
portaServo.attach()
'''
serraturaServo = servo.Servo(D19.PWM,500,2500,2350,20000)
serraturaServo.attach()

#ultrasonic = hcsr04(triggerpin, echopin)
distanzaUltraSonic = 0.0
#thread(thread_ultrasonic())


timer_tastierino = timers.timer()
timer_serratura = timers.timer()
timer_porta = timers.timer()


#Setup tastierino
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
        if distanzaUltraSonic >= DISTANZA_APERTURA_PORTA:
            impostaStatoTre()
        else:
            impostaStatoUno()
        return
    elif state == 1:
        if access:
            impostaStatoDue()
            return
    elif state == 2:
        if tempo_serratura_finito:
            global tempo_serratura_finito = False
            impostaStatoUno()
            return
        if distanzaUltraSonic >= DISTANZA_APERTURA_PORTA:
            impostaStatoTre()
            return
    elif state == 3:
        if tempo_porta_finito:
            global tempo_porta_finito = False
            impostaStatoQuattro()
            return
    elif state == 4:
        if distanzaUltraSonic < DISTANZA_APERTURA_PORTA:
            impostaStatoUno()

def clearBuffer():
    global s
    print("Resetto buffer")
    s=""

def codice_corretto():
    print("Codice corretto")
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
                timer_tastierino.one_shot(TEMPO_TASTIERINO_INSERIMENTO,clearBuffer)
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

def thread_ultrasonic():
    while True:
        global distanzaUltraSonic = ultrasonic.getDistanceCM()

def notifica_tempo_serratura():
    global tempo_serratura_finito = True

def notifica_tempo_porta():
    global tempo_porta_finito = True

def impostaStatoUno():
    state = 1
    
    display.display_password_prompt()
    serraturaServo.moveToDegree(SERRATURA_SERVO_CHIUSO)
    #portaServo.moveToDegree(PORTA_SERVO_CHIUSO)
    
def impostaStatoDue():
    state = 2
    
    display.display_access(1)
    serraturaServo.moveToDegree(SERRATURA_SERVO_APERTO)
    timer_serratura.one_shot(TEMPO_SERRATURA_CHIUSURA, notifica_tempo_serratura)
    
def impostaStatoTre():
    state = 3
    timer_porta.one_shot(TEMPO_PORTA_CHIUSURA,notifica_tempo_porta)

def impostaStatoQuattro():
    state = 4
    portaServo.moveToDegree(PORTA_SERVO_CHIUSO)
    
    
    
    


