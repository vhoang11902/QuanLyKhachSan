from datetime import datetime, timedelta

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app import app, db, dao
from app.models import Room, RoomType, Booking
from flask_login import logout_user, current_user
from flask import redirect, session, request
from app.models import UserRoleEnum

admin = Admin(app=app, name='Novotel Admin', template_mode='bootstrap4')

class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


# class MyProductView(AuthenticatedAdmin):
#     column_list = ['id', 'name', 'price', 'category']
#     column_searchable_list = ['name']
#     column_filters = ['price', 'name']
#     can_export = True
#     can_view_details = True
#
#
# class MyCategoryView(AuthenticatedAdmin):
#     column_list = ['name', 'products']

class MyRoomView(AuthenticatedAdmin):
    column_list = ['name', 'room_status']

    def _format_room_status(view, context, model, name):
        if model.status:
            return 'Active'
        else:
            return 'Inactive'

    column_formatters = {
        'room_status': _format_room_status
    }

class MyRoomTypeView(AuthenticatedAdmin):
    column_list = ['name', 'price', 'numBeds']


class MyBookingView(AuthenticatedAdmin):
    @expose("/")
    def index(self):
        current_datetime = datetime.now()
        start_day = datetime(current_datetime.year, current_datetime.month, current_datetime.day, 14, 0)
        end_day = datetime(current_datetime.year, current_datetime.month, current_datetime.day, 12, 0) + timedelta(
            days=1)
        booking_room = dao.get_booking_rooms_query(start_day, end_day)
        room_list = dao.load_roomAll()
        return self.render('admin/stats.html', rooms=room_list, booking_room=booking_room)

    @expose('/<int:room_id>/')
    def room_detail(self, room_id):
        room = Room.query.get(room_id)
        user_id = request.args.get('user')
        booking_id = request.args.get('booking_id')
        date = request.args.get('date')
        numNights = request.args.get('numNights')
        user = dao.load_user(user_id)
        booking = dao.load_booking(booking_id)
        if booking_id:
            date = booking.startDay
            numNights = (booking.endDay-date).days
        elif date and numNights:
            date = request.args.get('date')
            numNights = request.args.get('numNights')
        else:
            date = datetime.now().strftime('%Y-%m-%d')
            numNights = 1
            print(numNights)
        return self.render('admin/roomDetail.html',booking=booking, booking_id=booking_id, room=room, user_id=user_id, user=user, date=date, numNights=numNights)

class MyLogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(MyRoomView(Room, db.session))
admin.add_view(MyRoomTypeView(RoomType, db.session))
admin.add_view(MyBookingView(Booking, db.session, name='Booking'))
admin.add_view(MyLogoutView(name='Đăng xuất'))
