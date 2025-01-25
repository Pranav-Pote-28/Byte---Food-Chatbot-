import mysql.connector
global cnx

cnx=mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="pandeyji_eatery"
)

def get_order_status(order_id :int):
    cursor=cnx.cursor()

    query=("SELECT status FROM order_tracking WHERE order_id=%s")
    cursor.execute(query,(order_id,))

    result=cursor.fetchone()
    cursor.close()
    # cnx.close()

    if result is not None:
        return result[0]
    else:
        return None



