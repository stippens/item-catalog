#--SQLAlchemy imports to make the database work properly------------------------------------------------------
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

#--Imports to make Authentication work properly---------------------------------------------------------------
# from passlib.apps import custom_app_context as pwd_context
# import random, string
# from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	name = Column(String(250))
	email = Column(String(250))
	picture = Column(String(250))

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'      : self.id,
			'name'    : self.name,
			'email'   : self.email,
			'picture' : self.picture,
		}

class Media(Base):
	__tablename__ = 'media'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	urlname = Column(String(250), nullable=False)
	description = Column(String(500))
	media_type = Column(String(100))
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'          : self.id,
			'name'        : self.name,
			'description' : self.description,
			'media_type'  : self.media_type,
		}


engine = create_engine('sqlite:///mediaCatalog.db')
Base.metadata.create_all(engine)
