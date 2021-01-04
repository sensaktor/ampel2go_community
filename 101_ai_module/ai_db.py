
""" This is the ai_db module containing the class AiDatabase """

from datetime import datetime
import logging
from sqlalchemy import create_engine, Table, Column, Integer, DateTime,  MetaData



#--------------------------------------------------------------------------------------------------#
class AiDatabase:
    "All methods relating to the database connection"
    def __init__(self, sql_connection):
        # Initialize sqlAlchemy
        # CONN = create_engine( \
        #   'sqlite:////home/jetson/Desktop/ampel2go_code/104_user_display/db.sqlite3')

        self.logger = logging.getLogger('ai_db_logger')
        self.logger.info('creating an instance of Auxiliary')
        self.CONN = create_engine(sql_connection)
        self.META_DATA = MetaData(bind=self.CONN)
        self.MAIN_OCCUPANCY = Table(
            'main_occupancy', self.META_DATA,
            Column('id', Integer, primary_key=True),
            Column('capacity', Integer), Column('date', DateTime),
            Column('person_count', Integer),
            Column('direction', Integer),
            )

        self.MAIN_AREATHRESHOLD = Table(
            'main_areathreshold', self.META_DATA,
            Column('id', Integer, primary_key=True),
            Column('area_threshold', Integer),
            )
        self.logger.info( "Current occupancy: %s", str(self.get_occupancy()) )

    def get_max_id(self):
        "gets the last entry of the db (i.e. the one with the highest id"
        with self.CONN.connect() as connection:
            result = connection.execute("select max(id) as maxid from main_occupancy")
            for row in result:
                max_id = row['maxid']
            return max_id

    def clean_db(self):
        "Removes all entries in DB, except the last one"
        with self.CONN.connect() as connection:
            with connection.begin():
                result = connection.execute( \
                    "select max(id) as maxid, count(*) as cnt from main_occupancy")
                for row in result:
                    max_id = row['maxid']
                    row_cnt = row['cnt']
                    self.logger.info("clean_db: rows %s , max_id: %s ", row_cnt, max_id)
                result = connection.execute( \
                    "delete from main_occupancy where id <>'" + str(max_id)+"' ")
                return

    def get_occupancy(self):
        "gets the value for the current occupancy"
        with self.CONN.connect() as connection:
            max_id = self.get_max_id()
            person_count = 0
            result = connection.execute( \
                "select person_count from main_occupancy where id ='" + str(max_id) + "' ")
            for row in result:
                person_count = row['person_count']
            return person_count

    def set_occupancy(self, person_count):
        "sets the value for the occupancy "
        with self.CONN.connect() as connection:
            max_id = self.get_max_id()
            # placeholder for result b/c pylint
            _ = connection.execute( "update main_occupancy set person_count = " \
                + str(person_count) + " where id ='" + str(max_id) + "' ")
            self.logger.info("DB-set occupancy: ", person_count)
            return

    def get_area_threshold(self):
        "gets area threshold parameter from db"
        with self.CONN.connect() as connection:
            result = connection.execute( \
                "select area_threshold from main_areathreshold")
            for row in result:
                area_threshold = row['area_threshold']
            return area_threshold

    def get_current_data(self):
        "get latest values of all three fields from main_occupancy table"
        with self.CONN.connect() as connection:
            max_id = self.get_max_id()
            result = connection.execute( \
                "select capacity,person_count, direction from main_occupancy where id ='" \
                    + str(max_id)+"' ")
            for row in result:
                capacity = row['capacity']
                latest_person_count = row['person_count']
                direction = row['direction']
            return capacity, latest_person_count, direction

    def set_current_data(self, capacity, person_count, direction):
        "write values to all three fields of the main_occupancy table"
        with self.CONN.connect() as connection: #klaus: why is connection here unused?
            now = datetime.now()
            now = now.replace(microsecond=0)
            insert = self.MAIN_OCCUPANCY.insert().values(capacity=capacity \
                , date=now, person_count=person_count, direction=direction)
            self.CONN.execute(insert)
            #self.logger.info("DB-set current data: ", person_count)
            return
#--------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    SQL_CONNECTION = 'sqlite:///../104_user_display/db.sqlite3'
    ai_db = AiDatabase(SQL_CONNECTION)
    logger = logging.getLogger('ai_db_logger')

    def add_occupancy(num):
        "small test for occupancy"
        oc1 = ai_db.get_occupancy()
        oc2 = oc1 + num
        ai_db.set_occupancy(oc2)
        oc3 = ai_db.get_occupancy()
        passed = oc2 == oc3
        logger.info("Occupancy Pass: %s , Add/Before/Calc/After: %s %s %s %s" , str(passed) \
            , str(num), str(oc1),str( oc2 ), str(oc3 ))
        return passed

    for i in [1, 10, -5, -6]:
        add_occupancy(i)

    capacity, latest_person_count, direction = ai_db.get_current_data()
    logger.info("capacity: %s, latest_person_count: %s , direction: %s", capacity \
        , latest_person_count, direction)
    ai_db.set_current_data(capacity+1, latest_person_count+1, direction+1)
    capacity, latest_person_count, direction = ai_db.get_current_data()
    logger.info("capacity: %s, latest_person_count: %s , direction: %s", capacity \
        , latest_person_count, direction)
    ai_db.set_current_data(capacity-1, latest_person_count-1, direction-1)
    capacity, latest_person_count, direction = ai_db.get_current_data()
    logger.info("capacity: %s, latest_person_count: %s , direction: %s", capacity \
        , latest_person_count, direction)
    logger.info("Test ended.")
