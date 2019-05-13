import mysql.connector
from mysql.connector import errorcode
import config as cfg

class DbManager(object):
    '''
    Class to handle MySQL Db
    '''

    def __init__(self):
        self.cnx = None
        self.db_schema = cfg.config["db_schema"]

    def connect(self, user, password, host, db):
        try:
            self.cnx = mysql.connector.connect(user=user, password=password, host=host, database=db)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            raise (err)

    def generate_insert_query(self, table_name, column_dict):
        cols = []
        vals = []
        table_name = self.db_schema + "." + table_name
        for col, val in column_dict.items():
            cols.append(col)
            vals.append(val)

        query_str = "INSERT INTO {} ({}) VALUES ({})".format(
            table_name,
            ','.join(cols),
            ','.join(['%s'] * len(cols))
        )
        return query_str, tuple(vals)

    def insert_browser_detail(self, column_dict):
        (query_string, query_data) = self.generate_insert_query("browser_master", column_dict)
        db_cursor = self.cnx.cursor()
        try:
            db_cursor.execute(query_string, query_data)
            row_id = db_cursor.lastrowid
            self.cnx.commit()
        except Exception as e:
            print "Failed to insert browser detail"
            raise (e)
        finally:
            db_cursor.close()
        return row_id

    def insert_data(self, result, tc_detail_result):
        cursor = self.cnx.cursor()
        (query_string, query_data) = self.generate_insert_query("test_results_summary", result)
        try:
            # Insert Test Summary
            cursor.execute(query_string, query_data)
            last_row_id = cursor.lastrowid

            # Insert Test detail
            for tc in tc_detail_result:
                tc['test_summary_id'] = int(last_row_id)
                tc['root_cause'] = ""
                if len(tc["error_log"]) > 1:
                    tc["error_log"] = self.cnx.converter.escape(tc["error_log"])
                (query_string, query_data) = self.generate_insert_query("test_results_detail", tc)
                cursor.execute(query_string, query_data)
            self.cnx.commit()
            return True
        except Exception as e:
            print "Test results are failed insert.", e
            self.cnx.rollback()
        finally:
            cursor.close()

        return False

    def close(self):
        self.cnx.close()

    def get_results(self, sp_name, params):
        sp_name = self.db_schema + "." + sp_name
        my_cursor = self.cnx.cursor()
        my_cursor.callproc(sp_name, params)
        query_result = [result.fetchall() for result in my_cursor.stored_results()]
        return query_result
