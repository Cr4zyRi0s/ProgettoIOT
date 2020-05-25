import lcd1602_I2C

class SmartDoorLCD:
    
    def __init__(self,address):
        self.lcd = lcd1602_I2C.lcd(address) 
        self.seconds = 0
    
    def display_access(self, access_result):
        self.lcd.lcd_clear()
        if access_result == 0:
            self.lcd.lcd_display_string("Accesso Negato",1)
        elif access_result == 1:
            self.lcd.lcd_display_string("Accesso",1)
            self.lcd.lcd_display_string("Consentito",2)
            
    def display_password_prompt(self):
        self.lcd.lcd_clear()
        self.lcd.lcd_display_string("Inserire Codice.",1)
        self.lcd.lcd_display_string("  ->",2)
        
    def display_password_update(self, password_length):
        string = "  ->"
        for i in range(password_length):
            string += "*"
        string += "_"
        self.lcd.lcd_display_string(string,2)
        
    def display_door_closing(self):
        self.lcd.lcd_clear()
        self.lcd.lcd_display_string("Chiusura",1)
        self.lcd.lcd_display_string("Porta",2)
        
    def display_timer(self, seconds):
        if self.seconds == seconds:
            return
        if seconds < 10:
            self.lcd.lcd_display_string_pos("0" + str(seconds), 2, 14)
        else:
            self.lcd.lcd_display_string_pos(str(seconds), 2, 14)
    
    def display_clear(self):
        self.lcd.lcd_clear()

    
