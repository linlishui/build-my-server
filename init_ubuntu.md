
## 系统安装

系统版本：Ubuntu2204

分区方案（1TB）：
- 启动分区`/boot/efi`：500MB
- 交换分区`swap`：设备内存32GB，分配了32GB
- 系统分区`/`：120GB
- 主分区`/home`：剩余的存储空间



## 基础环境及配置

```shell

# 同步双系统时间
timedatectl set-local-rtc 1

# 禁用所有snap包的自动更新
sudo snap refresh --hold

# 常用工具：vim、net-tools
sudo apt install vim net-tools

# Git
sudo apt install git
git config --global user.name [your_name]
git config --global user.email [your_email]

# 生成ssh公钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# Java
sudo apt install openjdk-11-jre-headless

# OpenVPN
sudo apt-get install openvpn

```

### apt

**替换成国内源**
```shell
# 1. 运行以下命令，备份原软件源
sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak

# 2. 运行以下命令，新建并打开配置文件
sudo vim /etc/apt/sources.list

# 3. 按i进入编辑模式，为配置文件添加以下信息(以Ubuntu2204为例)
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse

# deb https://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse

deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
deb-src https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse

# 4. 按Esc键，输入:wq，按Enter键关闭并保存配置文件

# 5. 运行以下命令，更新软件包信息库。
sudo apt update

```

**apt常用命令**
```shell
# 刷新软件源列表
sudo apt update

# 升级所有可升级的软件包
sudo apt upgrade

# 智能地完成系统升级(升级整个系统)
sudo apt full-upgrade

# 安装一个或多个软件包
sudo apt install <包名>

# 修复损坏的依赖关系
sudo apt -f install

# 移除一个或多个软件包。但会保留其配置文件
sudo apt remove <包名>

# 完全移除一个或多个软件包。同时删除软件包及其配置文件
sudo apt purge <包名>

# 自动移除不再需要的依赖包
sudo apt autoremove

# 清理已下载的旧版本软件包缓存
sudo apt autoclean

# 清理所有已下载的软件包缓存(清空 /var/cache/apt/archives/ )
sudo apt clean

# 在软件源中搜索包含关键词的软件包
apt search <关键词>

# 显示某个软件包的详细信息
apt show <包名>

# 列出所有可以升级的软件包
apt list --upgradeable

# 列出所有已安装的软件包
apt list --installed

``` 

**dpkg底层包管理器**
```shell
# 安装一个本地的 .deb 软件包
sudo dpkg -i <package.deb>

# 移除一个已安装的软件包
sudo dpkg -r <包名>

# 完全清除一个已安装的软件包
sudo dpkg -P <包名>

# 列出所有已安装的软件包
dpkg -l

# 列出一个已安装的软件包都安装了哪些文件到系统里，以及文件的安装位置
dpkg -L <包名>

# 显示一个已安装软件包的详细状态信息
dpkg -s <包名>

# 查询系统中的某个文件是由哪个软件包安装的
dpkg -S <文件名>

# 查看一个 .deb 文件内部包含哪些文件
dpkg --contents <package.deb>
```

### .bashrc配置

在用户的`.bashrc`文件增加如下内容：
```bash

# CUSTOM

## environment 

### JDK
export JDK11_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export JAVA_HOME=$JDK11_HOME
export PATH=$JAVA_HOME/bin:$PATH

### Android
export ANDROID_HOME=/home/water/Android/Sdk
export PATH=${PATH}:${ANDROID_HOME}/tools
export PATH=${PATH}:${ANDROID_HOME}/platform-tools


## server
export N100='user@192.168.1.123'

## custom alias
alias vpn='sudo openvpn --config <client.ovpn>'

alias n100='ssh $N100'

alias gst='git status'
alias gcount='git rev-list --count HEAD'

alias aps='adb shell ps -A'
alias aty='adb logcat -b events | grep -i on_resume'

```

> **PATH值**初始化数据路径：`/etc/environment`


### Vim配置

- 用户配置路径：`~/.vimrc`
- 全局配置路径：`/etc/vim/vimrc`

配置内容如下：
```shell

" 默认展示行号
set nu

```



## 常见问题

### 1. 系统提示进入飞行模式，并且无线网卡在开机启动时报错-110
禁用 Windows 快速启动（适用于双系统用户），Windows 的“快速启动”功能可能会在关机时锁定无线网卡，导致 Ubuntu 无法正常使用它。

- 在 Windows 中搜索并打开“控制面板”。
- 选择“电源选项” > “选择电源按钮的功能”。
- 点击“更改当前不可用的设置”。
- 在下方的“关机设置”中，取消勾选“启用快速启动（推荐）”。
- 保存修改后彻底关闭Windows（非重启），再启动进入Ubuntu查看问题是否解决。