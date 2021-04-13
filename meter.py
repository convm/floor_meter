import pandas as pd
from guizero import App, Text, PushButton
from datetime import datetime
from configparser import ConfigParser
import serial
from time import sleep

def read_config(): 
    config = ConfigParser()
    config.read('Display.txt')
    config.sections()
    text1 = config['Main']['text1']
    text2 = config['Main']['text2']
    text3 = config['Main']['text3']
    text4 = config['Main']['text4']
    return (text1, text2, text3, text4)
    
def read_building():
    df = pd.read_csv('building.csv')
    cum_height = 0
    ceil_ground_distances = []
    
    for x in df.Height:
        cum_height += x
        ceil_ground_distances.append(cum_height)

    df['ceil_ground_distance'] = ceil_ground_distances  
    return df

def get_floor(df, current_ground_distance):
    floor = '?/F'
    for i, x in df.iterrows():
        if current_ground_distance <= x.ceil_ground_distance:
            return x.Floor
    return floor

def now_string():
    return datetime.now().strftime("%d-%b-%Y, %H:%M:%S")

def read_single(ser):
    s = ser.write(b'\xAE\xA7\x04\x00\x05\x09\xBC\xBE')
    line = ser.readline() 
    if (line == b'\xAE\xA7\x04\x00\x05\x89\xBC\xBE'):
        return None
    else:
        dist = int.from_bytes(line[7:9], byteorder='big') / 10
        return dist

def update_timestamp(floor, reading, df):
    ground_distance = read_single(ser)
    if ground_distance != None:
        floor.value = get_floor(df, ground_distance)
        reading.value = u'{}m'.format(ground_distance)
    else:
        floor.value = 'N/A'
        reading.value = 'N/A'
    
def close_app():
    ser.close()
    app.destroy()

text1, text2, text3, text4 = read_config()
df = read_building()
    
app = App()
Text(app)
building_name = Text(app, text=text1, size=20)
if text2: label2 = Text(app, text=text2)

floor = Text(app, text="---", size=80, color='green')
reading = Text(app, text="--- --", size=40, color='green')
Text(app)
remark1 = Text(app, text=text3)
if text4: remark2 = Text(app, text=text4)
Text(app)
close = PushButton(app, command=close_app, text='Close')

app.repeat(1500, update_timestamp, [floor, reading, df])
app.tk.attributes("-fullscreen", True)

ser = serial.Serial('COM3', 9600, timeout=1)

app.display()