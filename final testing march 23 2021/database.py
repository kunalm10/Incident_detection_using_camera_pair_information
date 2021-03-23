import pymysql
# from sshtunnel import SSHTunnelForwarder
import os

root = {'host': '149.166.99.237',
        'database': 'indot_db_10-08-2020',
        'user': 'iuindot',
        'pass': 'indot_Passwd_2019'}

other = {'user': 'root', 'pass': 'zanpaktao'}

tables = {

    'ip_address':
        "ip_id` int(11) NOT NULL,"
      "camera_id` int(11) DEFAULT NULL,"
      "stream_link` varchar(45) DEFAULT NULL,"
      "created_date` datetime DEFAULT NULL,"
      "updated_date` datetime DEFAULT NULL,"
      "PRIMARY KEY (`ip_id`),"
      "KEY `camera_id_idx` (`camera_id`),"
      "CONSTRAINT `camera_id` FOREIGN KEY (`camera_id`) REFERENCES `camera_list` (`camera_id`),"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8",

}

fields = {


    'ip_address':
        "ip_id,"
        "camera_id,"
        "stream_link,"
        "created_date,"
        "updated_date",


}

sql_queries = dict()


def init_insert_queries():
    global sql_queries
    for table_name, columns in fields.items():
        q = "INSERT INTO " + table_name + " (" + columns + ") VALUES " + \
            "(" + ",".join(["%s"] * len(columns.split(","))) + ")"
        sql_queries[table_name] = q


def get_connection():
    print("Connecting...")
    # tunnel = None
    # try:
    #     tunnel = SSHTunnelForwarder(
    #             ('in-engr-indot.engr.iupui.edu', 22),
    #             ssh_username='zd2',
    #             ssh_password='Allan@870630zmd',
    #             remote_bind_address=('127.0.0.1', 3306),
    #             )
    # except:
    #     print('false')
    # print(type(tunnel))
    # tunnel.start()
    cnx = pymysql.connect(user=root.get("user"),
                          password=root.get("pass"),
                          database=root.get("database"),
                          host=root.get("host"),
                          port=3306,  # tunnel.local_bind_port,
                          )
    print("Connected")
    init_insert_queries()
    return cnx


def create_tables(cnx_cursor):
    for table in tables:
        cnx_cursor.execute(table)


def update_tables(cnx, cnx_cursor, queries):
    global sql_queries
    for q in queries:
        cnx_cursor.execute(sql_queries[q[0]], q[1:])
    cnx.commit()


def delete_entries(cnx_cursor, table_names, conditions):
    for name in table_names:
        cnx_cursor.execute("DELETE FROM " + name + (("WHERE " + conditions[name]) if name in conditions else ''))


def drop_all_tables(cnx_cursor):
    cnx_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in fields:
        cnx_cursor.execute("DROP TABLE IF EXISTS " + table)


def save_static_tables(folder):
    cnx, t = get_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM camera")
    with open(os.path.join(folder, "camera.txt"), "wt") as f:
        for i in cursor.fetchall():
            f.write(str(i))
            f.write('\n')
    cursor.execute("SELECT * FROM road")
    with open(os.path.join(folder, "road.txt"), "wt") as f:
        for i in cursor.fetchall():
            f.write(str(i))
            f.write('\n')
    cursor.execute("SELECT * FROM location")
    with open(os.path.join(folder, "location.txt"), "wt") as f:
        for i in cursor.fetchall():
            f.write(str(i))
            f.write('\n')
    cursor.execute("SELECT * FROM ip_address")
    with open(os.path.join(folder, "ip_address.txt"), "wt") as f:
        for i in cursor.fetchall():
            f.write(str(i))
            f.write('\n')


def get_table_names(cnx_cursor):
    cnx_cursor.execute("SHOW TABLES")
    return [table for (table,) in cnx_cursor.fetchall()]


def insert(cnx, cnx_cursor, query):
    cnx_cursor.execute(sql_queries[query[0]], tuple(query[1:]))
    cnx.commit()


