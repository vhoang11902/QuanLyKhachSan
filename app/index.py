from flask import render_template, request, redirect, session, jsonify, url_for
import dao
import utils
from app import app, login, controller
from flask_login import login_user, logout_user


@app.route('/login', methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

        next = request.args.get('next')
        if next:
            return redirect(next)

        return redirect("/")

    return render_template('login.html')


@app.route('/reviewBooking/endBooking/<booking_id>')
def end_booking(booking_id):
    return render_template('endBooking.html', booking_id=booking_id)

app.add_url_rule('/', 'index', controller.index)

app.add_url_rule('/api/room', 'find_room', controller.find_room, methods=['post'])

app.add_url_rule('/checkOutBooking/<id>', 'checkOutBooking', controller.checkOut_booking)

app.add_url_rule('/reviewBooking/<booking_id>', 'reviewBooking', controller.review_booking, methods=['post'])

app.add_url_rule('/api/submitBooking/<booking_id>', 'submitBooking', controller.submit_booking, methods=['post'])

app.add_url_rule('/room', 'room', controller.room)

# phía admin
app.add_url_rule('/api/roomAdmin', 'findRoom_admin', controller.findRoom_admin, methods=['post'])

app.add_url_rule('/api/bookingRoomAdmin', 'bookingRoom_admin', controller.bookingRoom_admin, methods=['post'])

app.add_url_rule('/api/checkInRoom/<room_id>', 'checkIn_room', controller.checkIn_room, methods=['post'])

app.add_url_rule('/api/checkOutRoom/<room_id>', 'checkOut_room', controller.checkOut_room, methods=['post'])

@app.route('/admin/login', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id=id)


# dang nhap luc nao cung phai la post
@app.route('/user-login', methods=['GET', 'POST'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for('index'))
        else:
            err_msg = 'Username hoac password khong chinh xac'
    return render_template('login.html', err_msg=err_msg)


@app.route('/user_logout', methods=['get'])
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        phoneNum = request.form.get('phoneNum')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None
        try:
            if (password.strip().__eq__(confirm.strip())):
                dao.add_user(name=name, username=username, phoneNum=phoneNum, email=email,
                             password=password)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mat khau khong khop!'
        except Exception as ex:
            err_msg = 'He thong co loi: ' + str(ex)
        # sau nay co cac truong hop loi cu the phai show ra dung loi

    return render_template('register.html', err_msg=err_msg)


if __name__ == '__main__':
    from app import admin

    app.run(debug=True, port=2222)
