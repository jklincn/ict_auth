# ICT Auth

ICT Internet Authentication without GUI.

## Target machine requirements

- Python>=3.8 (e.g. Ubuntu 20.04 or above)
- Connect to APT source (By default in ICT network)

## Get started

There are two ways to obtain ICT Auth. 

1. Download the pre-packaged run file from the [release](https://github.com/jklincn/ict_auth/releases) page.

2. Package it yourself on a machine with network access.

   ```
   git clone https://github.com/jklincn/ict_auth.git
   cd ict_auth
   ./package.sh
   ```

Once you have the run file, you can use SCP or a USB drive to transfer it to the target machine and then execute it.

```
./ict_auth.run
```