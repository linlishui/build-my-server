

#### Ubuntu系统安装Mysql

安装与配置流程如下：
- 输入`sudo apt update`更新依赖环境信息
- 执行`sudo apt install mysql-server`安装Mysql
- 输入`systemctl status mysql.service`查看Mysql服务是否启动
- 修改登录方式。解决ERROR 1698 (28000): Access denied for user 'root'@'localhost'报错：
	- 以管理员身份进入mysql：`sudo mysql`
	- 修改密码：`alter user 'root'@'localhost' identified with mysql_native_password 'custom_passwd';`
	- 通过密码形式登录root用户进入mysql：`mysql -u root -p`


#### Windows系統安裝Mysql

安装与配置流程如下：
- 官网下载mysql压缩包，笔者这里是`mysql-8.0.39-winx64`版本
- 解压到应用目录后，新建**my.ini**文件，按需配置。以下是笔者的配置内容：
	```
	[mysqld]
	; 设置3306端口
	port=3306
	; 设置mysql的安装目录
	basedir=D:\\Program Files\\mysql-8.0.39-winx64
	; 设置mysql数据库的数据的存放目录
	datadir=F:\\AppData\\Mysql
	; 允许最大连接数
	max_connections=200
	; 允许连接失败的次数。这是为了防止有人从该主机试图攻击数据库系统
	max_connect_errors=10
	; 服务端使用的字符集默认为UTF8
	character-set-server=utf8
	; 创建新表时将使用的默认存储引擎
	default-storage-engine=INNODB
	; 默认使用插件认证（caching_sha2_password）
	default_authentication_plugin=mysql_native_password

	[mysql]
	; 设置mysql客户端默认字符集
	default-character-set=utf8

	[client]
	; 设置mysql客户端连接服务端时默认使用的端口
	port=3306
	default-character-set=utf8
	```

- 以管理员身份打开控制台，进入mysql的安装目录
- 进入mysql的bin目录，执行`mysqld --initialize --console`命令。记录生成的临时root密码
- 执行`mysqld --install`命令安装mysql服务
- 执行`net start mysql`命令启动mysql服务
- 输入`mysql -u root -p`，使用初始密码登录mysql
- 输入`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'custom_passwd';`修改密码


#### 常用命令

- `show databases;`：列出数据库
- `select database();`：当前数据库
- `use [database_name]`：打开数据库
- `show tables;`：列出数据表
- `desc [table_name];`：查看表结构
- `show create table [table_name];`：查看创建表的sql语句


数据库中常用SQL语句：
```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS <database_name>
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_general_ci;

-- 删除数据库
DROP DATABASE IF EXISTS <database_name>;

-- 删除数据表
DROP TABLE IF EXISTS <table_name>;
```