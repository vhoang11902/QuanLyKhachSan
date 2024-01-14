from collections import defaultdict
from datetime import datetime
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, RoomType, Booking, Room, Receipt, Account
from app import app, db
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
import hashlib


def load_roomTypes(id=None, page=None):
    roomTypes = RoomType.query
    if id:
        room = roomTypes.filter(RoomType.id.contains(id))
        return room.first()
    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size
        return roomTypes.slice(start, start + page_size)

    return roomTypes.all()


def get_available_rooms_query(start_date, end_date):
    return (
        db.session.query(Room, RoomType)
        .join(RoomType, RoomType.id == Room.roomType_id)
        .outerjoin(Booking)
        .options(joinedload(Room.roomType))
        .filter(
            or_(
                Booking.id.is_(None),
                and_(
                    or_(
                        Booking.startDay > end_date,
                        Booking.endDay < start_date
                    ),
                    Booking.id.isnot(None)
                )
            )
        )
    )

def get_booking_rooms_query(start_date, end_date):
    return (
        db.session.query(Room, RoomType, Booking)
        .join(RoomType, RoomType.id == Room.roomType_id)
        .join(Booking)
        .options(joinedload(Room.roomType))
        .filter(
            and_(
                or_(
                    and_(Booking.startDay <= end_date, Booking.endDay >= start_date),
                    and_(Booking.startDay >= start_date, Booking.startDay <= end_date),
                    and_(Booking.endDay >= start_date, Booking.endDay <= end_date)
                ),
                Booking.id.isnot(None)
            )
        )
    )


def load_booking(id=None):
    bookings = Booking.query
    if id:
        booking = bookings.get(id)
        return booking
    else:
        return bookings.all()


def load_findRoom(start_date, end_date):
    try:
        checkInDay = datetime.strptime(start_date, '%d/%m/%Y %H:%M')
        checkOutDay = datetime.strptime(end_date, '%d/%m/%Y %H:%M')

        rooms_query = get_available_rooms_query(checkInDay, checkOutDay)
        room_type_info = defaultdict(lambda: {'count': 0, 'price': 0})

        # Đếm số lượng phòng trống cho từng loại phòng
        for room, room_type in rooms_query.all():
            room_type_info[room_type.name]['count'] += 1
            room_type_info[room_type.name]['price'] = room_type.price
            room_type_info[room_type.name]['id'] = room_type.id

        rooms_data = [
            {
                'room_type_id': info['id'],
                'room_type_name': type_name,
                'room_available': str(info['count']),
                'room_price': info['price'],
            }
            for type_name, info in room_type_info.items()
        ]
        return rooms_data

    except SQLAlchemyError as e:
        print(f"An error occurred in load_findRoom: {str(e)}")
        return jsonify({'error': str(e)}), 500


def saveBookingData(id, user_id, roomType_id, checkInDay, checkOutDay):
    rooms_query = (
        db.session.query(Room, RoomType)
        .join(RoomType, RoomType.id == Room.roomType_id)
        .outerjoin(Booking)
        .options(joinedload(Room.roomType))
        .filter(
            or_(
                Booking.id.is_(None),
                and_(
                    or_(
                        Booking.startDay > checkOutDay,
                        Booking.endDay < checkInDay
                    ),
                    Booking.id.isnot(None)
                )
            ), Room.roomType_id == roomType_id
        )
    )
    result = rooms_query.first()
    if result:
        room_id = result[0].id  # Lấy room_id từ kết quả
        print(result[0].name)
        new_booking = Booking(
            id=id,
            user_id=user_id,
            room_id=room_id,
            startDay=checkInDay,
            endDay=checkOutDay
        )
        db.session.add(new_booking)
        db.session.commit()
        return print("Đặt phòng thành công!")
    else:
        return print("Không có phòng trống!")


def saveBookingData_admin(bookingId, nameCustomer, numPhoneCus,room_id, checkInDay, checkOutDay):
    new_user = User(
        name=nameCustomer,
        phoneNum=numPhoneCus,
    )
    db.session.add(new_user)
    db.session.commit()

    newUser_id = new_user.id
    new_booking = Booking(
        id=bookingId,
        room_id=room_id,
        user_id=newUser_id,
        startDay=checkInDay,
        endDay=checkOutDay
    )
    db.session.add(new_booking)
    db.session.commit()

    room = Room.query.get(room_id)
    if room:
        room.checkIn_status = True
        db.session.commit()
        return True
    else:
        return False

def load_roomAll(id=None):
    rooms = Room.query
    if id:
        room = rooms.get(id)
        return room
    else:
        return rooms.all()


def checkIn_room(id, booking_id, user_id, checkInDate, numNights, totalPrice):
    booking = Booking.query.get(booking_id)
    if booking:
        booking.checkIn_status = True
        db.session.commit()
        new_receipt = Receipt(
            user_id=user_id,
            booking_id=booking_id,
            startDay=checkInDate,
            totalPrice=totalPrice,
        )
        db.session.add(new_receipt)
        db.session.commit()
        return True
    else:
        return False

def checkOut_room(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        booking.checkIn_status = False
        db.session.commit()
        return True
    else:
        return False


def count_product():
    return RoomType.query.count()


def get_user_by_id(id):
    return Account.query.get(id)

def add_user(name, username, phoneNum, email, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    user = User(name=name, phoneNum=phoneNum, email=email)
    db.session.add(user)
    db.session.commit()
    user_id = user.id
    account = Account(user_id = user_id, username=username, password=password)
    db.session.add(account)
    db.session.commit()

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return Account.query.filter(Account.username.__eq__(username.strip()),
                             Account.password.__eq__(password)).first()
def load_user(id=None):
    users = User.query
    if id:
        user = users.filter(User.id == id)
        return user.first()
    else:
        return users.all()