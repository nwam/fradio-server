import MySQLdb

# Returns one row obtained from the query
def query(q, args=None, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q, args)
    query_response = cursor.fetchone()

    return query_response

# Returns one row obtained from the query
def query_all(q, args=None, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q, args)
    query_response = cursor.fetchall()

    return query_response

# Commits a query, returns number of rows changed
def transact(q, args=None):
    connection = MySQLdb.connect(user='root', db='fradio')
    cursor = connection.cursor()
    rows_changed = cursor.execute(q, args)
    connection.commit()

    return rows_changed
