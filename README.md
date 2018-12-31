Creating the MySQL database:
Requires mysql-8.0.13:

```
    CREATE DATABASE ism_gw CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs;
```


Convert (mysql to sqlite)[https://github.com/dumblob/mysql2sqlite]:

```
    ./3rd_party_tools/mysql2sqlite dump_mysql.sql | sqlite3 mysqlite3.db
```
