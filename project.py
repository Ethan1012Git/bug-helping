from googlesheet import MicroGoogleSheet
import network, time
from characters import CHARACTER_DATA
from machine import Pin, I2C, ADC, 
import ssd1306
#setup esp32
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

vert = ADC(Pin(32))
horz = ADC(Pin(35))
vert.atten(ADC.ATTN_11DB)
horz.atten(ADC.ATTN_11DB)
button = Pin(17, Pin.IN, Pin.PULL_UP)

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0) 
oled.show()
#connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("", "")

dot = 0
while not wlan.isconnected():
    out = "Wifi Connecting"
    oled.fill(0)
    for i in range(dot):
        out += "."
    oled.text(out, 0, 0)
    oled.show()
    dot += 1
    if dot > 3:
        dot = 0
    time.sleep(0.000000001)
oled.fill(0)
oled.text('Wifi Connected!', 0, 0)
oled.show()

#setup google sheet
oled.fill(0)
oled.text('Setting', 0, 0)
oled.show()
sheet_url = "https://docs.google.com/spreadsheets/d/17avqZetma9QLbLvLJ5j93FUrbQJfYQWe4EVcnU8gg7I/edit#gid=1491347069"
sheet_name = "工作表1"
deploy_id = "AKfycbxSobDGlUoO4YnLB_U_Hs-LUEFSphCGRzW6UJk9YJhT"
ggsheet = MicroGoogleSheet(sheet_url,sheet_name)
ggsheet.set_DeploymentID(deploy_id)
ggsheet.gen_scriptFile()
#print(ggsheet.getCell(1,1))


def draw_character(data, x, y):
    for j in range(16):  # Rows
        for byte_index in range(2):  # Each row has 2 bytes of data
            byte_val = data[j * 2 + byte_index]  # Accessing the right byte
            for i in range(8):  # Bits in a byte
                if byte_val & (1 << (7 - i)):
                    oled.pixel(x + byte_index * 8 + i, y + j, 1) 

def display_text_string(oled, text, start_x=0, start_y=0, spacing=2):
    """Displays a string of characters on the OLED."""
    x_offset = start_x
    for char in text:
        if char in CHARACTER_DATA:
            char = CHARACTER_DATA[char]
            draw_character(char, x_offset, start_y)
            x_offset += 16 + spacing  # Move the x-offset for the next character

def bug_name(row):
    oled.fill(0)
    name = ggsheet.getCell(row,1)
    display_text_string(oled,name,0,0)
    display_text_string(oled,"特性",90,0)
    oled.show()
    return name

def display_title(name,y):
    oled.fill(0)
    if y == 2:
        title = "特性"
    elif y == 3:
        title = "特徵"
    elif y == 4:
        title = "對策"
    display_text_string(oled,name,0,0)
    display_text_string(oled,title,90,0)
    oled.show()
    
def display_info(row,column,name):
    oled.fill(0)
    y = 16
    if column == 2:
        title = "特性"
    elif column == 3:
        title = "特徵"
    elif column == 4:
        title = "對策"
    info = ggsheet.getCell(row,column)
    info_len = len(info)
    if info_len > 7:
        for i in range(0, info_len, 7):
            out = info[i:i+7]
            print(out)
            display_text_string(oled,out,0,y)
            y+=16
    else:
        display_text_string(oled,info,0,16)
    display_text_string(oled,name,0,0)
    display_text_string(oled,title,90,0)
    oled.show()
    
    
press_h = 0
press_v = 0
row = 2
column = 2
name = bug_name(row)
display_info(row,column,name)
while True:
    h = horz.read()
    v = vert.read()
    if h < 1500 and press_h == 0:
        row -= 1
        if row < 2:
            row = 3
        name = bug_name(row)
        display_info(row,column,name)
        press_h = 1
    elif h > 2500 and press_h == 0:
        row += 1
        if row > 3:
            row = 2
        name = bug_name(row)
        display_info(row,column,name)
        press_h = 1
    elif v < 1500 and press_v == 0:
        column -= 1
        if column < 2:
            column = 4
        press_v = 1
        display_info(row,column,name)
    elif v > 2500 and press_h == 0:
        column += 1
        if column > 4:
            column = 2
        press_v = 1
        display_info(row,column,name)
    if h < 2500 and h > 1500 and press_h == 1:
        press_h = 0
    if v < 2500 and v > 1500 and press_v == 1:
        press_v = 0
    
        
        
        

