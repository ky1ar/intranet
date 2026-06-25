from application.db_models.base_model import db, BaseModel


class Order(BaseModel):
    __tablename__ = "wordpress_order"

    id                   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id            = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    wc_order_id          = db.Column(db.Integer, nullable=False, unique=True)
    order_number         = db.Column(db.String(30))
    # Estado interno del tablero (kanban): registered / in_process / completed / discarded.
    status               = db.Column(db.String(20), nullable=False, default="registered")
    # Estado del pedido tal cual llega de WooCommerce (pending, processing, etc.).
    wc_status            = db.Column(db.String(30))
    total                = db.Column(db.Numeric(10, 2))
    currency             = db.Column(db.String(10))
    payment_method       = db.Column(db.String(50))
    payment_method_title = db.Column(db.String(100))
    order_date           = db.Column(db.DateTime)
    # Vendedor (ejecutivo de ayuda): user.id de la intranet resuelto por correo.
    seller_id            = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at           = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at           = db.Column(db.DateTime, onupdate=db.func.now())

    client = db.relationship("Clients", foreign_keys=[client_id], lazy="joined")
    seller = db.relationship("Users", foreign_keys=[seller_id], lazy="joined")


class OrderItem(BaseModel):
    __tablename__ = "wordpress_order_items"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id   = db.Column(db.Integer, db.ForeignKey("wordpress_order.id"), nullable=False)
    product_id = db.Column(db.Integer)
    name       = db.Column(db.String(255))
    quantity   = db.Column(db.Integer, default=1)
    total      = db.Column(db.Numeric(10, 2))

    order = db.relationship(
        "Order",
        foreign_keys=[order_id],
        backref=db.backref("items", lazy="selectin"),
    )
