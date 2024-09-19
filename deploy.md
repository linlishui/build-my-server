


### Ubuntu部署SpringBoot项目

在`/lib/systemd/system`目录下，SpringBoot项目应用以系统服务进行管理。

这里以`n100-server.service`文件样例进行说明：

```
[Unit]
Description=N100 Spring Boot Application
After=syslog.target network.target

[Service]
User=water
# 工作目录
WorkingDirectory=/home/water/n100-server
# 执行命令
ExecStart=java -jar n100-server-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
# 143是Spring Boot应用在接收到SIGTERM信号时的标准退出代码
SuccessExitStatus=143

[Install]
WantedBy=multi-user.target
Alias=n100-server.service
```

查看n100-server服务相关状态，命令如下：
- `systemctl start n100-server.service`：启动服务
- `systemctl stop n100-server.service`：停止服务
- `systemctl restart n100-server.service`：重启服务
- `systemctl status n100-server.service`：服务状态