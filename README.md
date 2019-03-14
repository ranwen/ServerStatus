# ServerStatus 部分重构版

- Server部分采用python重构
- 一键部署

## Server部署

- 需要python3

  ```bash
  git clone https://github.com/ranwen/ServerStatus
  cd ServerStatus/server
  ```

  修改config.json下的token 之后执行

  ```bash
  python3 server.py
  ```

  访问IP:7122即可查看

## Client部署

- 需要python2/3

```bash
wget -O - http://IP:7122/add?token=TOKEN&name=NAME | bash
```

其中

IP 为服务端IP

TOKEN 为服务端token

NAME 为节点名

会自动添加任务到 /etc/rc.local

## 感谢

[https://github.com/BotoX/ServerStatus](https://github.com/BotoX/ServerStatus)

[https://github.com/cppla/ServerStatus](https://github.com/cppla/ServerStatus)