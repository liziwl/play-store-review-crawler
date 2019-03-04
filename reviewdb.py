import sqlite3
import re
import time
import calendar
import csv

new_app_sql = """CREATE TABLE IF NOT EXISTS {}(
    USER VARCHAR(100) NOT NULL,
    RVTIME int NOT NULL,
    STAR int NOT NULL,
    COMMENT VARCHAR(1000),
    RESPONSER varchar (100),
    RESPONSE_TIME int,
    RESPONSE varchar (1000),
    UNIQUE(USER, RVTIME, STAR, COMMENT) ON CONFLICT REPLACE
);"""

drop_app_sql = "DROP TABLE IF EXISTS {};"

insert_com_sql = """INSERT INTO {} (USER,RVTIME,STAR,COMMENT,RESPONSER,RESPONSE_TIME,RESPONSE)
                VALUES ('{}',{},{},'{}',{},{},{});"""

select_app_sql = """SELECT USER, substr(datetime(RVTIME,'unixepoch'),1,10) as DATE, STAR, COMMENT,
                  RESPONSER,substr(datetime(RESPONSE_TIME,'unixepoch'),1,10) as RESPONSE_DATE,RESPONSE from {};"""


def get_star(star_str):
    return re.sub("\D", "", star_str)


def get_date(date_str):
    conv = time.strptime(date_str, "%B %d, %Y")
    # print(time.strftime("%d/%m/%Y",conv))
    return calendar.timegm(conv)


def insert_table(cursor, tb_name, data):
    # USER,RVTIME,STAR,COMMENT,RESPONSER,RESPONSE_TIME,RESPONSE
    tmp_data = []
    tmp_data.append(tb_name)
    tmp_data.extend(data)
    tmp_data[2] = get_date(tmp_data[2])
    tmp_data[3] = get_star(tmp_data[3])
    if len(data) > 4:
        tmp_data[5] = "'{}'".format(tmp_data[5])
        tmp_data[6] = get_date(tmp_data[6])
        tmp_data[7] = "'{}'".format(tmp_data[7])
    else:
        tmp_data.extend(['null', 'null', 'null'])
    exc_sql = insert_com_sql.format(*tmp_data)
    # print(exc_sql)
    cursor.execute(exc_sql)


def create_table(cursor, tb_name):
    exc_sql = new_app_sql.format(tb_name)
    print(exc_sql)
    cursor.execute(exc_sql)


def drop_table(cursor, tb_name):
    exc_sql = drop_app_sql.format(tb_name)
    print(exc_sql)
    cursor.execute(exc_sql)


class Reviewdb:
    def __init__(self, filepath='app_review.db'):
        self.conn = sqlite3.connect(filepath)
        self.cursor = self.conn.cursor()

    def _db_commit(self):
        self.conn.commit()

    def db_close(self):
        self.conn.close()

    def db_newtable(self, tb_name):
        create_table(self.cursor, tb_name)
        self._db_commit()

    def db_droptable(self, tb_name):
        drop_table(self.cursor, tb_name)
        self._db_commit()

    def db_insert_row(self, tb_name, data):
        insert_table(self.cursor, tb_name, data)
        self._db_commit()

    def db_select_table(self, tb_name):
        self.cursor.execute(select_app_sql.format(tb_name))
        rows = self.cursor.fetchall()
        return rows

    def dump_csv(self, tb_name):
        with open(tb_name + '.csv', "w", encoding="utf_8_sig", newline='') as app_review_file:
            f_csv = csv.writer(app_review_file)
            f_csv.writerow(["User", "Time", "Star", "Comment", "Responsor", "Response Time", "Response "])
            self.cursor.execute(select_app_sql.format(tb_name))
            rows = self.cursor.fetchall()
            f_csv.writerows(rows)


if __name__ == '__main__':
    rdb = Reviewdb()
    # rdb.cursor.execute(select_app_sql.format("com_owncloud_android"))
    # rows = rdb.cursor.fetchall()
    # print(rows)
    rdb.dump_csv("it_feio_android_omninotes")
    rdb.db_close()
