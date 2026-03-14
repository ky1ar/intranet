from application import db
from enum import Enum

class HistoryType(Enum):
    ADDED = "ADDED"
    STATUS_CHANGE = "STATUS_CHANGE"
    UPDATED = "UPDATED"
    DELETED = "DELETED"


class ShippingStatusList(Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    ON_THE_WAY = "ON_THE_WAY"
    DELIVERED = "DELIVERED"
    NOT_DELIVERED = "NOT_DELIVERED"


class HistoryType(Enum):
    ADDED = "ADDED"
    STATUS_CHANGE = "STATUS_CHANGE"
    UPDATED = "UPDATED"
    DELETED = "DELETED"

    
class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self, only_fields=None, exclude_fields=None):
        if only_fields:
            only_fields = set(only_fields)
        if exclude_fields:
            exclude_fields = set(exclude_fields)

        result = {}
        for column in self.__table__.columns:
            if only_fields and column.name not in only_fields:
                continue
            if exclude_fields and column.name in exclude_fields:
                continue
            result[column.name] = getattr(self, column.name)

        return result





# USERS
class Users(BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('user_level.id'), nullable=False, default=1)
    department_id = db.Column(db.Integer, db.ForeignKey('user_department.id'))
    shipping_app_level = db.Column(db.Integer)
    document = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))
    birthday = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    default_page = db.Column(db.String(100))
    stamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    level = db.relationship("UserLevel", lazy="joined", foreign_keys=[level_id])
    department = db.relationship("UserDepartment", lazy="joined", foreign_keys=[department_id])


class UserCodes(BaseModel):
    __tablename__ = 'user_codes'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(9))
    otp = db.Column(db.String(6))
    status = db.Column(db.String(25), default="pending")
    created_at = db.Column(db.DATETIME, nullable=False, server_default=db.func.current_timestamp())

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class UserLevel(BaseModel):
    __tablename__ = 'user_level'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(120))
    slug = db.Column(db.String(120))


class UserDepartment(BaseModel):
    __tablename__ = 'user_department'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(120))
    slug = db.Column(db.String(120))


class FireCloudTokens(BaseModel):
    __tablename__ = 'firecloud_tokens'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    device_platform = db.Column(db.String(16), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])





class Department(BaseModel):
    __tablename__ = "location_department"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class Province(BaseModel):
    __tablename__ = "location_province"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("location_department.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    department = db.relationship("Department", lazy="joined", foreign_keys=[department_id])


class District(BaseModel):
    __tablename__ = "location_district"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey("location_province.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    province = db.relationship("Province", lazy="joined", foreign_keys=[province_id])
    

# CLIENTS
class Clients(BaseModel):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    document = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    stamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    department_id = db.Column(db.Integer, db.ForeignKey('location_department.id'), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('location_province.id'), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('location_district.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    department = db.relationship("Department", lazy="joined", foreign_keys=[department_id])
    province = db.relationship("Province", lazy="joined", foreign_keys=[province_id])
    district = db.relationship("District", lazy="joined", foreign_keys=[district_id])


class ClientOrders(BaseModel):
    __tablename__ = 'client_orders'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    number = db.Column(db.Integer, unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)

    client = db.relationship("Clients", lazy="joined", foreign_keys=[client_id])





# SHIPPING
class ShippingMethod(BaseModel):
    __tablename__ = 'shipping_method'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100))
    background = db.Column(db.String(7))
    border = db.Column(db.String(7))


class ShippingStatus(BaseModel):
    __tablename__ = 'shipping_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class ShippingSchedule(BaseModel):
    __tablename__ = 'shipping_schedule'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class ShippingDistricts(BaseModel):
    __tablename__ = 'shipping_districts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255))


class ShippingOrders(BaseModel):
    __tablename__ = 'shipping_orders'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    client_order_id = db.Column(db.Integer, db.ForeignKey('client_orders.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('shipping_method.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('shipping_status.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('shipping_schedule.id'))
    address = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(255))
    district_id = db.Column(db.Integer, db.ForeignKey('shipping_districts.id'), nullable=False)
    comments = db.Column(db.String(255))
    maps = db.Column(db.String(255))
    proof_photo = db.Column(db.String(255))
    register_date = db.Column(db.DATE, nullable=False)
    delivery_date = db.Column(db.DATE, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    client_order = db.relationship("ClientOrders", lazy="joined", foreign_keys=[client_order_id])
    method = db.relationship("ShippingMethod", lazy="joined", foreign_keys=[method_id])
    driver = db.relationship("Users", lazy="joined", foreign_keys=[driver_id])
    assigned = db.relationship("Users", lazy="joined", foreign_keys=[assigned_id])
    status = db.relationship("ShippingStatus", lazy="joined", foreign_keys=[status_id])
    schedule = db.relationship("ShippingSchedule", lazy="joined", foreign_keys=[schedule_id])
    district = db.relationship("ShippingDistricts", lazy="joined", foreign_keys=[district_id])


class ShippingHistory(BaseModel):
    __tablename__ = 'shipping_history'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shipping_order_id = db.Column(db.Integer, db.ForeignKey('shipping_orders.id'), nullable=False)
    type = db.Column(db.Enum(HistoryType), nullable=False)
    status = db.Column(db.Enum(ShippingStatusList), nullable=False)
    data = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp())

    shipping_order = db.relationship("ShippingOrders", lazy="joined", foreign_keys=[shipping_order_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])





# GENERAL
class Brands(BaseModel):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)


class Machines(BaseModel):
    __tablename__ = 'machines'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)

    brand = db.relationship("Brands", lazy="joined", foreign_keys=[brand_id])





# SERVICE
class ServiceMethod(BaseModel):
    __tablename__ = 'service_method'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)


class ServiceOrigin(BaseModel):
    __tablename__ = 'service_origin'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)


