import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    conn_str = 'postgres://owldriiwmspbrz:8e3649d6f77407b0ad8e146b7574c3f4ddade81cd0bf21a067651b5da5eed596@ec2-52-31-' \
               '94-195.eu-west-1.compute.amazonaws.com:5432/d8js8cf6v7shdn'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()