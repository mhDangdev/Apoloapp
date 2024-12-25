from app.models import *
from app import app, db
import hashlib
import cloudinary.uploader
from flask_login import current_user



def load_categories():
    return Category.query.order_by('id').all()



def load_products(cate_id=None, kw=None, page=1):
    query = Product.query

    if kw:
        query = query.filter(Product.name.contains(kw))

    if cate_id:
        query = query.filter(Product.category_id == cate_id)

    page_size = app.config.get('PAGE_SIZE')
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()


def count_products():
    return Product.query.count()

def get_customers():
    # result = db.session.query(Customer, reservation_customer).join(reservation_customer,
    #                                                                reservation_customer.c.customer_id == Customer.id).all()
    return Customer.query.all()

    return result

def get_rooms():
    return Room.query.all()

def load_rooms(status=None, page=1):
    query = Room.query

    if status:
        query = query.filter(Room.status == status)

    page_size = app.config.get('PAGE_SIZE')
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()

def count_rooms(status=None):
    if (status):
        return Room.query.filter(Room.status == status).count()
    return Room.query.count()

def load_customers(criteria=None, kw=None):
    if criteria == 'reservation':
        query = Reservation.query.join(ReservationCustomer).join(Customer)
    elif criteria == 'room_rental':
        query = RoomRental.query.join(CustomerRoomRental).join(Customer)
    # elif criteria == 'receipt':
    #     query = receipt.query
    if kw:
        query = query.filter(Customer.name.contains(kw))
    else :
        return

    return query.all()

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def get_user_by_id(id):
    return User.query.get(id)

def update_room_status(id, new_status):
        # Tìm phòng có id tương ứng
    room = Room.query.filter_by(id=id).first()

        # Kiểm tra xem phòng có tồn tại không
    if room:
            # Cập nhật trạng thái phòng
        room.status = new_status
        db.session.commit()


def get_user_id_by_cmnd(cmnd):
    cus = Customer.query.filter_by(cmnd=cmnd).first()
    if cus:
        return cus.id
    return None  # Trả về None nếu không tìm thấy người dùng

def add_user(name, username, password, avatar=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

def add_roomrental(checkin_date, checkout_date, room_id, deposit=None):
    if not deposit:
        deposit=0
    roomrental = RoomRental(receptionist_id=current_user.id, checkin_date=checkin_date, checkout_date=checkout_date
                            , room_id=room_id, deposit=deposit)
    db.session.add(roomrental)
    db.session.commit()
    return roomrental

def add_customer(name, customer_type, cmnd, address):
    customer = Customer(name=name, customer_type=customer_type, cmnd=cmnd, address=address)
    db.session.add(customer)
    db.session.commit()
    return customer
def add_customer_roomrental(customer_id, room_rental_id):
    query = CustomerRoomRental.insert().values(customer_id=customer_id, room_rental_id=room_rental_id)
    db.session.execute(query)
    db.session.commit()
def get_price(roomtype_id):
    u = RoomTypeRegulation.query.filter_by(RoomTypeRegulation.room_type_id==(roomtype_id)).first()
    return u.price
def load_roomtype_regulation():
    return  RoomTypeRegulation.query.all()
if __name__ == '__main__':
    print()