# ICT Auth

在没有图形化界面的情况下（比如 Ubuntu Server），进行中科院计算所上网认证。

## 前提

- Python>=3.8（例如 Ubuntu 20.04 或更高版本）
- 可以获得 ipv6 地址，用来正常访问 apt 源（计算所在不登陆的情况下可以正常获得 ipv6 地址并具有互联网访问）

## 安装

1. 获取安装包，目前有两种方法：

   - **（推荐）** 从[发布](https://github.com/jklincn/ict_auth/releases)下载预打包的。

   - 在其他联网的机器中自行制作：

     ```
     git clone https://github.com/jklincn/ict_auth.git
     cd ict_auth
     ./package.sh
     ```

2. 将安装包拷贝到目标机器，可以使用 scp 或者 U 盘等方法。

3. 在目标机器上安装，这会安装所需的 apt（通过网络） 和 pip（通过本地文件） 软件包。

   ```
   chmod +x ict_auth.run
   ./ict_auth.run
   ```

   默认安装路径为 `~/.local/ict_auth`，暂不支持更改。

   - 如果 `~/.local/bin` 不在 `PATH` 中，可以重新登陆使其自动添加或者手动修改 PATH 。
   - 或直接使用 `~/.local/bin/ict_auth` 来运行。

## 使用

### 登陆

运行 ict_auth 直接进行上网认证登陆，输入自己的账号密码回车即可。

```
$ ict_auth
Checking dependencies...
Checking if logged in...
Starting login...
=============================
ict_username: xxxx
ict_password:
=============================
Login succeeded
Username: xxxx
Used flow: 1.28 GB
Used time: 12小时33分12秒
IP address: 10.156.xxx.xxx
```

### 退出

在已登录的情况下，再次运行 ict_auth 会提示是否要退出，输入 y 进行退出。

```
$ ict_auth
Checking dependencies...
Checking if logged in...
You are already logged in. Do you want to logout? [y/N] y
Logout succeeded
```

### 卸载

这会删除 `~/.local/ict_auth` 文件夹以及 `~/.local/bin/ict_auth` 可执行文件，**但不会删除已经安装的 apt 包和 pip 包**

```
$ ict_auth --uninstall
ict_auth uninstalled successfully
```

### 帮助

更多命令可以使用 help 查看

```
$ ict_auth --help
Usage:
  ict_auth              Start Internet authentication
  ict_auth --help       Show help message
  ict_auth --uninstall  Uninstall ict_auth from the system
  ict_auth --version    Print version information
```