class ServiceStatus(BaseModel):
    __tablename__ = 'service_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)


class ServiceOrders(BaseModel):
    __tablename__ = 'service_orders'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    order_number = db.Column(db.Integer, nullable=False, unique=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('service_method.id'))
    origin_id = db.Column(db.Integer, db.ForeignKey('service_origin.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('service_status.id'), nullable=False, default=1)
    protect = db.Column(db.Integer, default=0)
    comments = db.Column(db.String(255))
    register_at = db.Column(db.DATETIME, nullable=False)
    updated_at = db.Column(db.DATETIME)
    paid = db.Column(db.Integer, default=0)
    pay_amount = db.Column(db.FLOAT)

    machine = db.relationship("Machines", lazy="joined", foreign_keys=[machine_id])
    client = db.relationship("Clients", lazy="joined", foreign_keys=[client_id])
    technician = db.relationship("Users", lazy="joined", foreign_keys=[technician_id])
    method = db.relationship("ServiceMethod", lazy="joined", foreign_keys=[method_id])
    origin = db.relationship("ServiceOrigin", lazy="joined", foreign_keys=[origin_id])
    status = db.relationship("ServiceStatus", lazy="joined", foreign_keys=[status_id])


class ServiceOrderStatus(BaseModel):
    __tablename__ = 'service_order_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    service_order_id = db.Column(db.Integer, db.ForeignKey('service_orders.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('service_status.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    register_at = db.Column(db.DATETIME, nullable=False)
    notes = db.Column(db.Text)

    service_order = db.relationship("ServiceOrders", lazy="joined", foreign_keys=[service_order_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
    status = db.relationship("ServiceStatus", lazy="joined", foreign_keys=[status_id])


class ServiceOrderPhotos(BaseModel):
    __tablename__ = 'service_order_photos'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    service_order_id = db.Column(db.Integer, db.ForeignKey('service_orders.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('service_status.id'), nullable=False)
    filename = db.Column(db.String(100))

    service_order = db.relationship("ServiceOrders", lazy="joined", foreign_keys=[service_order_id])
    status = db.relationship("ServiceStatus", lazy="joined", foreign_keys=[status_id])


class ServiceLinks(BaseModel):
    __tablename__ = 'service_links'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    order_number = db.Column(db.Integer)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('service_link_status.id'), nullable=False)
    created_at = db.Column(db.DATETIME, nullable=False)
    expires_at = db.Column(db.DATETIME)

    status = db.relationship("ServiceLinkStatus", lazy="joined", foreign_keys=[status_id])
    client = db.relationship("Clients", lazy="joined", foreign_keys=[client_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])


class ServiceLinkStatus(BaseModel):
    __tablename__ = 'service_link_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)





# TRAINING
class TrainingCalendar(BaseModel):
    __tablename__ = 'training_calendar'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('training_status.id'), nullable=False)
    purchase_receipt = db.Column(db.String(255))
    cancel_proof = db.Column(db.String(255))
    meet = db.Column(db.String(255))
    comments = db.Column(db.String(255))
    training_date = db.Column(db.DATE)
    training_start = db.Column(db.TIME)

    machine = db.relationship("Machines", lazy="joined", foreign_keys=[machine_id])
    technician = db.relationship("Users", lazy="joined", foreign_keys=[technician_id])
    client = db.relationship("Clients", lazy="joined", foreign_keys=[client_id])
    status = db.relationship("TrainingStatus", lazy="joined", foreign_keys=[status_id])


class TrainingStatus(BaseModel):
    __tablename__ = 'training_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)





# TRACKING
class TrackingOrders(BaseModel):
    __tablename__ = 'tracking_orders'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    client_order_id = db.Column(db.Integer, db.ForeignKey('client_orders.id'), nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('tracking_agencies.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('tracking_status.id'), nullable=False)
    code1 = db.Column(db.String(20), nullable=False)
    code2 = db.Column(db.String(20), nullable=False)
    code3 = db.Column(db.String(20), nullable=False)
    origin_agency = db.Column(db.String(100))
    destination_agency = db.Column(db.String(100))
    external_id = db.Column(db.String(25))
    register_at = db.Column(db.DATETIME, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DATETIME)

    client_order = db.relationship("ClientOrders", lazy="joined", foreign_keys=[client_order_id])
    agency = db.relationship("TrackingAgencies", lazy="joined", foreign_keys=[agency_id])
    status = db.relationship("TrackingStatus", lazy="joined", foreign_keys=[status_id])


class TrackingAgencies(BaseModel):
    __tablename__ = 'tracking_agencies'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(100), nullable=False)


class TrackingStatus(BaseModel):
    __tablename__ = 'tracking_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)


class TrackingOrderStatus(BaseModel):
    __tablename__ = 'tracking_order_history'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    tracking_order_id = db.Column(db.Integer, db.ForeignKey('tracking_orders.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('tracking_status.id'), nullable=False)
    register_at = db.Column(db.DATETIME, nullable=False)

    tracking_order = db.relationship("TrackingOrders", lazy="joined", foreign_keys=[tracking_order_id])
    status = db.relationship("TrackingStatus", lazy="joined", foreign_keys=[status_id])





# BOARD
class BoardIssues(BaseModel):
    __tablename__ = 'board_issues'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('board_statuses.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey('board_priority.id'), nullable=False, default=3)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('board_types.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DATETIME, nullable=False)
    updated_at = db.Column(db.DATETIME)

    status = db.relationship("BoardStatuses", lazy="joined", foreign_keys=[status_id])
    priority = db.relationship("BoardPriority", lazy="joined", foreign_keys=[priority_id])
    reporter = db.relationship("Users", lazy="joined", foreign_keys=[reporter_id])
    assignee = db.relationship("Users", lazy="joined", foreign_keys=[assignee_id])
    type = db.relationship("BoardTypes", lazy="joined", foreign_keys=[type_id])


class BoardStatuses(BaseModel):
    __tablename__ = 'board_statuses'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)


class BoardPriority(BaseModel):
    __tablename__ = 'board_priority'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)


class BoardTypes(BaseModel):
    __tablename__ = 'board_types'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('user_department.id'))

    department = db.relationship("UserDepartment", lazy="joined", foreign_keys=[department_id])


class BoardHistory(BaseModel):
    __tablename__ = 'board_history'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('board_issues.id'), nullable=False)
    type = db.Column(db.Enum(HistoryType), nullable=False)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DATETIME, nullable=False)

    issue = db.relationship("BoardIssues", lazy="joined", foreign_keys=[issue_id])
    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])





# WSP

class UserContext(BaseModel):
    __tablename__ = 'user_context'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(128), nullable=False)
    campaign = db.Column(db.String(128), nullable=False)
    last_message_id = db.Column(db.Text)
    status = db.Column(db.String(128), nullable=False, default='idle')
    sended_at = db.Column(db.TIMESTAMP)
    updated_at = db.Column(db.TIMESTAMP)





