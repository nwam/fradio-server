import MySQLdb

# Returns one row obtained from the query
def query(q, args, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q, args)
    query_response = cursor.fetchone()

    return query_response

# Commits a query, returns number of rows changed
def transact(q, args):
    connection = MySQLdb.connect(user='root', db='fradio')
    cursor = connection.cursor()
    rows_changed = cursor.execute(q, args)
    connection.commit()

    return rows_changed
