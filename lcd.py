import lcd1602_I2C

class SmartDoorLCD:
    
    lcd = None
    
    def __init__(self,address):
        self.lcd = lcd1602_I2C.lcd(address) 
    
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
    
    def display_clear(self):
        self.lcd.lcd_clear()

    
