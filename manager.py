# intended to manage the Smart Soda Tami5 system system
# insert data to Smart home DB
import paho.mqtt.client as mqtt
import time
import random
from mqtt_init import *
from icecream import ic
from datetime import datetime 

def time_format():
    return f'{datetime.now()}  Manager|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False) # use True for including script file context file  

# Define callback functions
def on_log(client, userdata, level, buf):
        ic("log: "+buf)
            
def on_connect(client, userdata, flags, rc):    
    if rc==0:
        ic("connected OK")                
    else:
        ic("Bad connection Returned code=",rc)
        
def on_disconnect(client, userdata, flags, rc=0):    
    ic("DisConnected result code "+str(rc))
        
def on_message(client, userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    ic("message from: " + topic, m_decode)
    
    ## שתי השורות מתחת קוראות את הכמות סודה והכוסות מההודעה שמתקבלת
    c_weight = float(m_decode.split(' ')[1])
    c_cups = float(m_decode.split(' ')[3])
    
    ## בדיקה על כמות הסודה והכוסות, ומידה והכמות היא מתחת לטרשהולד שהוגדרת, נשלחת ההודעה שהגדרנו למטה
    if c_weight <= soda_weight_trashold or c_cups <= cups_trashold:
        ic("ALERT: LOW ON SODA , Request a new soda canister.. " + m_decode)
        send_msg(client,warning_topic,"ALERT: LOW ON SODA , Request a new soda canister.. " + m_decode)
        

def send_msg(client, topic, message):
    ic("Sending message: " + message)
    #tnow=time.localtime(time.time())
    client.publish(topic,message)   

def client_init(cname):
    r=random.randrange(1,10000000)
    ID=str(cname+str(r+21))
    client = mqtt.Client(ID, clean_session=True) # create new client instance
    # define callback function       
    client.on_connect=on_connect  #bind callback function
    client.on_disconnect=on_disconnect
    client.on_log=on_log
    client.on_message=on_message        
    if username !="":
        client.username_pw_set(username, password)        
    ic("Connecting to broker ",broker_ip)
    client.connect(broker_ip,int(port))     #connect to broker
    return client

def main():
    cname = "Manager-"
    client = client_init(cname)
    # main monitoring loop - כאן האפליקציה מתחילה
    client.loop_start()  # Start loop
    client.subscribe(comm_topic+'5976397/sts')
    
    # הקטע קוד הזה, מונע הריצה ליפול,זה בודק אם החיבור עדיין קיים, אם לא, זה עובר הלאה, והורג את האפליקציה
    try:
        while conn_time==0:
            time.sleep(conn_time+manag_time)
            ic(f"Time for sleep {conn_time+manag_time}")
            time.sleep(3)       
        ic("con_time ending") 
    except KeyboardInterrupt:
        client.disconnect() # disconnect from broker
        ic("interrrupted by keyboard")

    # אם הקוד מגיע לכאן, הריצה מתה
    client.loop_stop()    #Stop loop
    # end session
    client.disconnect() # disconnect from broker
    ic("End manager run script")
if __name__ == '__main__':
    main()
    