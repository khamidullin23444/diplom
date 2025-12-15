from enum import IntEnum


class SensorTypeEnum(IntEnum):
    LEFT = 0
    PRIMARY = 1
    RIGHT = 2

    @classmethod
    def choices(cls):
        return (
            (cls.LEFT.value, 'Левый борт'),
            (cls.PRIMARY.value, 'Передняя часть'),
            (cls.RIGHT.value, 'Правый борт')
        )

