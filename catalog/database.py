import os
import sys
from sqlalchemy import Column, ForeignKey,  Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    picture = Column(String(150))


class Club(Base):
    __tablename__ = "club"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
            }


class Player(Base):
    __tablename__ = 'player'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    jersey = Column(String(8))
    position = Column(String(250))
    club_id = Column(Integer, ForeignKey('club.id'))
    club = relationship(Club)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'jersey': self.jersey,
            'position': self.position,
            'user_id': self.user_id
            }


engine = create_engine('sqlite:///clubinfo.db')
Base.metadata.create_all(engine)
