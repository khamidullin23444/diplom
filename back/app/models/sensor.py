from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Sensor(Base):
    __tablename__ = "core_sensor"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("core_robot.id"), nullable=False)
    sensor_type = Column(Integer, nullable=True)
    date_sensor = Column(DateTime, nullable=True)
    value = Column(Integer, nullable=True)

    # Relationship
    robot = relationship("Robot", back_populates="sensor")

    def __repr__(self):
        return f"<Sensor(id={self.id}, robot_id={self.robot_id}, type={self.sensor_type}, value={self.value})>"

