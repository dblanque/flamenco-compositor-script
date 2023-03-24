# Flamenco Compositor Script and Job
Scriptset to enable compositing in the Blender Flamenco Network Renderer

Author: Dylan Blanqué

Contributors:
* Sybren Stüvel

# Usage
For the moment this script has only been tested with Flamenco and Shaman enabled,
albeit it *should* be functional without Shaman, as the job paths and render output
paths do not get modified.

To use it you need to add the following variables to your Manager YAML config:
* storagePath
* jobSubPath
* renderSubPath
* deviceType

An example configuration file is included.

After that copy the multi_pass_render.js job to your Flamenco Manager Scripts
folder (if you don't have it, create a **scripts** folder and copy it there).

Then copy the startup_script python *script* to your NAS storage or wherever your
Flamenco Manager is keeping your files.

Select the corresponding job in Blender when submitting it to Flamenco and voilá.

*Multi-pass!*
