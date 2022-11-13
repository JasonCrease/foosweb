from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import INTEGER, TEXT, FLOAT
from sqlalchemy.dialects.sqlite import DATETIME

Base = declarative_base()


class Game(Base):
    __tablename__ = 'game'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    date = Column(DATETIME, nullable=False)
    blue_p1_id = Column(INTEGER, ForeignKey("player.id"), nullable=False)
    blue_p2_id = Column(INTEGER, ForeignKey("player.id"), nullable=False)
    blue_points = Column(INTEGER, nullable=False)
    red_p1_id = Column(INTEGER, ForeignKey("player.id"), nullable=False)
    red_p2_id = Column(INTEGER, ForeignKey("player.id"), nullable=False)
    red_points = Column(INTEGER, nullable=False)
    blue_p1 = relationship("Player", foreign_keys=[blue_p1_id])
    blue_p2 = relationship("Player", foreign_keys=[blue_p2_id])
    red_p1 = relationship("Player", foreign_keys=[red_p1_id])
    red_p2 = relationship("Player", foreign_keys=[red_p2_id])


class Player(Base):
    __tablename__ = 'player'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False)
    rating1 = Column(FLOAT, nullable=True)
