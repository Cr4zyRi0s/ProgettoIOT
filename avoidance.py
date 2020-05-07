#CODICE AVOIDANCE                                                                                                                                                          import streams
streams.serial()




class AvoidanceSensor:
    pin = 0
    obstacle = False
    enabled = True
    
    debug_mode = False
    
    def __init__(self, pin, debug_mode = False):
        self.pin = pin
        self.debug_mode = debug_mode
        pinMode(pin,INPUT)
    
    def update(self,deltaTime):
        if (not self.enabled):
            return
        pin_read =  digitalRead(self.pin)
        if(pin_read == LOW):
            if (self.debug_mode):
                print("Ostacolo non rilevato.")
            obstacle = False
        else:
            if(self.debug_mode):
                print("ostacolo rilevato")
            obstacle = True
            
