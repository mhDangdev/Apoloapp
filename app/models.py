from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, Table
from sqlalchemy.orm import relationship, Relationship, backref
from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)

class UserRole(RoleEnum):
    ADMIN = 1
    USER = 2
    RECEPTION = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1646729533/zuur9gzztcekmyfenkfr.jpg')
    user_role = Column(Enum(UserRole), default=UserRole.USER)

class RoomType(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    rooms = Relationship('Room', backref='room_type', lazy=True)

    def __str__(self):
        return self.name

class CustomerType(RoleEnum):
    DOMESTIC = 1
    FOREIGN = 2

####CÁC BẢNG TRUNG GIAN####

reservation_customer = db.Table(
    'reservation_customer',
    Column('reservation_id', Integer, ForeignKey('reservation.id'), primary_key=True),
    Column('customer_id', Integer, ForeignKey('customer.id'), primary_key=True)
)


customer_room_rental = db.Table(
    'customer_room_rental',
    Column('customer_id', Integer, ForeignKey('customer.id'), primary_key=True),
    Column('room_rental_id', Integer, ForeignKey('room_rental.id'), primary_key=True)
)

class Room(BaseModel):
    name = Column(String(100), nullable=False, unique=True)
    image = Column(String(500), default='static/images/phong1.jpg')
    room_type_id = Column(Integer, ForeignKey(RoomType.id), nullable=False)
    status = Column(String(100), nullable=True )
    room_rentals = relationship('RoomRental', backref='room', lazy='subquery')
    reservation = relationship('Reservation', backref='room', lazy='subquery')



class Customer(BaseModel):
    __tablename__ = 'customer'
    name = Column(String(100), nullable=False)
    customer_type = Column(Enum(CustomerType), default=CustomerType.DOMESTIC)
    cmnd = Column(String(100), nullable=False)
    address = Column(String(500), nullable=False)

    # Mối quan hệ với RoomRental thông qua bảng trung gian
    room_rentals = relationship('RoomRental',
                                secondary=customer_room_rental,
                                backref=backref('customers', lazy='subquery'),
                                lazy='subquery')


class RoomRental(BaseModel):
    __tablename__ = 'room_rental'
    checkin_date = Column(DateTime, nullable=False)
    checkout_date = Column(DateTime, nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)

class Reservation(BaseModel):
    __tablename__ = 'reservation'
    checkin_date = Column(DateTime)
    checkout_date = Column(DateTime)
    booker_name = Column(String(100), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)

    # Mối quan hệ Many-to-Many với Customer
    customers = relationship('Customer',
                             secondary=reservation_customer,
                             backref=backref('reservations', lazy='subquery'),
                             lazy='subquery')


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Product(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, default=0)
    image = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

    def __str__(self):
        return self.name
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        import hashlib
        # u = User(name='admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        #
        # u = User(name='letan', username='letan', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.RECEPTION)
        # db.session.add(u)
        #
        # u = User(name='user', username='user', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.USER)
        users = [
            User(name='admin', username='admin', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
                 user_role=UserRole.ADMIN),
            User(name='letan', username='letan', password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()),
                 user_role=UserRole.RECEPTION),
            User(name='John Doe', username='johndoe', password='123', user_role=UserRole.USER),
            User(name='Jane Smith', username='janesmith', password='123', user_role=UserRole.USER),
            User(name='Michael Brown', username='michaelb', password='123', user_role=UserRole.USER)
        ]
        db.session.bulk_save_objects(users)

        # Data mẫu cho RoomType
        room_types = [
            RoomType(name='Single'),
            RoomType(name='Double'),
            RoomType(name='Suite'),
            RoomType(name='Deluxe'),
            RoomType(name='Family')
        ]
        db.session.bulk_save_objects(room_types)
        db.session.commit()

        # Data mẫu cho Room
        rooms = [
            Room(name='101', image='static/images/phong1.jpg', room_type_id=1, status='còn trống'),
            Room(name='102', image='static/images/phong1.jpg', room_type_id=1, status='đã được thuê'),
            Room(name='201', image='static/images/phong1.jpg', room_type_id=2, status='còn trống'),
            Room(name='202', image='static/images/phong1.jpg', room_type_id=2, status='đã được thuê'),
            Room(name='301', image='static/images/phong1.jpg', room_type_id=3, status='đã được thuê'),
            Room(name='302', image='static/images/phong1.jpg', room_type_id=1, status='còn trống'),
            Room(name='303', image='static/images/phong1.jpg', room_type_id=1, status='đã được thuê'),
            Room(name='401', image='static/images/phong1.jpg', room_type_id=2, status='còn trống'),
            Room(name='402', image='static/images/phong1.jpg', room_type_id=2, status='đã được thuê'),
            Room(name='403', image='static/images/phong1.jpg', room_type_id=1, status='đã được thuê'),
            Room(name='405', image='static/images/phong1.jpg', room_type_id=1, status='đã được thuê'),
            Room(name='406', image='static/images/phong1.jpg', room_type_id=3, status='còn trống')
        ]
        db.session.bulk_save_objects(rooms)

        # Data mẫu cho Customer
        customers = [
            Customer(name='Nguyen Van A', customer_type=CustomerType.DOMESTIC, cmnd='123456789', address='Hanoi'),
            Customer(name='Tran Thi B', customer_type=CustomerType.DOMESTIC, cmnd='987654321',
                     address='Ho Chi Minh City'),
            Customer(name='John Carter', customer_type=CustomerType.FOREIGN, cmnd='A1234567', address='USA'),
            Customer(name='Jane Doe', customer_type=CustomerType.FOREIGN, cmnd='B7654321', address='UK'),
            Customer(name='Pham Van C', customer_type=CustomerType.DOMESTIC, cmnd='112233445', address='Da Nang')
        ]
        db.session.bulk_save_objects(customers)

        # Data mẫu cho RoomRental
        room_rentals = [
            RoomRental(checkin_date=datetime.today(), checkout_date=datetime(2025, 1, 3), room_id=1),
            RoomRental(checkin_date=datetime.today(), checkout_date=datetime(2025, 2, 7), room_id=2),
            RoomRental(checkin_date=datetime.today(), checkout_date=datetime(2025, 3, 15), room_id=3),
            RoomRental(checkin_date=datetime.today(), checkout_date=datetime(2025, 4, 25), room_id=4),
            RoomRental(checkin_date=datetime.today(), checkout_date=datetime(2025, 5, 3), room_id=5)

        ]
        db.session.bulk_save_objects(room_rentals)

        # Data mẫu cho Reservation
        reservations = [
            Reservation(checkin_date=datetime(2024, 6, 1), checkout_date=datetime(2024, 6, 3),
                        booker_name='Nguyen Van A', room_id=1),
            Reservation(checkin_date=datetime(2024, 7, 10), checkout_date=datetime(2024, 7, 12),
                        booker_name='Tran Thi B', room_id=2),
            Reservation(checkin_date=datetime(2024, 8, 15), checkout_date=datetime(2024, 8, 20),
                        booker_name='John Carter', room_id=3),
            Reservation(checkin_date=datetime(2024, 9, 5), checkout_date=datetime(2024, 9, 7), booker_name='Jane Doe',
                        room_id=4),
            Reservation(checkin_date=datetime(2024, 10, 1), checkout_date=datetime(2024, 10, 3),
                        booker_name='Pham Van C', room_id=5)
        ]
        db.session.bulk_save_objects(reservations)

        # Data mẫu cho bảng trung gian reservation_customer
        reservation_customer_data = [
            {'reservation_id': 1, 'customer_id': 1},
            {'reservation_id': 1, 'customer_id': 2},
            {'reservation_id': 2, 'customer_id': 3},
            {'reservation_id': 2, 'customer_id': 4},
            {'reservation_id': 2, 'customer_id': 5},
            {'reservation_id': 3, 'customer_id': 4},
            {'reservation_id': 4, 'customer_id': 5},
            {'reservation_id': 5, 'customer_id': 1}
        ]

        # Data mẫu cho bảng trung gian room_customer


        # Data mẫu cho bảng trung gian customer_room_rental
        customer_room_rental_data = [
            {'customer_id': 1, 'room_rental_id': 1},
            {'customer_id': 2, 'room_rental_id': 2},
            {'customer_id': 2, 'room_rental_id': 4},
            {'customer_id': 2, 'room_rental_id': 3},
            {'customer_id': 4, 'room_rental_id': 2},
            {'customer_id': 5, 'room_rental_id': 2},
            {'customer_id': 3, 'room_rental_id': 3},
            {'customer_id': 4, 'room_rental_id': 4},
            {'customer_id': 5, 'room_rental_id': 5}
        ]

        # Chèn dữ liệu vào các bảng trung gian
        for entry in reservation_customer_data:
            db.session.execute(reservation_customer.insert().values(**entry))


        for entry in customer_room_rental_data:
            db.session.execute(customer_room_rental.insert().values(**entry))

        db.session.commit()
