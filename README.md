# ICT Auth

ICT Internet Authentication without GUI.

## Target machine requirements

- Python>=3.8 (e.g. Ubuntu 20.04 or above)
- Connect to APT source (By default in ICT network)

## Get started

1. Get the runfile. There are two ways to get ICT Auth runfile. 

   - (Recommended) Download the pre-packaged runfile from the [release](https://github.com/jklincn/ict_auth/releases) page.

   - Package it yourself.

     ```
     git clone https://github.com/jklincn/ict_auth.git
     cd ict_auth
     ./package.sh
     ```

2. Transfer runfile to the target machine. You can use SCP or a USB drive.

3. Execute runfile on target machine.

   ```
   ./ict_auth.run
   ```

