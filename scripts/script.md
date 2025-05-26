

常用的一些脚本收集：
- gradle目录：gradle依赖拉取提速
- aliyunDDNS：阿里云DNS信息解析、更新、新增、删除等，简易的DDNS实现


### aliyunDDNS

脚本文件基于Python3环境。

#### 1. 阿里云相关SDK下载：
```bash
pip install aliyun-python-sdk-core
pip install aliyun-python-sdk-domain
pip install aliyun-python-sdk-alidns
```

#### 2. 对`ddns_config.json`进行初始化配置

填写在阿里云平台上的access_key_id、access_key_secret、domain_name、region_id信息

#### 3. 完全授予权限

chmod -R 777 aliyunDDNS

#### 4. 记录最近一次执行操作日志

会在同一目录下生成`operation_ddns.log`，打印内容样例如下：
```
DomainName=lsfun.cn
 subdomain=www
操作时间：Sat Jun 15 22:47:57 2024
操作结果：准备更新已有记录 -> 新ip与原ip相同，无法更新！
 subdomain=@
操作时间：Sat Jun 15 22:47:58 2024
操作结果：准备更新已有记录 -> 新ip与原ip相同，无法更新！
```

注意：如果是要定时执行脚本，生成日志要用绝对路径！！！


#### 5. 定时执行脚本

通过 `crontab ` 周期性执行python脚本。

- crontab 格式
```
m h  dom mon dow   command
```

- 执行`crontab -e` 命令添加以下定时任务内容
```bash
# 每十分钟执行一次任务
*/10 * * * * python3 /home/user/data/script/aliyunDDNS/aliyun_ddns.py
```

- 执行`crontab -l`查看当前用户下的周期任务表，确认是否写入成功

#### 6. 路由回流临时处理

已知Windows客户端与服务器处于同一个局域网，此时客户端直接使用域名访问资源会因为路由回流引起失败（电信光猫！）。

解决办法：
- 搭建本地的DNS服务，进行DNS劫持处理
- Windows设置本地DNS域名

这里仅针对该台Windows客户端临时解决路由回流，步骤如下：
1. 进入`C:\Windows\System32\drivers\etc`目录，打开`hosts`文件
2. 在文本末尾增加域名与ip的映射关系。示例：`192.168.1.1   example.com`


### hugo定时更新与部署

脚本名称：**hugo_deploy_changes.py**

工作流程：
- 周期性获取hugo-site仓库下最近一次提交的hash值，与脚本所在目录保存的hash值进行比对，若一致则中断流程
- 触发hugo-site的仓库 git pull 操作来更新内容
- 开始清理已有的 public 目录，同时进行 hugo 部署
- hugo 部署成功以后，触发 nginx reload 操作

执行 nginx 需要 sudo 权限，可以针对 nginx reload 操作进行权限豁免，操作如下：
- 使用visudo编辑文件：`sudo visudo -f /etc/sudoers.d/hugo_deploy_changes`
- 在 hugo_deploy_changes 添加内容：`user ALL=(root) NOPASSWD: /usr/sbin/nginx -s reload`
- 添加完内容以后，按 "Ctrl+O" 触发保存，再按 "Enter" 完成保存，接着 "Ctrl+X" 退出编辑


定时任务示例：
```bash
# 编辑定时任务
crontab -e

# 每小时触发 hugo deploy changes 任务
*/60 * * * * python3 /home/user/data/script/hugo/hugo_deploy_changes.py /home/user/library/hugo-site
```