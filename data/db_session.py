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
    conn_str = 'postgres://izinsczieoazxy:cecdb4a5fed2d64bbf994f806ddb1851ad1d7d2e7d0f78c3c2f0fcd54e41eed7' \
               '@ec2-54-247-125-38.eu-west-1.compute.amazonaws.com:5432/dfv4vfqusmd2u9'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()