def insert_all(cnx, cnx_cursor, queries):
    for q in queries:
        insert(cnx, cnx_cursor, q)


if __name__ == '__main__':
    cursor.execute("SELECT * FROM lane_condition")
    # lc = cursor.fetchall()
    # for i in lc:
    #     print(i)
# cursor.execute(
# "SELECT flow_rate, density "
# "FROM lane_condition "
# 'WHERE camera_location_view_road_id IN (SELECT camera_id FROM ip_address WHERE ip_address="rtsp://10.10.0.211/"), '
# 'location_id IN (SELECT location_id FROM ip_address WHERE ip_address="rtsp://10.10.0.211/")', multi=True)
# for i in cursor.fetchall():
#     print(i)
# cursor.execute("SELECT * FROM camera")
# entries = cursor.fetchall()
# for e in entries:
#     print(e)
# cursor.execute("SELECT * FROM road")
# entries = cursor.fetchall()
# for e in entries:
#     print(e)
# cursor.execute("SELECT * FROM location")
# entries = cursor.fetchall()
# for e in entries:
#     print(e)
# cursor.execute("SELECT * FROM camera_location_view")
# entries = cursor.fetchall()
# for e in entries:
#     print(e)
# cursor.execute("SELECT * FROM camera_location_view_road")
# entries = cursor.fetchall()
# for e in entries:
#     print(e)
# drop_tables(cursor)
# create_tables(cursor)
#
# insert(cnx, cursor, ('camera', "9C353B5F4CD7", "rtsp://10.10.0.211/", "Logtech", "T35001", "1080", "1296", "140", "25",
#                             "2018-04-08 13:45:45", "2019-04-08 13:45:45", "active"))
# insert(cnx, cursor, ('camera', "9C353B5F4CD7", "rtsp://10.10.0.32:8554/swVideo", "Logtech", "T35001", "1080", "1296",
#                             "140", "25", "2018-04-08 13:45:45", "2019-04-08 13:45:45", "active"))
# insert(cnx, cursor, ('camera', "9C353B5F4CD7", "rtsp://10.10.0.43:8554/swVideo", "Logtech", "T35001", "1080", "1296",
#                             "140", "25", "2018-04-08 13:45:45", "2019-04-08 13:45:45", "active"))
#
# insert(cnx, cursor, ('road', "I-65", "I-65 @ Southern Ave. - Mile 108.4"))
# insert(cnx, cursor, ('road', "I-65", "Camera 469 I-65 @ 248.0"))
# insert(cnx, cursor, ('road', "I-65", "Camera 472 I-65 @ 235.0"))
#
# insert(cnx, cursor, ('location', "Southern Ave", "39.727772", "-86.135454", None, None))
# insert(cnx, cursor, ('location', None, "0", "0", None, None))
# insert(cnx, cursor, ('location', None,  "0", "0", None, None))
#
# insert(cnx, cursor, ('ip_address', "rtsp://10.10.0.211/", "1", "1"))
# insert(cnx, cursor, ('ip_address', "rtsp://10.10.0.32:8554/swVideo", "2", "2"))
# insert(cnx, cursor, ('ip_address', "rtsp://10.10.0.43:8554/swVideo", "3", "3"))
#
#
# insert(cnx, cursor, ('camera_location_view', '1', '1', '0', '30', '40', '80', '320', '2018-04-08 13:45:45'))
# insert(cnx, cursor, ('camera_location_view', '2', '2', '0', '30', '40', '80', '320', '2018-04-08 13:45:45'))
# insert(cnx, cursor, ('camera_location_view', '3', '3', '0', '30', '40', '80', '320', '2018-04-08 13:45:45'))
#
# insert(cnx, cursor, ('camera_location_view_road', '1', '1', 'highway', '70', '3', None, None, None, None, None, None))
# insert(cnx, cursor, ('camera_location_view_road', '2', '2', 'highway', '70', '3', None, None, None, None, None, None))
# insert(cnx, cursor, ('camera_location_view_road', '3', '3', 'highway', '70', '3', None, None, None, None, None, None))
