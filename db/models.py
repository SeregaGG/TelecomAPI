from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from .db import Base, DBContext
from sqlalchemy.orm import validates
from sqlalchemy.orm import Session
import re


class EquipmentType(Base):
    __tablename__ = "equipment_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), nullable=False)
    serial_mask = Column(String(50), nullable=False)

    @classmethod
    def get_all_for_response(cls, db: Session):
        equipments: list[EquipmentType] = db.query(cls).all()
        return [{x.id: x.as_dict()} for x in equipments]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_type_id = Column(Integer, ForeignKey("equipment_type.id"), nullable=False)
    serial_number = Column(String(50), nullable=False)
    comment = Column(String(50))
    is_deleted = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('equipment_type_id', 'serial_number'),)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self, db: Session):
        db.add(self)
        db.commit()

    def get(self, db: Session):
        return db.query(self.__class__).filter(self.__class__.id == self.id and self.__class__.is_deleted == False).first()

    def update(self, db: Session, new_data: dict):
        for key, value in new_data.items():
            setattr(self, key, value)
        self.save(db)

    def soft_delete(self, db: Session):
        setattr(self, "is_deleted", True)
        self.save(db)

    @classmethod
    def get_all_for_response(cls, db: Session):
        equipments: list[Equipment] = db.query(cls).filter(cls.is_deleted == False).all()
        return [{x.id: x.as_dict()} for x in equipments]

    @validates('serial_number')
    def validate_sn(self, key, value):
        patterns = {
            "N": r"^[0-9]?",
            "A": r"^[A-Z]?",
            "a": r"^[a-z]?",
            "X": r"^[a-z]?|[0-9]",
            "Z": r"^[-,_,@]?"
        }
        with DBContext() as db:
            equipment_type: EquipmentType = db.query(EquipmentType).filter(EquipmentType.id == self.equipment_type_id).first()
        serial_mask: str = equipment_type.serial_mask

        if len(serial_mask) != len(value):
            raise AssertionError('Different length')

        for char, pattern in zip(value, serial_mask):
            is_invalid = re.fullmatch(patterns.get(pattern), char) is None
            if is_invalid:
                raise AssertionError('Bad serial number')

        return value
