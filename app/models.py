from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from app import db
from datetime import datetime
from flask_login import UserMixin
import enum


class UserRoleEnum(enum.Enum):
    USER = 1
    ADMIN = 2


class PendingStatus(enum.Enum):
    CHECKIN = 1
    PAID = 2
    CHECKOUT = 3


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phoneNum = Column(String(50), nullable=False)
    email = Column(String(50))
    # Tạo mối quan hệ một-đến-không với Account
    account = relationship('Account', back_populates='user', uselist=False)
    receipts = relationship('Receipt', backref='user', lazy=True)
    bookings = relationship('Booking', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Account(db.Model, UserMixin):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)

    # Tạo mối quan hệ một-đến-không với User
    user = relationship('User', back_populates='account', uselist=False)

    def __str__(self):
        return self.username


# class Category(db.Model):
#     __tablename__ = 'category'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(50), nullable=False, unique=True)
#     products = relationship('Product', backref='category', lazy=True)
#
#     def __str__(self):
#         return self.name

class RoomType(db.Model):
    __tablename__ = 'roomType'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(Float, default=0)
    numBeds = Column(Integer, default=1)
    image = Column(String(100))
    rooms = relationship('Room', backref='roomType', lazy=True)

    def __str__(self):
        return self.name

class Room(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    roomType_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    status = Column(Boolean, default=True)
    bookings = relationship('Booking', backref='room', lazy=True)  # Thêm dòng này
    def __str__(self):
        return self.name


class Booking(db.Model):
    # id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(256), primary_key=True, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)  # Sửa đổi kiểu dữ liệu thành Integer
    startDay = Column(DateTime, default=datetime.now())
    endDay = Column(DateTime, default=datetime.now())
    checkIn_status = Column(Boolean, default=False)
    status = Column(Boolean, default=True)
    # Thêm relationship 1-1 với Receipt
    receipt = relationship('Receipt', back_populates='booking', uselist=False, cascade="all, delete-orphan")

    def __str__(self):
        return self.user_id



# class Product(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(50), nullable=False, unique=True)
#     price = Column(Float, default=0)
#     image = Column(String(100))
#     category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
#     receipt_details = relationship('ReceiptDetails', backref='product', lazy=True)
#     def __str__(self):
#         return self.name


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


class Receipt(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    booking_id = Column(String(256), ForeignKey('booking.id'), nullable=False, unique=True)  # Khóa ngoại và không nullable
    startDay = Column(DateTime)
    numNights = Column(Integer, default=1)
    totalPrice = Column(Float, nullable=False)
    payment_status = Column(Enum(PendingStatus), default=PendingStatus.CHECKIN)

    # Thêm relationship 1-1 với Booking
    booking = relationship('Booking', back_populates='receipt')

    def __str__(self):
        return f"Receipt {self.id}"

    # receipt_details = relationship('ReceiptDetails', backref='receipt', lazy=True)

# class ReceiptDetails(BaseModel):
#     quantity = Column(Integer, default=0)
#     price = Column(Float, default=0)
#     receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
#     product_id = Column(Integer, ForeignKey(Product.id), nullable=False)


if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()

        import hashlib
        u = User(name='Admin',
                 phoneNum='0376624655',
                 email='tvhoang11902@gmail.com')
        db.session.add(u)
        db.session.commit()
        acc = Account(user_id=1,
                 username='admin',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                 user_role=UserRoleEnum.ADMIN)
        db.session.add(acc)
        db.session.commit()
        # c1 = Category(name='Mobile')
        # c2 = Category(name='Tablet')
        #
        # db.session.add(c1)
        # db.session.add(c2)
        # db.session.commit()
        #
        # p1 = Product(name='iPad Pro 2022', price=24000000, category_id=2,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
        # p2 = Product(name='iPhone 13', price=21000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")
        # p3 = Product(name='Galaxy S23', price=24000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
        # p4 = Product(name='Note 22', price=22000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")
        # p5 = Product(name='Galaxy Tab S9', price=24000000, category_id=2,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
        # p6 = Product(name='iPad Pro 2023', price=24000000, category_id=2,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")
        # p7 = Product(name='iPhone 15 Pro', price=21000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
        # p8 = Product(name='Galaxy S24', price=24000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")
        # p9 = Product(name='Note 23 Pro', price=22000000, category_id=1,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
        # p10 = Product(name='Galaxy Tab S9 Ultra', price=24000000, category_id=2,
        #              image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")

        rType1 = RoomType(name='Deluxe', price=100000, numBeds=2, image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")
        rType2 = RoomType(name='Luxury', price=140000, numBeds=1, image="https://res.cloudinary.com/dxxwcby8l/image/upload/v1691062682/tkeflqgroeil781yplxt.jpg")

        r1 = Room(name='101', roomType_id=2)
        r2 = Room(name='102', roomType_id=2)
        r3 = Room(name='103', roomType_id=2)
        r4 = Room(name='201', roomType_id=1)
        r5 = Room(name='202', roomType_id=1)
        r6 = Room(name='203', roomType_id=1)

        b1 = Booking(user_id='1', id='213123123',room_id=1)
        b2 = Booking(user_id='1', id='21313886',room_id=2)
        b3 = Booking(user_id='1', id='21314533123',room_id=3)

        db.session.add_all([rType1, rType2])
        db.session.add_all([r1, r2, r3, r4, r5, r6])

        # db.session.add_all([p1, p2, p3, p4, p5])
        # db.session.add_all([p6, p7, p8, p9, p10])

        db.session.commit()
        db.session.add_all([b1, b2, b3])

        db.session.commit()






