import math
from datetime import datetime, timedelta
import random, string

from flask import render_template, request, redirect, session, jsonify, url_for
from flask_login import current_user

from app import app, dao


def index():
    return render_template('index.html')


def room():
    kw = request.args.get('kw')
    page = request.args.get("page")
    roomTypes = dao.load_roomTypes(id=id, page=page)
    total = dao.count_product()

    return render_template('room.html',
                           products=roomTypes,
                           pages=math.ceil(total / app.config['PAGE_SIZE']))


def find_room():
    try:
        data = request.json
        start_date = datetime.strptime(data.get("date"), '%Y-%m-%d %H:%M')
        num_days = int(data.get("nights"))
        end_date = start_date + timedelta(days=num_days) - timedelta(hours=2)

        checkIn = start_date.strftime('%Y-%m-%d %H:%M')
        checkOut = end_date.strftime('%Y-%m-%d %H:%M')

        session['checkInDay'] = checkIn
        session['checkOutDay'] = checkOut
        session['guests'] = data.get('guests')

        checkInDay = start_date.strftime('%d/%m/%Y %H:%M')
        checkOutDay = end_date.strftime('%d/%m/%Y %H:%M')

        loadRoom = dao.load_findRoom(start_date=checkInDay, end_date=checkOutDay)

        return jsonify(loadRoom)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def checkOut_booking(id):
        booking_id = booking_id = ''.join(random.choices(string.digits, k=10))
        guests = session.get('guests')
        checkIn = datetime.strptime(session.get('checkInDay'), '%Y-%m-%d %H:%M')
        checkOut = datetime.strptime(session.get('checkOutDay'), '%Y-%m-%d %H:%M')

        checkInDay = checkIn.strftime('%a, %d %b %Y, From %H:%M')
        checkOutDay = checkOut.strftime('%a, %d %b %Y, From %H:%M')

        roomType = dao.load_roomTypes(id=id)

        room_name = roomType.name if roomType else None
        room_price = roomType.price if roomType else None
        room_tax = room_price * 10 / 100

        return render_template('completeBook.html', id=id, booking_id=booking_id, checkInDay=checkInDay,
                               checkOutDay=checkOutDay, guests=guests, room_name=room_name, room_price=room_price,
                               room_tax=room_tax)

def review_booking(booking_id):
    name = request.form.get('nameCustomer')
    numPhone = request.form.get('numPhoneCus')
    email = request.form.get('emailCustomer')
    roomName = request.form.get('room_name')
    roomPrice = float(request.form.get('room_price'))
    roomTax = float(request.form.get('room_tax'))
    roomId = request.form.get('room_id')

    checkIn = datetime.strptime(session.get('checkInDay'), '%Y-%m-%d %H:%M')
    checkOut = datetime.strptime(session.get('checkOutDay'), '%Y-%m-%d %H:%M')

    checkInDay = checkIn.strftime('%a, %d %b %Y')
    checkOutDay = checkOut.strftime('%a, %d %b %Y')

    return render_template('reviewBooking.html', roomId=roomId, booking_id=booking_id,
                           name=name, numPhone=numPhone, email=email,
                           checkOutDay=checkOutDay, checkInDay=checkInDay
                           , roomName=roomName, roomPrice=roomPrice, roomTax=roomTax)


def submit_booking(booking_id):
    data = request.json
    checkIn = data.get("checkInDay")
    checkOut = data.get("checkOutDay")
    user_id = current_user.id
    roomTypeId = data.get("roomType_id")

    checkInDay = datetime.strptime(checkIn, '%a, %d %b %Y %H:%M')
    checkOutDay = datetime.strptime(checkOut, '%a, %d %b %Y %H:%M')

    dao.saveBookingData(booking_id, user_id, roomTypeId, checkInDay, checkOutDay)
    return booking_id;
def findRoom_admin():
    try:
        data = request.json
        start_date = datetime.strptime(data.get("date"), '%Y-%m-%d %H:%M')
        num_days = int(data.get("nights"))
        end_date = start_date + timedelta(days=num_days) - timedelta(hours=2)

        checkInDay = start_date.strftime('%Y-%m-%d %H:%M')
        checkOutDay = end_date.strftime('%Y-%m-%d %H:%M')

        room_list = dao.load_roomAll()
        available_rooms_query = dao.get_booking_rooms_query(checkInDay, checkOutDay).all()

        available_room_data = [
            {
                'room_id': roomAble.id,
                'room_name': roomAble.name,
                'booking_id': Booking.id,
                'user_id': Booking.user.id,
                'user_name': Booking.user.name,
                'booking_status': Booking.status,
                'room_type_id': room_type.id,
                'room_type_name': room_type.name,
                'checkIn_status': Booking.checkIn_status
            }
            for roomAble, room_type, Booking in available_rooms_query
        ]
        room_list_data = [
            {
                'id': room.id,
                'name': room.name,
                'room_type': room.roomType.name,
            }
            for room in room_list
        ]
        response_data = {
            'availableRoom': available_room_data,
            'room_list': room_list_data
        }
        return jsonify(response_data)

    except Exception as e:
        # Handle exceptions
        print(f"Error: {e}")
        return jsonify({'error': str(e)})


def bookingRoom_admin():
    data = request.json
    booking_id = booking_id = ''.join(random.choices(string.digits, k=10))
    nameCustomer = data.get("nameCus")
    numPhoneCus = data.get("phoneNum")

    numNights = int(data.get("numNights"))
    checkIn = data.get("checkIn")
    room_id = data.get("room_id")

    checkInDay = datetime.strptime(checkIn, '%Y-%m-%d %H:%M')
    checkOutDay = checkInDay + timedelta(days=numNights) - timedelta(hours=2)

    dao.saveBookingData_admin(booking_id, nameCustomer, numPhoneCus, room_id, checkInDay, checkOutDay)

    success_data = {'message': 'Đặt phòng thành công!', 'status': 'success'}
    return jsonify(success_data)


def checkIn_room(room_id):
    data = request.json
    room = dao.load_roomAll(room_id)
    user_id = data.get("user_id")
    booking_id = data.get("booking_id")
    checkInDate = data.get("checkIn_date")
    numNights = data.get("numNights")
    totalPrice = room.roomType.price*int(numNights)
    dao.checkIn_room(room_id, booking_id, user_id, checkInDate, numNights, totalPrice)
    success_data = {'message': 'Check In thành công!', 'status': 'success'}
    return jsonify(success_data)


def checkOut_room(room_id):
    dao.checkOut_room(room_id)

    success_data = {'message': 'Check Out thành công!', 'status': 'success'}
    return jsonify(success_data)