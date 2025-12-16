import json
import os
from datetime import date
from typing import List, Dict
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Robot, Sensor, Battery
from app.enums import SensorTypeEnum

router = APIRouter()

# Настройка Jinja2
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
templates = env


def get_sensor_data(sensors: List[Sensor]) -> List[Dict[str, int]]:
    """Преобразует список сенсоров в формат для графиков"""
    k = 0
    sensor_data = []
    for sensor in reversed(sensors):
        data = {
            "x": k,
            "y": sensor.value
        }
        sensor_data.append(data)
        k += 1
    return sensor_data


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Главная страница со списком роботов"""
    robots_query = db.query(
        Robot.id,
        Robot.token,
        Robot.is_connected,
        Robot.ipaddr,
        Battery.battery_num.label('battery__battery_num')
    ).outerjoin(Battery, Robot.id == Battery.robot_id).all()
    
    robots = []
    for r in robots_query:
        robots.append({
            'id': r.id,
            'token': r.token,
            'is_connected': r.is_connected,
            'ipaddr': r.ipaddr,
            'battery__battery_num': r.battery__battery_num
        })
    
    template = templates.get_template("core/index.html")
    return HTMLResponse(content=template.render(request=request, robots=robots))


@router.get("/robot/{robot_id}", response_class=HTMLResponse)
async def robot(request: Request, robot_id: int, db: Session = Depends(get_db)):
    """Страница детальной информации о роботе"""
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        return RedirectResponse(url="/", status_code=302)
    
    if robot.manual_manage:
        return RedirectResponse(url=f"/robot_bluetooth/{robot_id}", status_code=302)
    
    # Получаем последние 10 записей для каждого типа датчика
    sensor_left = db.query(Sensor).filter(
        Sensor.robot_id == robot_id,
        Sensor.sensor_type == SensorTypeEnum.LEFT.value
    ).order_by(desc(Sensor.date_sensor), desc(Sensor.id)).limit(10).all()
    sensor_left_data = get_sensor_data(sensor_left)
    
    sensor_prim = db.query(Sensor).filter(
        Sensor.robot_id == robot_id,
        Sensor.sensor_type == SensorTypeEnum.PRIMARY.value
    ).order_by(desc(Sensor.date_sensor), desc(Sensor.id)).limit(10).all()
    sensor_prim_data = get_sensor_data(sensor_prim)
    
    sensor_right = db.query(Sensor).filter(
        Sensor.robot_id == robot_id,
        Sensor.sensor_type == SensorTypeEnum.RIGHT.value
    ).order_by(desc(Sensor.date_sensor), desc(Sensor.id)).limit(10).all()
    sensor_right_data = get_sensor_data(sensor_right)
    
    # Получаем батарею
    battery = db.query(Battery).filter(Battery.robot_id == robot_id).first()
    battery_num = battery.battery_num if battery else "Не указано"
    
    template = templates.get_template("core/robot.html")
    return HTMLResponse(content=template.render(
        request=request,
        robot={
            "id": robot.id,
            "token": robot.token,
            "ipaddr": robot.ipaddr,
            "battery__battery_num": battery_num
        },
        sensor_left=json.dumps(sensor_left_data),
        sensor_prim=json.dumps(sensor_prim_data),
        sensor_right=json.dumps(sensor_right_data)
    ))


@router.get("/robot_create/", response_class=HTMLResponse)
async def robot_create_form(request: Request):
    """Форма создания робота"""
    template = templates.get_template("core/create.html")
    return HTMLResponse(content=template.render(request=request))


@router.post("/robot_create/", response_class=RedirectResponse)
async def addrobot(
    ipaddr: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Создание нового робота"""
    robot = Robot(
        ipaddr=ipaddr,
        token=token,
        is_connected=False,
        first_connect=date.today()
    )
    db.add(robot)
    db.commit()
    return RedirectResponse(url="/", status_code=302)


@router.get("/robot_delete/{robot_id}", response_class=RedirectResponse)
async def deleterobot(robot_id: int, db: Session = Depends(get_db)):
    """Удаление робота"""
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if robot:
        db.delete(robot)
        db.commit()
    return RedirectResponse(url="/", status_code=302)


@router.get("/robot_bluetooth/{robot_id}", response_class=HTMLResponse)
async def change_type_robot(request: Request, robot_id: int, db: Session = Depends(get_db)):
    """Переключение робота в режим ручного управления"""
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        return RedirectResponse(url="/", status_code=302)
    
    robot.manual_manage = True
    db.commit()
    
    template = templates.get_template("core/bluetooth.html")
    return HTMLResponse(content=template.render(request=request, robot=robot))


@router.get("/sensor_data/")
async def sensor_data(sensor_type: int, db: Session = Depends(get_db)):
    """API для получения данных датчиков"""
    sensors = db.query(Sensor).filter(
        Sensor.sensor_type == sensor_type
    ).order_by(desc(Sensor.id)).limit(10).all()
    
    sensordata = get_sensor_data(sensors)
    return JSONResponse(content=sensordata)


@router.get("/robot_data/")
async def robot_data(robot: int, db: Session = Depends(get_db)):
    """API для получения данных робота"""
    robot_obj = db.query(Robot).filter(Robot.id == robot).first()
    if not robot_obj:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    battery = db.query(Battery).filter(Battery.robot_id == robot).first()
    battery_num = battery.battery_num if battery else "Не указано"
    
    robot_data_response = {
        'battery': battery_num
    }
    
    return JSONResponse(content=robot_data_response)

@router.get("/analyzer", response_class=HTMLResponse)
async def analyzer_index(request: Request, db: Session = Depends(get_db)):
    template = templates.get_template("core/analyzer.html")

    params = {
        "gain": 2,
        "mc_period": 3,
        "t90_180": 4,
        "pulse_count": 5,
        "accumulations": 6,
    }
    oil = {
        "heavy_density": 1,
        "light_density": 2,
        "heavy_mm": 3,
        "light_mm": 4,
        "viscosity_r2a": 5,
        "viscosity_p2a": 6,
        "c_ac": 7,
        "extra_block_1": 8,
        "extra_block_2": 9,
    }
    relax = {
        "t2a": 1,
        "t2b": 2,
        "t2c": 3,
        "aa": 4,
        "ab": 5,
        "ac": 6,
        "p2a": 7,
        "p2b": 8,
        "p2c": 9,
        "t2eff": 10,
        "t2_oil": 11,
        "t2_water": 12,
        "water_conc": 13,
    }
    power = {
        "p_sply": 1,
        "p_kpmg": 2,
    }
    return HTMLResponse(content=template.render(request=request, params=params, oil=oil, relax=relax, power=power))