from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Battery(Base):
    __tablename__ = "core_battery"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("core_robot.id"), nullable=False)
    battery_num = Column(Integer, nullable=True)

    # Relationship
    robot = relationship("Robot", back_populates="battery")

    __table_args__ = (
        CheckConstraint('battery_num >= 0 AND battery_num <= 100', name='check_battery_range'),
    )

    def __repr__(self):
        return f"<Battery(id={self.id}, robot_id={self.robot_id}, battery_num={self.battery_num})>"