# EVENTS

class Events(db.Model):
    __tablename__ = 'schedule_events'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    import_shipment_id = db.Column(db.Integer, db.ForeignKey('import_shipment.id'))
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)
    meet = db.Column(db.String(255))
    hex_color = db.Column(db.String(7))
    visibility_id = db.Column(db.Integer, db.ForeignKey('schedule_visibility.id'))
    all_day = db.Column(db.Integer)
    repeat_id = db.Column(db.Integer, db.ForeignKey('schedule_repeat.id'))
    notify_id = db.Column(db.Integer, db.ForeignKey('schedule_notify.id'))
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
    visibility = db.relationship("Visibility", lazy="joined", foreign_keys=[visibility_id])
    repeat = db.relationship("Repeat", lazy="joined", foreign_keys=[repeat_id])
    notify = db.relationship("Notify", lazy="joined", foreign_keys=[notify_id])
    import_shipment = db.relationship("ImportShipment", lazy="joined", foreign_keys=[import_shipment_id])
    visibility_users = db.relationship("EventVisibilityUser", lazy="selectin", cascade="all, delete-orphan", primaryjoin="Events.id==EventVisibilityUser.event_id")
    visibility_departments = db.relationship("EventVisibilityDepartment", lazy="selectin", cascade="all, delete-orphan",primaryjoin="Events.id==EventVisibilityDepartment.event_id")


