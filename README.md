# ICT Auth

ICT Internet Authentication without GUI.

## Target machine requirements

- Python>=3.8 (e.g. Ubuntu 20.04 or above)
- Connect to APT source (By default in ICT network)

## Usage

### Pre-Built

1. Download the run file from the [release](https://github.com/jklincn/ict_auth/releases) page.

2. Send the run file to the target machine. You can use SCP or USB flash disk.

3. Run the run file on the target machine.

   ```
   ./ict_auth.run
   ```

### Build

1. Clone the repository.

   ```
   git clone https://github.com/jklincn/ict_auth.git
   ```

2. Run the pack script to generate run file.

   ```
   cd ict_auth
   ./pack.sh
   ```

3. Follow the Pre-Built Step 2-3