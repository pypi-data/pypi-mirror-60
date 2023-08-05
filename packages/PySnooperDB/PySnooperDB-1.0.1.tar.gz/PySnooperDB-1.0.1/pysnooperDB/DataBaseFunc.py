import mysql.connector

class DB():
    def __init__(self, user='root', passwd='08191920.yh',db=''):
        self.conn = mysql.connector.connect(user=user,passwd=passwd,database=db)
        self.cur = self.conn.cursor()
 
    def __enter__(self):
        return self.cur
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()


def create_table(tablename, user='root', passwd='08191920.yh',databasename = 'TESTDB'):
    with DB(user = user, passwd = passwd, db= databasename) as db: 
        sql_drop = "DROP TABLE IF EXISTS `%s`" % (tablename)
        db.execute(sql_drop)
        sql_create = """CREATE TABLE `%s` (
                recordid INT NOT NULL AUTO_INCREMENT,
                code VARCHAR(255),
                codeline VARCHAR(255),
                PRIMARY KEY ( recordid )  )character set = utf8""" % (tablename)
        db.execute(sql_create)
   
def insert_table(tablename, observelist, name, value, code, codeline,\
         user='root', passwd='08191920.yh', databasename = 'TESTDB'):
    name = str(name)
    value = str(value).replace("'",'')
    code = str(code).replace("'",'')
    codeline = str(codeline)
    
    refuselist = ["args","kwargs","function","self"]
    if name in refuselist:
        return 0
    if observelist:
        if name not in observelist:
            return 0
    with DB(user = user, passwd = passwd, db= databasename) as db: 
        # 获取列名
        db.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = db.fetchall()
        columns = [column[0] for column in answer]
        if not name in columns:
            sql_add = "ALTER TABLE `%s` ADD `%s` VARCHAR(255)" % (tablename, name)
            db.execute(sql_add)
            columns.append(name)

        # 开始插入，复制上一行，只把name值改为value
        sql_select = "select * from `%s` order by recordid desc limit 1;" % (tablename)
        db.execute(sql_select)
        record_last = db.fetchone()
        if not record_last: #若为空表
            record_last = [None,None,None,None] 

        num = len(columns)
        record_last = list(record_last)
        for i in range(3):
            columns.pop(0)
            record_last.pop(0)

        for i in range(len(columns)):
            if columns[i] == name:
                record_last[i] = value

        ls1 = [str(i) for i in columns]
        ls1 = '`,`'.join(ls1)
        ls1 = "`"+ls1 + "`"
        ls2 = [str(i) for i in record_last]
        ls2 = "','".join(ls2) 
        ls2 = "'"+ls2 + "'"
        ls2 = ls2.replace("'None'","NUll")

        sql_insert = "INSERT INTO " + tablename + "(code, codeline, " \
            + ls1 + ") VALUES ('"+ code +"','" + codeline + "'," + ls2 + ")"   
        db.execute(sql_insert)

def delete_table(tablename, user='root', passwd='08191920.yh',databasename = 'TESTDB'):
    with DB(user = user, passwd = passwd, db= databasename) as db: 
        sql_drop = "DROP TABLE IF EXISTS `%s`" % (tablename)
        db.execute(sql_drop)  

def show_tablename(user='root', passwd='08191920.yh',databasename = 'TESTDB'):
    with DB(user = user, passwd = passwd, db= databasename) as db: 
        db.execute("SHOW TABLES")
        answer = db.fetchall()
        columns = [column[0] for column in answer]
        columns.insert(0,"Tables_in_%s" %(databasename))
    return columns


def show_table(tablename, user='root', passwd='08191920.yh',databasename = 'TESTDB'):
    # 获取列名
    with DB(user = user, passwd = passwd, db= databasename) as db: 
        db.execute("SHOW COLUMNS from `" + tablename + "`")
        answer = db.fetchall()
        columns = [column[0] for column in answer]

    with DB(user = user, passwd = passwd, db= databasename) as db: 
        sql_select = "select * from `%s`" % (tablename)
        db.execute(sql_select)  
        rows = db.fetchall()
        row = db.rowcount
        col = len(rows[0])

    result = []
    result.append(columns)

    for i in range(row):
        result_line = []
        for j in range(col):
            result_line.append(rows[i][j])
        result.append(result_line)
    return result