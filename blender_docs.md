---
title: Compositor Nodes and Multi-Platform Storage Paths
weight: 11
---

If you need to use Blender's **Compositor** Nodes with *Flamenco*,
a Python Script and a Flamenco Job have been contributed to the community.

You'll need to do the following changes to support this workflow:

(It's recommended to use a symbolic link to the git repo files)

1. Clone the [Flamenco Compositor Script repository][compositorrepo]
(you'll need to install **git**) or download the files manually to a directory
in your Flamenco Manager/Server.
```bash
git clone https://github.com/dblanque/flamenco-compositor-script.git
```
2. Copy or make a symbolic link of the **startup_script.py** file.
to the configured Blender File Folder in your *Network Attached Storage*.
3. Copy or make a symbolic link of the multipass javascript job to the *scripts*
folder in your Flamenco Manager Installation (Create it if it doesn't exist).
4. Add and configure the required variables from the *example Manager YAML*
*Config* to your Flamenco Manager YAML.
    * **storagePath**   - Your NAS path, multi-platform variable.
    * **jobSubPath**    - Where the jobs are stored inside storagePath.
    * **renderSubpath** - Where the Render Output is stored inside storagePath.
    * **deviceType**    - Compute Device Type to force *do not set the variable if*
     *you wish to use whatever is available*
5. Submit your job from a Blender Client with the corresponding Multi-Pass Job,
it should whatever compositor nodes you have set and correct the paths where
necessary.

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
shared_storage_path: /mnt/storage/project_files
shaman:
  enabled: true
  garbageCollect:
    period: 24h0m0s
    maxAge: 744h0m0s
    extraCheckoutPaths: []
task_timeout: 10m0s
worker_timeout: 1m0s
blocklist_threshold: 3
task_fail_after_softfail_count: 3
variables:
  blender:
    values:
    - platform: all
      value: blender
    - platform: linux
      value: /usr/local/blender/blender
    - platform: windows
        value: C:/Program Files/Blender Foundation/Blender 3.4/blender.exe
    - platform: darwin
        value: /usr/bin/blender
  blenderArgs:
    values:
    - platform: all
      value: -b -y
  storagePath:
    values:
    - platform: linux
      value: /mnt/storage
    - platform: windows
      value: "Z:\\"
  jobSubPath:
    values:
    - platform: all
      value: project_files
  renderSubPath:
    values:
    - platform: all
      value: project_render
  deviceType:
    values:
    - platform: all
      value: "CUDA"
    # Set the device type to FIRST or remove the variable definition
    # to use whatever device type is detected first.
```