import math
from flask import render_template, request, redirect, session, jsonify
import dao, utils
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole, User, RoomRental


@app.route("/")
def index():
    cate_id = request.args.get('category_id')
    kw = request.args.get('kw')
    page = request.args.get('page', 1)
    prods = dao.load_products(cate_id=cate_id, kw=kw, page=int(page))

    page_size = app.config.get('PAGE_SIZE', 8)
    total = dao.count_products()

    return render_template('index.html', products=prods,
                           pages=math.ceil(total/page_size))


@app.route('/reception_room')
def reception_room():
    status = request.args.get('status')
    cr_rental = request.args.get('cr_rental')
    page = request.args.get('page', 1)
    rooms = dao.load_rooms(status=status, page=int(page))
    page_size = app.config.get('PAGE_SIZE', 8)
    total = dao.count_rooms(status)

    return render_template('reception/reception_room.html', rooms=rooms,
                           cr_rental=cr_rental,
                           pages=math.ceil(total/page_size))

@app.route('/reception')
def reception_home():
    kw = request.args.get("kw")
    criteria = request.args.get("criteria")
    cus = dao.get_customers()
    rooms = dao.get_rooms()
    # if not result:
    #     return redirect(request.referrer)
    result = dao.load_customers(criteria=criteria, kw=kw)

    return render_template('reception/reception_home.html'
                           ,result = result, customers = cus, rooms = rooms, criteria = criteria)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)
            if u.user_role == UserRole.RECEPTION:
                return redirect('/reception')
            return redirect('/')
    return render_template('login.html')



@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = None
    if request.method.__eq__('POST'):
        confirm = request.form.get('confirm')
        password = request.form.get('password')
        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)
            return redirect('/login')
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)
@app.route('/reception_rental', methods=['GET', 'POST'])
def reception_rental():
    room_id = request.args.get('room_id')
    room_name = request.args.get('room_name')
    err_msg = None
    if request.method == 'POST':
        checkin_date = request.form.get('checkin_date')
        checkout_date = request.form.get('checkout_date')
        room_id = request.form.get('room_id')
        guest_count = int(request.form.get('guest_count', 0))
        guests = []
        for i in range(1, guest_count + 1):
            guest = {
                'name': request.form.get(f'guest{i}_name'),
                'type': request.form.get(f'guest{i}_type'),
                'cmnd': request.form.get(f'guest{i}_cmnd'),
                'address': request.form.get(f'guest{i}_address')
            }
            guests.append(guest)

        # Kiểm tra dữ liệu hợp lệ
        if checkin_date and checkout_date and guest_count != 0:
            for guest in guests:
                if guest['name'] and guest['type'] and guest['cmnd'] and guest['address']:
                    dao.add_customer(name=guest['name'], customer_type=guest['type'],
                                     cmnd=guest['cmnd'], address=guest['address'])
                else:
                    err_msg = 'VUI LÒNG ĐIỀN ĐẦY ĐỦ THÔNG TIN!'
            if not err_msg :
                r = dao.add_room_rental(checkin_date=checkin_date, checkout_date=checkout_date, room_id=room_id)
                dao.update_room_status(room_id, 'đã được thuê')
                for guest in guests:
                    dao.add_customer_room_rental(customer_id=dao.get_user_id_by_cmnd(guest['cmnd']), room_rental_id=r.id)
                return redirect('/reception')
    return render_template('reception/reception_rental.html',
                           room_id=room_id, room_name=room_name, err_msg=err_msg)




@app.route('/api/carts', methods=['post'])
def add_to_cart():
    """
    {
        "1": {
            "id": "1",
            "name": "abc",
            "price": 123,
            "quantity": 2
        }, "2": {
            "id": "2",
            "name": "abc",
            "price": 123,
            "quantity": 2
        }
    }
    """
    cart = session.get('cart')
    if not cart:
        cart = {}

    id = str(request.json.get("id"))
    name = request.json.get("name")
    price = request.json.get("price")

    if id in cart:
        cart[id]["quantity"] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session['cart'] = cart

    return jsonify(utils.stats_cart(cart))


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.context_processor
def common_response():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.stats_cart(session.get('cart'))
    }


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
