# Membrane switch
# Created at 2020-04-28 15:28:37.207189
from servo import servo
import timers
import streams 
import pwm

import hcsr04
#import lcd
import avoidance

from mqtt import mqtt
from wireless import wifi
from espressif.esp32net import esp32wifi as wifi_driver

wifi_driver.auto_init()
streams.serial()

LOCK_PASSWORD="1234"

MQTT_NOME_CLIENT = "esp32device"
MQTT_WIFI_SSID = "ESP32Hotspot"
MQTT_WIFI_PASSWORD = "putroccola"
MQTT_BROKER_SERVICE = "test.mosquitto.org"#"broker.hivemq.com"

DISTANZA_APERTURA_PORTA = 5.0

PORTA_SERVO_APERTO = 90
PORTA_SERVO_CHIUSO = 0

SERRATURA_SERVO_APERTO = 90
SERRATURA_SERVO_CHIUSO = 0

TEMPO_SERRATURA_CHIUSURA = 10000
TEMPO_PORTA_CHIUSURA = 10000
TEMPO_TASTIERINO_INSERIMENTO = 5000

state = 0

#Flags
access_granted = False
lock_requested = False
tempo_serratura_finito = False
tempo_porta_finito = False

#display=lcd.SmartDoorLCD(I2C0)

#serraturaServo = servo.Servo(D4.PWM,500,2500,800,20000)
#serraturaServo.attach()
pwm.write(D4.PWM,20000,2000,MICROS)
pwm.write(D14.PWM,20000,1000,MICROS)
#portaServo = servo.Servo(D14.PWM,500,2500,2350,20000)
#portaServo.attach()

ultrasonic = hcsr04.hcsr04(D15, D2)
distanzaUltraSonic = 0.0

avoidance = avoidance.AvoidanceSensor(D0)

timer_tastierino = timers.timer()
timer_serratura = timers.timer()
timer_porta = timers.timer()


#Setup tastierino
s=""
keymap =[
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
    ]
rows=[D23,D22,D21,D19]
columns=[D18,D5,D17,D16]

#Setup Buzzer
pin_buzzer=D27


def impostaStatoUno():
    print("Passaggio di stato: " + str(state) + " -> 1" )
    global access_granted
    global state
    global lock_requested
    
    state = 1
    access_granted = False
    lock_requested = False
    
    #display.display_password_prompt()
    pwm.write(D4.PWM,20000,2000,MICROS)
    #portaServo.moveToDegree(PORTA_SERVO_APERTO)
    
def impostaStatoDue():
    print("Passaggio di stato: " + str(state) + " -> 2" )
    global state
    timer_tastierino.clear()
    state = 2
    
    display.display_access(1)
    pwm.write(D4.PWM,20000,1000,MICROS)
    timer_serratura.one_shot(TEMPO_SERRATURA_CHIUSURA, notifica_tempo_serratura)
    
def impostaStatoTre():
    print("Passaggio di stato: " + str(state) + " -> 3" )
    portaServo=pwm.write(D14.PWM,20000,300,MICROS)
    global state
    state = 3
    
    pwm.write(D4.PWM,20000,1000,MICROS)
    timer_porta.one_shot(TEMPO_PORTA_CHIUSURA,notifica_tempo_porta)

def impostaStatoQuattro():
    print("Passaggio di stato: " + str(state) + "  -> 4" )
    global lock_requested
    global state
    
    state = 4
    lock_requested = False
    
    display.display_door_closing()
    pwm.write(D14.PWM,20000,1000,MICROS)

def notifica_tempo_serratura():
    print("Tempo serratura esaurito")
    global tempo_serratura_finito
    tempo_serratura_finito = True
    
def notifica_tempo_porta():
    print("Tempo porta esaurito")
    global tempo_porta_finito
    tempo_porta_finito = True

def checkTransizioni():
    if state == 0:
        print(distanzaUltraSonic)
        if distanzaUltraSonic >= DISTANZA_APERTURA_PORTA:
            impostaStatoTre()
        else:
            impostaStatoUno()
        return
    elif state == 1:
        if access_granted:
            impostaStatoDue()
            return
    elif state == 2:
        if tempo_serratura_finito:
            tempo_serratura_finito = False
            impostaStatoUno()
            return
        if distanzaUltraSonic >= DISTANZA_APERTURA_PORTA:
            timer_serratura.clear()
            impostaStatoTre()
            return
        if lock_requested:
            timer_serratura.clear()
            impostaStatoUno()
            return
    elif state == 3:
        if tempo_porta_finito:
            tempo_porta_finito = False
            impostaStatoQuattro()
            return
        if lock_requested:
            timer_porta.clear()
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
    global access_granted
    access_granted = True
    print("Codice corretto")
    #Suono apertura corretta
    pwm.write(pin_buzzer,2000,1000,MICROS)
    sleep(500)
    pwm.write(pin_buzzer,0,0,MICROS)
    

