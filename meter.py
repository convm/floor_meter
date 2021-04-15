import os
import psutil
from datetime import datetime
from time import sleep
from configparser import ConfigParser

import serial
import pandas as pd

from guizero import App, Box, Text, PushButton, Picture
from PIL import Image

def find_data_usb():
    file_exists = lambda directory, filename : os.path.exists(os.path.join(directory, filename))
    config_exists = lambda d : file_exists('config.txt')
    building_exists = lambda d : file_exists('building.csv')
    
    drives = [d.mountpoint for d in psutil.disk_partitions()]
    for d in drives: 
        if config_exists(d) and building_exists(d): return d
    return None

def read_config(drive): 
    path = os.path.join(drive, 'config.txt')
    config = ConfigParser()
    config.read(path)
    config.sections()
    header = config['Main']['header']
    footer = config['Main']['footer']
    return (header, footer)
    
def read_building(drive):
    path = os.path.join(drive, 'building.csv')
    df = pd.read_csv(path)
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

def read_single(ser):
    s = ser.write(b'\xAE\xA7\x04\x00\x05\x09\xBC\xBE')
    line = ser.readline() 
    if (line == b'\xAE\xA7\x04\x00\x05\x89\xBC\xBE'):
        return None
    else:
        dist = int.from_bytes(line[7:9], byteorder='big') / 10
        return dist

def update_meter(floor, reading, df, ser):
    ground_distance = read_single(ser)
    if ground_distance != None:
        floor.value = get_floor(df, ground_distance)
        reading.value = u'{}m'.format(ground_distance)
    else:
        floor.value = 'N/A'
        reading.value = 'N/A'
        
def build_app_body(app, header_text, footer_text, df, ser):
    
    yl = Image.open("yl_logo.jfif")
    yl.thumbnail((300, 150), Image.ANTIALIAS)
    
    omatic = Image.open('omatic_logo.jpg')
    omatic.thumbnail((150,150), Image.ANTIALIAS)
    
    box = Box(app, layout='grid')
    picture = Picture(box, image=yl, grid=[0,0])
    picture = Picture(box, image=omatic, grid=[1,0])
    
    box = Box(app, layout='grid')
    header = Text(box, text=header_text, size=20, align='top', grid=[0,0])
    floor = Text(box, text="--/F", size=60, color='green', grid=[0,1])
    reading = Text(box, text="--M", size=20, color='green', grid=[0,2])
    footer = Text(box, text=footer_text, size=20, grid=[0,3])

    app.repeat(1200, update_meter, [floor, reading, df, ser])
    app.tk.attributes("-fullscreen", True)
    
    return app

def build_app():
    valid = True
    app = App(bg='white')
    drive = find_data_usb()
    
    if drive is None:
        Text(app, 'Data USB Not Found')
        valid = False
    else:
        try:
            header, footer = read_config(drive)
        except:
            valid = False
            Text(app, 'Config File Not Valid')
            
        try:
            df = read_building(drive)
        except:
            valid = False
            Text(app, 'Building File Not Found')

        try:
            ser = serial.Serial('COM3', 9600, timeout=1)
        except:
            Text(app, 'Laser Not Ready')
            valid = False
    
    if valid: app = build_app_body(app, header, footer, df, ser)
    app.display()
    
build_app()