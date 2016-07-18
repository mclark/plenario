from sqlalchemy import Column, Integer, String
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from plenario.database import app_engine, Base, session


# These dictionaries help to keep me from making errors. If a message or
# status is misspelled, it will cause a fast and loud KeyError, saving me
# the trouble of weeding out the issue somewhere down the line.

ETLStatus = {
    'pending': 'Ingest Pending',
    'success': 'Success',
    'failure': 'Failure'
}

ETLType = {
    'dataset': 'master',
    'shapeset': 'shape'
}


class ETLTask(Base):
    """Store information about completed jobs pertaining to ETL actions."""

    __tablename__ = 'etl_task'
    id = Column(Integer, primary_key=True)
    dataset_name = Column(String, nullable=False, unique=True)
    status = Column(String)
    error = Column(String)
    type = Column(String)


def add_task(dataset_name, status, error, type_):
    """Used primarily in the views, called whenever a dataset is added
    by an administrator or a dataset is approved. Used to create a new
    ETLTask record.

    :param dataset_name: (string)
    :param status: (string) best to use a status from the ETLStatus dict
    :param error: (string) printout of an exception and traceback
    :param type_: (string) differentiates between tables, best to use a type
                           from the ETLType dict"""

    task = ETLTask(dataset_name=dataset_name,
                   status=status,
                   error=error,
                   type=type_)

    try:
        session.add(task)
        session.commit()
    except IntegrityError:
        session.rollback()


def update_task(dataset_name, status, error):
    """Used when a dataset completes or fails. Updates a single ETLTask.

    :param dataset_name: (string)
    :param status: (string) best to use a status from the ETLStatus dict
    :param error: (string) printout of an exception and traceback"""

    session.execute(
        update(
            ETLTask,
            values={ETLTask.status: status, ETLTask.error: error}
        ).where(ETLTask.dataset_name == dataset_name)
    )


def fetch_task(dataset_name):
    """Generally used for testing, selects a single ETLTask corresponding
    to some dataset.

    :param dataset_name: (string)"""

    q = "select * from etl_task where dataset_name = '{}'".format(dataset_name)
    return app_engine.execute(q).first()


def delete_task(dataset_name):
    """Also generally used for testing, deletes a ETLTask corresponding to some
    dataset.

    :param dataset_name: (string) a table name"""

    q = "delete from etl_task where dataset_name = '{}'".format(dataset_name)
    app_engine.execute(q)


def fetch_pending_tables(model):
    """Used in views.py, fetch all records corresponding to tables pending
    administrator approval. These tables exist in the master tables, but their
    corresponding records have not been ingested.

    :param model: (class) ORM Class corresponding to a meta table
    :returns: (list) contains all records for which is_approved is false"""

    query = session.query(model).filter(model.approved_status is not True)
    return query.all()


def fetch_table_etl_status(type_):
    """Used in views.py, fetch all records corresponding to tables that have
    entered the ETL process. Used to report successful, ongoing, or failed
    ETL tasks.

    :param type_: (string) designates what tasks to return
    :returns: (list) contains all records for datasets and ETL status"""

    q = "select * from etl_task where type = '{}'".format(type_)
    return app_engine.execute(q).fetchall()


if __name__ == '__main__':
    Base.metadata.create_all()
