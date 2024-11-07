# ICT Auth

使用命令行界面进行中科院计算所上网认证登陆。

## 前提

- 系统自带的 Python 版本 >= 3.8（例如 Ubuntu 20.04 或更高版本）
- 可以通过网线获得正常的内网 ipv4 地址以及 ipv6 地址

暂时仅支持 Ubuntu 发行版（仅在 Ubuntu 20.04/22.04 LTS 上测试过）

## 安装

1. 获取安装包，目前有两种方法：

   - **（推荐）** 从[发布](https://github.com/jklincn/ict_auth/releases)下载预制作的安装包（ict_auth.run）

   - 在其他联网的机器中自行制作：

     ```
     git clone https://github.com/jklincn/ict_auth.git
     cd ict_auth
     ./package.sh
     ```

2. 将安装包拷贝到目标机器，可以使用 scp 或者 U 盘等方法。

3. 在目标机器上安装，这会安装所需的 deb 包（通过网络），然后使用 venv 创建虚拟环境，在虚拟环境中安装所需的 whl 包（通过本地文件）。

   ```
   chmod +x ict_auth.run
   ./ict_auth.run
   ```


## 使用

### 登陆

运行 ict_auth 直接进行上网认证登陆，输入自己的账号密码回车即可。

```
$ ict_auth
[INFO] Checking if logged in...
[INFO] Starting login process...
=============================
ICT Username: aaabbbccc
ICT Password: 
=============================
[INFO] Login succeeded
[INFO] Username: aaabbbccc
[INFO] Used flow: 33.42 GB
[INFO] Used time: 13小时8分11秒
[INFO] IP address: 10.xxx.xxx.xxx
```

### 退出

在已登录的情况下，再次运行 ict_auth 会提示是否要退出，输入 y 进行退出。

```
$ ict_auth
[INFO] Checking if logged in...
[INFO] You are already logged in. Do you want to logout? [y/N] y
[INFO] Logout succeeded
```

### 持久连接

据观察，所里的网络时常自动断开，可以使用 `--enable` 将 ict_auth 注册为系统后台服务，持续检测上网认证状态。如果发现网络断开，则自动进行登陆。默认检测频率是每分钟一次。

**注意：这会在本地明文保存账号与密码，存在账号安全隐患（待优化）**

```
$ ict_auth --enable
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

取消持久连接（这会卸载系统服务并清空账号信息）

```
$ ict_auth --disable
[INFO] Stopping persistent connection service...
Removed /etc/systemd/system/timers.target.wants/ict_auth.timer.
[INFO] Persistent connection service stopped successfully.
```

查看持久连接日志

```
$ ict_auth --log
Nov 07 08:02:21 603-1 bash[546277]: [INFO] Connection interruption detected. Logging in automatically.
Nov 07 08:02:21 603-1 bash[546277]: [INFO] Username: aaabbbccc
Nov 07 08:02:21 603-1 bash[546277]: [INFO] Used flow: 3.42 GB
Nov 07 08:02:21 603-1 bash[546277]: [INFO] Used time: 24小时16分42秒
Nov 07 08:02:21 603-1 bash[546277]: [INFO] IP address: 10.xxx.xxx.xxx
Nov 07 08:21:23 603-1 bash[552090]: [INFO] Connection interruption detected. Logging in automatically.
Nov 07 08:21:23 603-1 bash[552090]: [INFO] Username: aaabbbccc
Nov 07 08:21:23 603-1 bash[552090]: [INFO] Used flow: 3.55 GB
Nov 07 08:21:23 603-1 bash[552090]: [INFO] Used time: 24小时35分29秒
Nov 07 08:21:23 603-1 bash[552090]: [INFO] IP address: 10.xxx.xxx.xxx
```

### 卸载

这会删除 ict_auth 相关的所有文件，包括持久连接服务和使用 venv 创建的虚拟环境。

```
$ ict_auth --uninstall
[INFO] ict_auth uninstalled successfully
```

### 帮助

更多命令可以使用 help 查看

```
$ ict_auth --help
Usage:
  ict_auth              Start Internet authentication
  ict_auth --help       Show help message
  ict_auth --enable     Enable and start the persistent connection service
  ict_auth --disable    Disable the persistent connection service.
  ict_auth --log        View the logs for the persistent connection service.
  ict_auth --uninstall  Uninstall ict_auth from the system
  ict_auth --version    Print version information
```

## 权限说明

setup.sh 脚本中的 sudo 权限用于：

- 程序安装过程中进行 deb 包的安装（apt-get 命令）
- 开启持久连接时写入 /etc/systemd 文件夹（包括 systemctl 命令）
- 取消持久连接时写入 /etc/systemd 文件夹（包括 systemctl 命令）