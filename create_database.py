from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Media


engine = create_engine('sqlite:///mediaCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#--media for newuser-----------------------------------------------------------
user = User( name="Scott Tippens", email="scott.tippens@gmail.com", picture="")
session.add(user)
session.commit()

media = Media( name="Sekiro", urlname="sekiro", description="Challenging action adventure game.", media_type="video-game", user=user)
session.add(media)
session.commit()

media = Media( name="Candle in the Dark", urlname="candle-in-the-dark", description="Wonderful discussion of human tendencies.", media_type="book", user=user)
session.add(media)
session.commit()

media = Media( name="Dark Souls", urlname="dark-souls", description="Best game series I've ever played.", media_type="video-game", user=user)
session.add(media)
session.commit()


#--media for newuser-----------------------------------------------------------
user = User( name="Sarah Thomens", email="sarah.thomens@gmail.com", picture="")
session.add(user)
session.commit()

media = Media( name="Tangled", urlname="tangled", description="Best animated feature ever!", media_type="movie", user=user)
session.add(media)
session.commit()

media = Media( name="Twilight", urlname="twilight", description="Nice book for a fun afternoon.", media_type="book", user=user)
session.add(media)
session.commit()

media = Media( name="Uprooted", urlname="uprooted", description="Wonderful fantasy advanture story.", media_type="book", user=user)
session.add(media)
session.commit()


print "database updated with new elements!"
