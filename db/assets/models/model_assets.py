from db.base import Base
from sqlalchemy import inspect
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship


class Assets(Base):
    __tablename__ = 'assets'

    id = Column(BigInteger, primary_key= True)
    site = Column(String(3), ForeignKey('sites.site'))
    asset = Column(String(100), unique=True, nullable=False)
    parent = Column(String(100), ForeignKey('assets.asset'), nullable=True)
    path = Column(String(255))
    description = Column(String(255))
    sensors = relationship('Sensors', lazy='dynamic', back_populates='asset_')

    def __init__(self, site, asset, parent=None, description=None, path=None):
        self.site = site
        self.asset = asset
        self.parent = parent
        self.description = description
        if parent==None:
            self.path = path
        else:
            self.path = self.findPath(parent)

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def findPath(self, parent):
        if parent == '':
            return '/'
        else:
            temp = ''
            ancestor = Assets.query.filter_by(asset=parent).first()
            print(ancestor)
            if ancestor.parent != None:
                loop = ancestor.parent.split('/')
                while loop:
                    temp = loop.pop() + temp
                    temp = '/'+temp
                return temp + '/' + parent +'/'
            else:
                return '/' + ancestor.asset

    def __repr__(self):
        return '<id {}>'.format(self.id)