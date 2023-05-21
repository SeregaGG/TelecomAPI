from db.models import Base, EquipmentType, Equipment
from db.db import engine, DBContext
import cherrypy
import json
import redis
from uuid import uuid4
import os


def check_auth(func):
    def wrapper(*args, **kwargs):
        if args[0].R.get(cherrypy.request.headers["Authorization"].split()[1]) is None:
            raise cherrypy.HTTPError(403, "Forbidden, need to auth first")
        return func(*args, **kwargs)
    return wrapper


class WebService:
    R = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)

    @cherrypy.tools.json_out()
    @check_auth
    def get_equipment_by_id(self, eq_id: int):
        try:
            with DBContext() as db:
                equipment: Equipment = Equipment(id=int(eq_id)).get(db)
            return equipment.as_dict()
        except ValueError:
            raise cherrypy.HTTPError(404)

    @cherrypy.tools.json_out()
    @check_auth
    def get_all_equipment(self):
        with DBContext() as db:
            response: dict = Equipment.get_all_for_response(db)
        return json.dumps(response)

    @cherrypy.tools.json_in()
    @check_auth
    def create_equipment(self):
        errors_equipments: list = []

        for item in cherrypy.request.json:
            try:
                with DBContext() as db:
                    Equipment(**item).save(db)
            except Exception as e:
                errors_equipments.append((item, str(e)))

        return json.dumps(errors_equipments)

    @cherrypy.tools.json_in()
    @check_auth
    def update_equipment(self, eq_id):
        try:
            with DBContext() as db:
                equipment: Equipment = Equipment(id=int(eq_id)).get(db)
                equipment.update(db, cherrypy.request.json)
            return "Success"
        except Exception as e:
            return str(e)

    @cherrypy.tools.json_out()
    @check_auth
    def soft_delete_equipment(self, eq_id):
        try:
            with DBContext() as db:
                equipment: Equipment = Equipment(id=int(eq_id)).get(db)
                equipment.soft_delete(db)
            return "Success"
        except Exception as e:
            return str(e)

    @cherrypy.tools.json_out()
    @check_auth
    def get_equipment_types(self):
        with DBContext() as db:
            response: dict = EquipmentType.get_all_for_response(db)
        return json.dumps(response)

    def login(self):
        user_token = str(uuid4())
        self.R.set(user_token, 1)
        return user_token


def setup_database():
    Base.metadata.create_all(engine)

    # For test only
    with DBContext() as db:
        equipment_type = EquipmentType(type_name="Test", serial_mask="XXAAAAAXAA")
        db.add(equipment_type)
        db.commit()


if __name__ == '__main__':
    cherrypy.server.socket_host = os.getenv("APP_HOST")

    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    dispatcher.explicit = False

    dispatcher.connect(name='get equipment by id',
                       route='/api/equipment/{eq_id}',
                       controller=WebService().get_equipment_by_id,
                       conditions={'method': ['GET']})

    dispatcher.connect(name='get all equipments',
                       route='/api/equipment',
                       controller=WebService().get_all_equipment,
                       conditions={'method': ['GET']})

    dispatcher.connect(name='create equipment',
                       route='/api/equipment',
                       controller=WebService().create_equipment,
                       conditions={'method': ['POST']})

    dispatcher.connect(name='update equipment',
                       route='/api/equipment/{eq_id}',
                       controller=WebService().update_equipment,
                       conditions={'method': ['PUT']})

    dispatcher.connect(name='delete equipment',
                       route='/api/equipment/{eq_id}',
                       controller=WebService().soft_delete_equipment,
                       conditions={'method': ['DELETE']})

    dispatcher.connect(name='get equipment-type',
                       route='/api/equipment-type',
                       controller=WebService().get_equipment_types,
                       conditions={'method': ['GET']})

    dispatcher.connect(name='auth',
                       route='/api/user/login',
                       controller=WebService().login,
                       conditions={'method': ['POST']})

    conf = {
        '/': {
            'request.dispatch': dispatcher,
            'log.screen': True,
        }
    }

    cherrypy.engine.subscribe('start', setup_database)
    cherrypy.tree.mount(None, "/", config=conf)
    cherrypy.quickstart(None, config=conf)
