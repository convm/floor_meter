import pandas as pd
from guizero import App, Text, PushButton
from datetime import datetime
from configparser import ConfigParser

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

def update_timestamp(floor, reading, df, ground_distance, angle):
    ground_distance[0] -= 1
    floor.value = get_floor(df, ground_distance[0])
    reading.value = u'{}m {}\N{DEGREE SIGN}'.format(ground_distance[0], angle)
    
def close_app():
    app.destroy()

text1, text2, text3, text4 = read_config()
df = read_building()
ground_distance = [df.ceil_ground_distance.iloc[-1]+10]  # Dummy variable
    
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

app.repeat(500, update_timestamp, [floor, reading, df, ground_distance, 2])
app.tk.attributes("-fullscreen", True)
app.display()