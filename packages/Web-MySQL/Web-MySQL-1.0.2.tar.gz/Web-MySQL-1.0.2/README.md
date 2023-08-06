
# Web-MySQL
A pure Python MySQL connect tool which base on PyMySQL

A toolkit that simplifies the operation of use Python to connecting to MySQL database in Web development. It can be used in undersize Flask or Django project or other small porject.

### [中文介绍](#中文介绍)

[Introduction in Chinese](https://www.arukione.com/2020/01/29/%E5%9F%BA%E4%BA%8EPyMySQL%E6%9E%84%E5%BB%BA%E7%9A%84Web-MySQL/)

### [Installation](#installation)

use pip to install this package:

`$ pip3 install Web-MySQL`

use pip to upgrade Web-MySQL:

`$ pip3 install --upgrade Web-MySQL`

### [Instruction](#Instruction)

Just set MySQL settings than you can use fetchone,fetchall,executor function to operate MySQL database in Python3.

You can input sql command string and values list which format is as follows:

```Python
sql = "insert into users (name,age) values (%s,%s);"
values = ['your_name',11]
```
Than these function will use PyMySQL to execute the sql command to operate MySQL database.

```Python
# executor function only execute the sql command and it will not return anything.
def executor(sql,values=None):
  ...
 
# fetchone function will execute the select sql command and fetch the first select result.
def fetchone(sql,values=None):
 ...
 return fetch_result

# fetchall function will execute the select sql command and fetch all select result as list.
def fetchall(sql,values=None):
  ...
  return fetch_result
```

The database operation can be performed by calling the corresponding function with passing in the SQL command and 'values'. When there are no variables to be passed in SQL command, 'values' don't need to be passed in.

### [Example](#Example)

We can configure the database and use the recommended usage to use functions as follows.

Create a golbal Connector instance, and modify the corresponding variables which are database connection information;

```Python
from web_mysql import Connector

connector = Connector()
connector.host = "localhost"
connector.user = "root"
connector.password = "123456"
connector.database = "test"

def insert_user():
  sql = "insert into users (name,id) values (%s,%s);“
  values = ["name", 10001]
  connector.executor(sql, values)

def get_user(name, id):
  sql = "select * from users where name=%s and id=%s;"
  values = [name, id]
  user = connector.fetchone(sql, values)

def get_users():
  sql = "select * from users;"
  all_user = connector.fetchall(sql)
```

### [Suggest](#Suggest)

You can create a Connector instance in a independent Python file or Python class, we don't advice you create multiple instances in the same file or class, it's bad for maintenance. If you want have multiple different instance to operate different databases, you should have multiple files or classes to hold it.

1.0.0
---

2020/1/29  正式发布
