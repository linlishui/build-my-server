

### 反向代理n100-server

在`/etc/nginx/conf.d`目录里新建`n100-server.conf`文件，内容如下：
```
upstream server_upstream{
  server 127.0.0.1:8090   max_fails=3 fail_timeout=3s weight=10;
}

# 【websocket】如果没有Upgrade头，则$connection_upgrade为close，否则为upgrade
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
  listen 9090;
  server_name  127.0.0.1;

  location /n100-wss {
    proxy_pass http://server_upstream;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
  }

  location /api {
    proxy_pass http://server_upstream;
    proxy_set_header Host $host:$server_port;
    proxy_set_header X-Forwarded-Host $server_name;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```