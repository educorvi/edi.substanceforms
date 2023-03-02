import psycopg2

class DBConnect(object):
    def __init__(self, host, db, user, password):
        self.host=host
        self.db=db
        self.user=user
        self.password=password

    def connect(self):
        self.conn = psycopg2.connect(host=self.host,
                                    dbname=self.db,
                                    user=self.user,
                                    password=self.password)

    def execute(self, command):
        results = False
        cur = conn.cursor()
        cur.execute(command)
        method = command.split(" ")[0]
        if method == "SELECT":
            results = cur.fetchall()
        elif method in ["INSERT", "UPDATE"]:
            results = self.conn.commit()
        elif method == "DELETE":
            results = self.conn.commit()
        cur.close()
        return results

    def close(self):
        self.conn.close()
