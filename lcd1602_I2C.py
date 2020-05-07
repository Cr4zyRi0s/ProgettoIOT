import i2c

# LCD I2C Interface Address
#ADDRESS = 0x3F
ADDRESS= 0x27
# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit



class i2c_device():

    #Init
    def __init__(self, drvname, addr):
        
        self.port=i2c.I2C(drvname,addr)
        
        self.addr = addr
        try:
            self.port.start()
        except PeripheralError as e:
            print(e)
    
    def write_cmd(self, cmd):
        
        self.port.write(cmd)
        sleep(1)
    
    def __del__(self):
        self.port.stop()


class lcd:
    #initializes objects and lcd
    def __init__(self,drvname):
        
        self.lcd_device = i2c_device(drvname,ADDRESS)
        
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)
        
        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(2)
    
    #destructor
    def __del__(self):
        self.port.__del__()
    
    
    # clocks EN to latch command
    def lcd_strobe(self, data):
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(5)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(1)
    
    def lcd_write_four_bits(self, data):
        
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        
        self.lcd_strobe(data)
    
    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))
    
    # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
    # works!
    def lcd_write_char(self, charvalue, mode=1):
        self.lcd_write_four_bits(mode | (charvalue & 0xF0))
        self.lcd_write_four_bits(mode | ((charvalue << 4) & 0xF0))
    
    
    # put string function
    def lcd_display_string(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
    
        for char in string:
          self.lcd_write(ord(char), Rs)
    
    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)
    
    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state): # for state, 1 = on, 0 = off
        if state == 1:
            self.lcd_device.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.lcd_device.write_cmd(LCD_NOBACKLIGHT)
    
    # add custom characters (0 - 7)
    def lcd_load_custom_chars(self, fontdata):
        self.lcd_write(0x40);
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)         
          
    # define precise positioning (addition from the forum)
    def lcd_display_string_pos(self, string, line, pos):
        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
    
        self.lcd_write(0x80 + pos_new)
    
        for char in string:
            self.lcd_write(ord(char), Rs)