def codice_errato():
    print("Codice errato")
    #display.display_access(0)
    pwm.write(pin_buzzer,10000,5000,MICROS)
    sleep(500)
    pwm.write(pin_buzzer,0,0,MICROS)
    sleep(2000)
    #display.display_clear()

def leggi_tastierino():
    while True:
        for j in range (4):
            digitalWrite(columns[j], LOW)
            for i in range (4):
                if (digitalRead(rows[i])== LOW):
                    while (digitalRead(rows[i])==LOW):
                        sleep(1)
                    timer_tastierino.one_shot(TEMPO_TASTIERINO_INSERIMENTO,clearBuffer)
                    if(keymap[i][j]=='#'):
                        print("Stringa inviata:",s)
                        if(s==LOCK_PASSWORD):
                            codice_corretto()
                            return True
                        else:
                            codice_errato()
                        s=""
                    else:
                        if(keymap[i][j]=='C'):
                            x=len(s)
                            s=s[0:x-1]
                        else:
                            s+=keymap[i][j] 
                        print (s)
                        #display.display_password_update(len(s))
            digitalWrite(columns[j], HIGH)

def mqtt_on_message(client, data):
    print("Received MQTT Message")
    message = data["message"]
    if message.topic == "unlock" and state == 1:
        print("Unlock message:\t" + message.payload)
        if message.payload == LOCK_PASSWORD:
            access_granted = True
    elif message.topic == "lock" and (state == 2 or state == 3):
        print("Lock message:\t" + message.payload)
        lock_requested = True
        
    elif message.topic == "status":
        print("Status message:\t" + message.payload)
        status_string = ""
        if state == 0:
            status_string = "Configurazione."
        if state == 1:
            status_string = "Porta chiusa e Bloccata"
        if state == 2:
            status_string = "Porta chiusa e Sbloccata"
        if state == 3:
            status_string = "Porta Aperta"
        if state == 4:
            status_string = "Porta in Chiusura"
        #state = (state + 1) % 5
        client.publish("status_response", status_string)
        
        '''
def connect_wifi():
    print("Establishing Link...")
    try:
        wifi.link(MQTT_WIFI_SSID,wifi.WIFI_WPA2,MQTT_WIFI_PASSWORD)
    except Exception as e:
        print("Something wrong while linking.", e)

def connect_broker():
    print("Connection to broker")
    try:
        client = mqtt.Client(MQTT_NOME_CLIENT,True)
        for retry in range(10):
            try:
                client.connect(MQTT_BROKER_SERVICE, 60)
                break
            except Exception as e:
                print("Connecting...\t%d" % retry)
        print("Connected.")
        client.subscribe([["unlock",2],["lock",2],["status",2],["status_response",2]]) 
        client.loop(mqtt_on_message)
    except Exception as e:
        print(e)

#CONNESSIONE ALLA RETE WIFI
connect_wifi()

#CONNESSIONE AL BROKER MQTT
connect_broker()
'''

for j in range (4):
    pinMode(columns[j],OUTPUT)
    digitalWrite(columns[j],HIGH)
for i in range (4):
    pinMode(rows[i],INPUT_PULLUP)
    digitalWrite(rows[i],HIGH)

pinMode(pin_buzzer,OUTPUT)


while True:
    global state
    if state == 0:
        global distanzaUltraSonic
        distanzaUltraSonic = ultrasonic.getDistanceCM()
    elif state == 1:
        #print('Sono nello stato 1')
        prova=leggi_tastierino()
    elif state == 2:
        global distanzaUltraSonic
        distanzaUltraSonic = ultrasonic.getDistanceCM()
        #print('Sono nello stato 2')
    elif state == 3:
        avoidance.update()
        #print('Sono nello stato 3')
        if avoidance.obstacle:
            timer_porta.one_shot(TEMPO_PORTA_CHIUSURA, notifica_tempo_porta)
            print('Ostacolo presente')
    elif state == 4:
        #print('Sono nello stato 4')
        pass
    checkTransizioni()




