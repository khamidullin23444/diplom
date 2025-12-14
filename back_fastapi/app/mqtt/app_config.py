import base64
import datetime
import paho.mqtt.client as mqtt
from app.mqtt.service import parse
from app.database import SessionLocal
from app.models import Robot, Sensor, Battery
from app.enums import SensorTypeEnum

# MQTT settings
MQTT_SERVER = '185.152.81.104'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MAIN_TOPIC = 'esp8266/sensor/'


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print("Успешное подключение")
        mqtt_client.subscribe(MAIN_TOPIC)
    else:
        print("Подключение не удалось", rc)


def on_disconnect(mqtt_client, userdata, rc):
    if rc != 0:
        print("Произошло отключение!")


def on_message(mqtt_client, userdata, msg):
    db = SessionLocal()
    try:
        try:
            base64_payload = base64.b64decode(msg.payload).decode('UTF-8')
        except Exception:
            base64_payload = msg.payload.decode('UTF-8')

        if "\r\n" in base64_payload:
            base64_payload = base64_payload.split('\r\n')[0]

        robot_data = parse(base64_payload)
        robot_name = robot_data['name']
        
        if robot_name:
            robot = db.query(Robot).filter(Robot.token == robot_name).first()
            if not robot:
                return
            
            command = robot_data['command']
            print(command)
            
            if 'SEN' in command:
                if "L" in command:
                    sensor_type = SensorTypeEnum.LEFT
                elif "R" in command:
                    sensor_type = SensorTypeEnum.RIGHT
                elif "P" in command:
                    sensor_type = SensorTypeEnum.PRIMARY
                else:
                    return
                    
                sensor = Sensor(
                    robot_id=robot.id,
                    sensor_type=sensor_type.value,
                    value=robot_data['value'],
                    date_sensor=datetime.datetime.now()
                )
                db.add(sensor)
                db.commit()
                
            elif 'BATT' in command:
                battery = db.query(Battery).filter(Battery.robot_id == robot.id).first()
                if battery:
                    battery.battery_num = robot_data['value']
                    db.commit()
                else:
                    # Создаем новую батарею, если её нет
                    battery = Battery(
                        robot_id=robot.id,
                        battery_num=robot_data['value']
                    )
                    db.add(battery)
                    db.commit()
    except Exception as e:
        print(f"Ошибка обработки MQTT сообщения: {e}")
        db.rollback()
    finally:
        db.close()


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_disconnect = on_disconnect
# client.on_message = on_message
# client.connect(
#     host=MQTT_SERVER,
#     port=MQTT_PORT,
#     keepalive=MQTT_KEEPALIVE
# )

