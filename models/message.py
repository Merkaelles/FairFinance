from models import db
from sqlalchemy import ForeignKey
from datetime import datetime


class Message(db.Model):
    __tablename__ = 'message_box'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    sender = db.Column(db.String(64), comment='发送者')
    receiverID = db.Column(db.BIGINT, comment='接受者ID')
    read_state = db.Column(db.Integer, comment='已读', default=0)
    content_id = db.Column(db.BIGINT, ForeignKey('message_content.id'), comment='消息盒子')
    content = db.relationship('Message_Content', backref=db.backref('in_box', lazy=True))


class Message_Content(db.Model):
    __tablename__ = 'message_content'
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), comment='消息标题')
    content = db.Column(db.String(200), comment='消息内容')
    send_time = db.Column(db.DateTime, default=datetime.now(), comment='发送时间')
