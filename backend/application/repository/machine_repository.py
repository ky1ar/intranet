from application.handlers import handle_db_exceptions
from application.models import Machines, Brands, Category
from sqlalchemy import func, or_
from flask import g


class MachineRepository:
    @handle_db_exceptions
    def get_machines(self, machine_name):
        search_term = f"%{machine_name}%"
        full_name = func.concat(Brands.name, ' ', Machines.model).label("full_name")

        machines = (
            g.db_session.query(Machines.id, Machines.image, Machines.category_id, full_name)
            .join(Brands)
            .filter(full_name.ilike(search_term))
            .filter(Machines.category_id != 57)
            .order_by(full_name)
            .all()
        )
        if not machines:
            return None, 400

        return machines, 200

    @handle_db_exceptions
    def get_machine(self, machine_id):
        full_name = func.concat(Brands.name, ' ', Machines.model).label("full_name")
        machine = (
            g.db_session.query(Machines.id, Machines.image, full_name)
            .join(Brands)
            .filter(Machines.id == machine_id)
            .first()
        )
        if not machine:
            return None, 400

        return machine, 200

    @handle_db_exceptions
    def get_machine_full(self, machine_id):
        machine = g.db_session.query(Machines).filter(Machines.id == machine_id).first()
        if not machine:
            return None, 404
        return machine, 200

    # ---------------------------------------------------------------- listado
    @handle_db_exceptions
    def get_machines_paginated(self, page=1, per_page=12, q=None, category_id=None, brand_id=None):
        full_name = func.concat(Brands.name, ' ', Machines.model)

        query = (
            g.db_session.query(Machines)
            .join(Brands, Machines.brand_id == Brands.id)
            .join(Category, Machines.category_id == Category.id)
        )

        if q:
            like = f"%{q}%"
            query = query.filter(or_(full_name.ilike(like), Machines.model.ilike(like)))
        if category_id:
            query = query.filter(Machines.category_id == category_id)
        if brand_id:
            query = query.filter(Machines.brand_id == brand_id)

        query = query.order_by(Brands.name.asc(), Machines.model.asc())

        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "list": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }, 200

    # ----------------------------------------------------------------- machine
    @handle_db_exceptions
    def create_machine(self, data):
        machine = Machines(
            brand_id=data.get("brand_id"),
            category_id=data.get("category_id"),
            model=data.get("model"),
            image=data.get("image"),
            type=data.get("type"),
        )
        g.db_session.add(machine)
        g.db_session.flush()
        machine_id = machine.id
        g.db_session.commit()
        return machine_id, 200

    @handle_db_exceptions
    def update_machine(self, machine, data):
        for field in ("brand_id", "category_id", "model", "type", "image"):
            if data.get(field) is not None:
                setattr(machine, field, data[field])
        g.db_session.add(machine)
        g.db_session.commit()
        return True, 200

    # -------------------------------------------------------------- categories
    @handle_db_exceptions
    def list_categories(self):
        categories = g.db_session.query(Category).order_by(Category.name.asc()).all()
        return categories, 200

    @handle_db_exceptions
    def get_category(self, category_id):
        category = g.db_session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None, 404
        return category, 200

    @handle_db_exceptions
    def create_category(self, name, slug):
        category = Category(name=name, slug=slug)
        g.db_session.add(category)
        g.db_session.flush()
        category_id = category.id
        g.db_session.commit()
        return category_id, 200

    @handle_db_exceptions
    def update_category(self, category, name, slug):
        category.name = name
        category.slug = slug
        g.db_session.add(category)
        g.db_session.commit()
        return True, 200

    # ------------------------------------------------------------------ brands
    @handle_db_exceptions
    def list_brands(self):
        brands = g.db_session.query(Brands).order_by(Brands.name.asc()).all()
        return brands, 200

    @handle_db_exceptions
    def get_brand(self, brand_id):
        brand = g.db_session.query(Brands).filter(Brands.id == brand_id).first()
        if not brand:
            return None, 404
        return brand, 200

    @handle_db_exceptions
    def create_brand(self, name, slug):
        brand = Brands(name=name, slug=slug)
        g.db_session.add(brand)
        g.db_session.flush()
        brand_id = brand.id
        g.db_session.commit()
        return brand_id, 200

    @handle_db_exceptions
    def update_brand(self, brand, name, slug):
        brand.name = name
        brand.slug = slug
        g.db_session.add(brand)
        g.db_session.commit()
        return True, 200
