# ICT Auth

使用 CLI 进行中科院计算所上网认证登陆。

核心想法是使用浏览器的无头模式搭配自动化工具来模拟用户打开认证网页，输入账号密码登陆的操作。

## 前提

- 系统自带的 Python 版本 >= 3.8（例如 Ubuntu 20.04 或更高版本）
- 可以通过网线获得正常的内网 ipv4 地址以及公网 ipv6 地址

暂时仅支持 Ubuntu 发行版（仅在 Ubuntu 20.04/22.04 LTS 上测试过）

## 安装

```
curl -sSf -6 https://oss.jklincn.com/ict_auth.sh | sh
```

这会通过 ipv6 网络下载安装包并进行安装。

## 使用

### 登陆

使用 `login` 命令进行上网认证登陆，需要输入自己的账号密码。

```
$ ict_auth login
[INFO] Preparing the runtime...
[INFO] Starting login process...
=============================
ICT Username: aaabbbccc
ICT Password: 
=============================
[INFO] Login succeeded.
[INFO] Username: aaabbbccc
[INFO] Used flow: 33.42 GB
[INFO] Used time: 13小时8分11秒
[INFO] IP address: 10.xxx.xxx.xxx
```

### 退出

使用 `logout` 命令进行退出。

```
$ ict_auth logout
[INFO] Preparing the runtime...
[INFO] Logout succeeded.
```

### 当前状态

使用 `status` 命令查看当前状态。

```
# 已登陆状态
$ ict_auth status
[INFO] Preparing the runtime...
[INFO] Status: Online
[INFO] Username: aaabbbccc
[INFO] Used flow: 33.42 GB
[INFO] Used time: 13小时8分11秒
[INFO] IP address: 10.xxx.xxx.xxx

# 未登录状态
$ ict_auth status
[INFO] Preparing the runtime...
[INFO] Status: Offline
```

### 持久连接 (Beta)

据观察，所里的网络时常自动断开，可以使用 `enable` 将 ict_auth 注册为系统后台服务，持续检测上网认证状态。如果发现网络断开，则自动进行登陆。默认检测频率是每分钟一次，如果出错则十分钟后进行重试。

> **2024-12-23 更新：感觉网络逐渐稳定，登陆一次后很少会断开。**

**注意：这会在本地明文保存账号与密码，存在账号安全隐患（即便文件权限已设置成 600）（待优化）**

```
$ ict_auth enable
[INFO] Starting persistent connection service...
=============================
ICT Username: aaabbbccc
ICT Password: 
=============================
[INFO] Verifying account...
[INFO] Account verification successful.
Created symlink /etc/systemd/system/timers.target.wants/ict_auth.timer → /etc/systemd/system/ict_auth.timer.
[INFO] Persistent connection service started successfully.
```

使用 `disable` 取消持久连接（这会卸载系统服务并清空账号信息）

```
$ ict_auth disable
[INFO] Stopping persistent connection service...
Removed /etc/systemd/system/timers.target.wants/ict_auth.timer.
[INFO] Persistent connection service stopped successfully.
```

使用 `logs` 查看持久连接日志

```
$ ict_auth logs
2024-12-19 05:51:24 [INFO] Service Start.
2024-12-19 07:37:35 [INFO] Connection interruption detected. Logging in automatically.
2024-12-19 07:37:35 [INFO] Connection interruption detected. Logging in automatically.
2024-12-19 07:37:35 [INFO] Username: aaabbbccc
2024-12-19 07:37:35 [INFO] Used flow: 3.55 GB
2024-12-19 07:37:35 [INFO] Used time: 24小时35分29秒
2024-12-19 07:37:35 [INFO] IP address: 10.xxx.xxx.xxx
```

### 更新

使用 `upgrade` 命令进行更新

```
$ ict_auth upgrade
[INFO] Upgrading from 2024-12-07 to 2024-12-17...
[INFO] Downloading installer...
######################################################### 100.0%
Verifying archive integrity...  100%   MD5 checksums are OK. All good.
Uncompressing ICT Auth - 2024-12-17  100%
[INFO] ict_auth successfully installed in /home/lin/.local/ict_auth
[INFO] Upgrade completed successfully.
```

### 卸载

使用 `uninstall` 可以删除 ict_auth 相关的所有文件，包括持久连接服务和使用 venv 创建的虚拟环境。

```
$ ict_auth uninstall
[INFO] ict_auth uninstalled successfully.
```

### 帮助

更多命令可以使用 `-h` 或 `--help` 查看

```
$ ict_auth --help
Usage: ict_auth [OPTIONS] COMMAND

A command-line tool for ICT network authentication.

Options:
  -h, --help          Show this help message and exit
  -V, --version       Show version information and exit

Commands:
  login               Log in to the ICT network
  logout              Log out and terminate the session
  status              Show the current login status
  enable              Enable and start the persistent connection service
  disable             Disable the persistent connection service
  logs                Show logs for the persistent connection service
  upgrade             Check for updates and install the latest version
  uninstall           Uninstall ict_auth from the system
```

## 管理员权限说明

install.sh 脚本中的 sudo 权限用于：

- 程序安装过程中进行 deb 包的安装（apt-get 命令）

entry.sh 脚本中的 sudo 权限用于：

- 开启持久连接时写入 /etc/systemd 文件夹（包括 systemctl 命令）
- 取消持久连接时写入 /etc/systemd 文件夹（包括 systemctl 命令）
