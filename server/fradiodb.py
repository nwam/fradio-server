import MySQLdb

# Returns one row obtained from the query
def query(q, cols=None):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    cursor.execute(q)
    query_response = cursor.fetchone()

    return query_response

# Commits a query, returns number of rows changed
def transact(q):
    cursor = MySQLdb.connect(user='root', db='fradio').cursor()
    rows_changed = cursor.execute(q)
    cursor.commit()

    return rows_changed
