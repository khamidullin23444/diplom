from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Distance(Base):
    __tablename__ = "core_distance"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("core_robot.id"), nullable=False)
    path = Column(Integer, nullable=True)
    date_distance = Column(DateTime, nullable=True)
    speed = Column(Float, nullable=True)
    direction = Column(String(16), nullable=True)

    # Relationship
    robot = relationship("Robot", back_populates="distance")

    def __repr__(self):
        return f"<Distance(id={self.id}, robot_id={self.robot_id}, path={self.path})>"

