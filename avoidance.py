class AvoidanceSensor:
    def __init__(self, pin, debug_mode = False):
        self.pin = pin
        self.debug_mode = debug_mode
        self.obstacle = False
        pinMode(pin,INPUT)
    
    def update(self):
        pin_read = digitalRead(self.pin)
        if(pin_read == HIGH):
            if (self.debug_mode):
                print("Ostacolo non rilevato.")
            self.obstacle = False
        else:
            if(self.debug_mode):
                print("ostacolo rilevato")
            self.obstacle = True
            
