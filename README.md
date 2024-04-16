# Flamenco Compositor Script and Job
Scriptset to enable compositing in the Blender Flamenco Network Renderer

Author: Dylan Blanqué

Contributors:
* Sybren Stüvel

### Tested with Blender >= 4.0

If you need to use Blender's **Compositor** Nodes with *Flamenco*,
a Python Script and a Flamenco Job have been contributed to the community.

You'll need to do the following changes to support this workflow:

(It's recommended to use a symbolic link to the git repo files)

1. Clone the [Flamenco Compositor Script repository][compositorrepo]
(you'll need to install **git** to clone it) or [download the files manually](https://github.com/dblanque/flamenco-compositor-script/archive/refs/heads/main.zip) to a directory
in your Flamenco Manager/Server.
```bash
git clone https://github.com/dblanque/flamenco-compositor-script.git
```
2. Copy or make a symbolic link of the **startup_script.py** file
to the root path of your configured *Network Attached Storage*.
3. Copy or make a symbolic link of the multipass javascript job to the *scripts*
folder in your Flamenco Manager Installation (Create it if it doesn't exist).
4. Add and configure the required variables from the *example Manager YAML*
*Config* to your Flamenco Manager YAML.
    * **clientStoragePath**   - Your NAS path, multi-platform variable.
    * **jobSubPath**    - Where the jobs are stored inside storagePath. (Default: jobs)
    * **renderSubpath** - Where the Render Output is stored inside storagePath. (Default: render)
    * **deviceType**    - Compute Device Type to force (*do not set the variable if*
     *you wish to use whatever is available*)
5. Submit your job from a Blender Client with the corresponding Multi-Pass Job,
it should use and render whatever compositor nodes you have set and automatically correct
the paths where necessary.

[compositorrepo]: https://github.com/dblanque/flamenco-compositor-script.git

**This has only been tested in an environment with Flamenco Manager and**
**Shaman enabled, but it should work without Shaman as well.**

# Example Configuration Flamenco Manager YAML

```yaml
# Configuration file for Flamenco.
#
# For an explanation of the fields, 
# refer to the original flamenco-manager-example.yaml
_meta:
  version: 3
manager_name: Flamenco Manager
database: flamenco-manager.sqlite
listen: :8080
autodiscoverable: true
local_manager_storage_path: ./flamenco-manager-storage
shared_storage_path: /mnt/data/flamenco
shaman:
  enabled: true
task_timeout: 10m0s
worker_timeout: 1m0s
blocklist_threshold: 3
task_fail_after_softfail_count: 3
variables:
  blender:
    values:
      - platform: linux
        value: blender
      - platform: windows
        value: "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe"
      - platform: darwin
        value: blender
  blenderArgs:
    values:
      - platform: all
        value: -b -y
  clientStoragePath:
    values:
      - platform: linux
        value: /mnt/storage
      - platform: windows
        value: "Z:\\"
  jobSubPath:
    values:
      - platform: all
        value: jobs
  renderSubPath:
    values:
      - platform: all
        value: render
  deviceType:
    values:
      - platform: all
        value: "CUDA"
    # Set the device type to FIRST or remove the variable definition
    # to use whatever device type is detected first.
    # Valid Choices: 
    # * CPU
    # * CUDA
    # * OPTIX
    # * HIP
    # * ONEAPI
    # * FIRST
```
Select the corresponding job in Blender when submitting it to Flamenco and voilá.

*Multi-pass!*
