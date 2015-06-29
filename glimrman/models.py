import sqlalchemy
from sqlalchemy import Column, Integer, Float, String, Text, Boolean, Date, DateTime, Time, ForeignKey, Table, Enum, \
                       ForeignKeyConstraint, UniqueConstraint, Index, \
                       func, and_, or_
from sqlalchemy.orm import relationship, backref, join, object_session, remote, foreign, validates, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Track(Base):
    '''
    Single song on Spotify
    '''
    __tablename__ = 'spotify_tracks'

    id = Column(String(length=150), 
                primary_key=True)  # Base-62 spotify ID

    artist = Column(String(length=255), 
                    nullable=False)

    name = Column(String(length=255), 
                  nullable=False)

    duration_ms = Column(Integer)

    is_active = Column(Boolean, 
                       default=True)

    added_at = Column(DateTime, 
                      nullable=False, 
                      default=func.current_timestamp())

    # ratings

    @hybrid_property
    def rating(self):
        if len(self.ratings) == 0:
            return 0
        else:
            return reduce(lambda accum, r: accum + r.rating, self.ratings, 0.0) / len(self.ratings)

    # @rating.expression
    # def rating(cls):
    #     return func.avg(TrackRating.rating)


class TrackRating(Base):
    '''
    User rating for a track
    '''
    __tablename__ = 'spotify_track_ratings'

    id = Column(Integer, primary_key=True)

    track_id = Column(String(length=150), 
                      ForeignKey(Track.id))
    track = relationship(Track, backref='ratings')

    rating = Column(Integer, nullable=False)

    rated_at = Column(DateTime, 
                      nullable=False, 
                      default=func.current_timestamp())

    rated_by_id = Column(String)  # Luma user ID


