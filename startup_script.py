# ############################################################################ #
# Author: Dylan Blanque
# Reviewer: Sybren Stüvel
# Updated: 2023-03-24
# SPDX-License-Identifier: GPL-3.0-or-later
# Blender Script for Flamenco Network Rendering with Compositor Support and
# Multi-platform compatibility
# ############################################################################ #

import bpy
from os import path as os_path
import sys
from bpy.app.handlers import persistent
argv = sys.argv

@persistent
def main(self):
	if "--custom-script" not in argv: return

	try:
		enable_gpus()
	except Exception as e:
		print("Unhandled Exception: Unable to change Compute Device Settings.")
		print(f"Exception Message: {e}")
		raise

	try:
		fix_compositing_paths()
	except Exception as e:
		print("Unhandled Exception: Could not enable Compositing Nodes.")
		print(f"Exception Message: {e}")
		raise

def enable_gpus():
	blender_scene = bpy.context.scene
	blender_preferences = bpy.context.preferences

	if blender_scene.render.engine != "CYCLES": return

	# Detect Devices
	cycles_preferences = blender_preferences.addons["cycles"].preferences
	cycles_preferences.get_devices()
	device_list = cycles_preferences.devices

	compute_types = [ "CPU" ]
	nvidia_types = [ "CUDA", "OPTIX" ]
	amd_types = [ "HIP" ]
	intel_types = [ "ONEAPI" ]

	compute_types.extend(nvidia_types)
	compute_types.extend(amd_types)
	compute_types.extend(intel_types)

	# Source: https://blender.stackexchange.com/questions/217912/get-access-to-the-device-type-gpu-and-cpu-activation
	# Show detected devices and get priority compute type
	first_detected_type = None
	print("Devices:")
	for device in device_list:
		print(f"\t{device.name} ({device.type})")
		if device.type != "CPU" and not first_detected_type:
			first_detected_type = device.type

	# Set the device_type
	selected_device_type = argv[argv.index("--device-type") + 1]
	if selected_device_type == "FIRST" or selected_device_type not in compute_types:
		print(f"Cycles Render will use the first non-CPU compute device type detected")
		cycles_preferences.compute_device_type = first_detected_type
	else:
		cycles_preferences.compute_device_type = selected_device_type

	# Set the device and feature set
	blender_scene.cycles.device = "GPU"
	compute_device_type = cycles_preferences.compute_device_type

	print(f"Cycles Render Compute mode set to prefer {selected_device_type}")

	for device in device_list:
		if device.type == "CPU" or device.type == compute_device_type:
			device["use"] = 1 # Using all devices, include GPU and CPU
			print(f"Device {device.name} will be used ({device.use} - {device.type}).")

	print("Enabled GPUs for Cycles where possible.")

def fix_compositing_paths():
	blender_scene = bpy.context.scene

	# Render Output Path Cleanup
	render_output_path = argv[argv.index("--render-output") + 1]
	render_output_path = render_output_path.replace('\\','/')
	render_output_path = os_path.split(render_output_path)[0]

	print("Executing compositor startup fixes.")
	print(f"Output path: {render_output_path}")

	# Enable Post Processing and Use Nodes
	blender_scene.render.use_compositing = True
	blender_scene.use_nodes = True

	# Get the File Output Nodes by type and put into a Generator
	fo_nodes = (c_node for c_node in blender_scene.node_tree.nodes if c_node.bl_rna.identifier == "CompositorNodeOutputFile")

	for node in fo_nodes:
		try:
			node.base_path = render_output_path
			print(f"Using path {node.base_path} for Compositor Node {node.name}")
		except Exception as e:
			print(f"Could not set File Output Nodes (Compositor) - Exception traceback: {e}")

bpy.app.handlers.load_post.append(main)