class Visibility(db.Model):
    __tablename__ = 'schedule_visibility'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


class EventVisibilityUser(db.Model):
    __tablename__ = "schedule_event_visibility_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey("schedule_events.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint("event_id", "user_id", name="uq_event_user"),
    )


class EventVisibilityDepartment(db.Model):
    __tablename__ = "schedule_event_visibility_departments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey("schedule_events.id"), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("user_department.id"), nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint("event_id", "department_id", name="uq_event_dept"),
    )


class Repeat(db.Model):
    __tablename__ = 'schedule_repeat'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


class Notify(db.Model):
    __tablename__ = 'schedule_notify'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)


class Colors(db.Model):
    __tablename__ = 'schedule_colors'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hex = db.Column(db.String(7), nullable=False)


class Holidays(db.Model):
    __tablename__ = 'schedule_holidays'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hex_color = db.Column(db.String(7))
    deleted_at = db.Column(db.DateTime)





# PURCHASE

class PurchaseType(db.Model):
    __tablename__ = 'purchase_type'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)


class PurchaseUrgency(db.Model):
    __tablename__ = 'purchase_urgency'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)


class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('purchase_type.id'), nullable=False)
    urgency_id = db.Column(db.Integer, db.ForeignKey('purchase_urgency.id'))
    needed_date = db.Column(db.Date)
    express = db.Column(db.Integer, default=0, nullable=False)
    it_validation = db.Column(db.Integer, default=0, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('purchase_status.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    leader_approved_at = db.Column(db.DateTime)
    manager_approved_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    user = db.relationship("Users", lazy="joined", foreign_keys=[user_id])
    purchase_type = db.relationship("PurchaseType", lazy="joined", foreign_keys=[type_id])
    purchase_urgency = db.relationship("PurchaseUrgency", lazy="joined", foreign_keys=[urgency_id])
    status = db.relationship("PurchaseStatus", lazy="joined", foreign_keys=[status_id])


class PurchaseItems(db.Model):
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2))
    url = db.Column(db.Text)
    ruc = db.Column(db.String(11))
    order_number = db.Column(db.String(64))
    legal_name = db.Column(db.String(255))
    deleted_at = db.Column(db.DateTime)

    purchase_request = db.relationship("PurchaseRequest", lazy="joined", foreign_keys=[purchase_id], backref=db.backref("items", lazy="selectin"),)


class PurchaseStatus(db.Model):
    __tablename__ = 'purchase_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)


class PurchaseChats(db.Model):
    __tablename__ = 'purchase_chats'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column( db.DateTime, nullable=False)
    
    commenter = db.relationship( "Users", lazy="joined", foreign_keys=[commenter_id])
    purchase_request = db.relationship( "PurchaseRequest", lazy="joined", foreign_keys=[purchase_id], backref=db.backref("chats", lazy="selectin"))