from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Robot(Base):
    __tablename__ = "core_robot"

    id = Column(Integer, primary_key=True, index=True)
    ipaddr = Column(String(16), nullable=False)
    token = Column(String(16), nullable=True)
    is_connected = Column(Boolean, default=False, nullable=True)
    first_connect = Column(Date, nullable=True)
    manual_manage = Column(Boolean, default=False)

    # Relationships
    sensor = relationship("Sensor", back_populates="robot", cascade="all, delete-orphan")
    battery = relationship("Battery", back_populates="robot", cascade="all, delete-orphan")
    distance = relationship("Distance", back_populates="robot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Robot(id={self.id}, token={self.token})>"

