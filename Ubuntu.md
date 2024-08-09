

### 一、环境简介

硬件信息：
- CPU：n100
- 内存：16G
- 系统：Ubuntu 20.04

用户管理：
- `su [user]`：切换用户。不带用户名称时，会尝试切换到root账号；
- `passwd [user]`：修改某个用户的密码。
- `id [user]`：查看用户所在用户组信息。不带用户名称时，则查询当前用户所在用户组信息
- `adduser [user]`：创建新用户（系统生成默认配置）
- `useradd [options] [user]`：创建新用户（普通用户添加新用户，可自主配置）
- `usermod [options] [user]`：修改用户相关信息
- `chown [options]... [owner][:[group]] FILE...`：修改文件所属用户信息

进程管理：
- `sudo lsof -i :[port]`：查看目标端口号的应用
- `sudo netstat -a | grep [port]`：查看目标端口号占用情况

### 二、开机自启

Linux系统开机启动顺序：
1. 加载BIOS（Basic Input Output System，基本输入输出系统）
2. 读取MBR（Master Boot Record，主引导记录）
3. 运行 BootLoader，初始化硬件设备
4. 加载内核
5. 运行 init 程序。设置开机启动项将在这一步执行！
6. 执行`/bin/login`程序，进入登录状态

#### 背景介绍

通常 CentOS、Ubuntu 早期版本Linux系统开机自动加载程序或者脚本，我们都放在 /etc/rc.local 执行。
拿 Ubuntu系统来说，Ubuntu 16.04 版本开始去除了 rc.local 文件，自启动服务方面基本由 systemd 全面接管了。

在 init 系统模式下，内核调用 init 进程后会首先获取系统运行级别（run-level）的信息。
这里的运行级别共有 0~6 共七种（级别非优先级而是运行模式）：
- 0：关机
- 1：单用户模式
- 2：多用户模式，没有网络支持
- 3：多用户模式，有网络支持
- 4：保留，未使用
- 5：X11，与运行级别 3 类似，但加载使用 X-windows 支持的图形界面
- 6：重启

> 使用模式：`sudo init n`，譬如我们要重启，可以执行`sudo init 6`


#### systemd优先级

systemd的使用可提高系统服务的运行效率, 而unit文件主要存在以下三个目录（按照启动优先级排序）：
- `/etc/systemd/system`
- `/run/systemd/system`
- `/lib/systemd/system`


#### 使用 rc-local.service

rc-local.service 是系统自带的一个开机自启服务， 但是在 Ubuntu20 的 systemd 启动方式下，该服务默认没有开启。

1. 开启 rc-local.service

在`/usr/lib/systemd/system/rc-local.service`文件中添加以下内容：
```bash
[Install]
WantedBy=multi-user.target
Alias=rc-local.service
```

此时完整的rc-local.service样例如下

```bash
[Unit]
Description=/etc/rc.local Compatibility
Documentation=man:systemd-rc-local-generator(8)
ConditionFileIsExecutable=/etc/rc.local
After=network.target

[Service]
Type=forking
ExecStart=/etc/rc.local start
TimeoutSec=0
RemainAfterExit=yes
GuessMainPID=no

[Install]
WantedBy=multi-user.target
Alias=rc-local.service
```

2. `[可选]`提高 rc-local.service 启动优先级

迁移到etc相关目录：`mv /usr/lib/systemd/system/rc-local.service /etc/systemd/system/`

3. 新建 rc.local 文件

ubuntu20.04的 /etc 目录默认是没有 `rc.local` 文件，可新建一个。
```bash
touch /etc/rc.local

chmod 755 /etc/rc.local

```

4. rc.local 文件启动样例

这里以开机启动nexus为例，样例内容如下：
```bash
#!/bin/bash

# 通过xxx用户来启动nexus服务
runuser -l xxx -c '/home/xxx/library/nexus-3.68.1-02/bin/nexus start'

exit 0
```

5. 查看状态

运行命令`systemctl status rc-local.service`，显示如下内容：
```
● rc-local.service - /etc/rc.local Compatibility
     Loaded: loaded (/lib/systemd/system/rc-local.service; enabled-runtime; vendor preset: enabled)
    Drop-In: /usr/lib/systemd/system/rc-local.service.d
             └─debian.conf
     Active: active (exited) since Wed 2024-06-19 11:32:12 CST; 7h ago
       Docs: man:systemd-rc-local-generator(8)
    Process: 797 ExecStart=/etc/rc.local start (code=exited, status=0/SUCCESS)

6月 19 11:32:12 n100 systemd[1]: Starting /etc/rc.local Compatibility...
6月 19 11:32:12 n100 systemd[1]: Started /etc/rc.local Compatibility.
```

部分字段说明：
- Loaded：显示加载状态、服务地址等
- Active：显示服务可用值与当前运行状态