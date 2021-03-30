import pandas as pd
from guizero import App, Text, PushButton
from datetime import datetime

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

def update_timestamp(floor, reading, timestamp, df, ground_distance, angle):
    ground_distance[0] -= 1
    floor.value = get_floor(df, ground_distance[0])
    reading.value = u'{}m {}\N{DEGREE SIGN}'.format(ground_distance[0], angle)
    timestamp.value = now_string()
    
def close_app():
    app.destroy()
    
df = read_building()
ground_distance = [df.ceil_ground_distance.iloc[-1]+10]  # Dummy variable
    
app = App()
building_name = Text(app, text="\nMetro Centre II\n", size=20)

floor = Text(app, text="---", size=80, color='green')
reading = Text(app, text="--- --", size=40, color='green')
Text(app)
timestamp = Text(app, text="Pending to start...", size=20, color='grey')
close = PushButton(app, command=close_app, text='Close')

app.repeat(500, update_timestamp, [floor, reading, timestamp, df, ground_distance, 2])
app.tk.attributes("-fullscreen", True)
app.display()