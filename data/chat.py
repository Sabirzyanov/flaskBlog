import sqlalchemy
from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chat'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    chat_txt = sqlalchemy.Column(sqlalchemy.String, nullable=False)