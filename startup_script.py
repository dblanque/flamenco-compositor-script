# ############################################################################ #
# Author: Dylan Blanque
# Reviewer: Sybren Stüvel
# Created: 2023-03-24
# SPDX-License-Identifier: GPL-3.0-or-later
# Blender Script for Flamenco Network Rendering with Compositor Support and
# Multi-platform compatibility
# ############################################################################ #

import bpy
from os import path as os_path
import sys
from bpy.app.handlers import persistent
import argparse

arg_parser = argparse.ArgumentParser(
	description="Add custom script hook before rendering a job in Flamenco",
)
arg_parser.add_argument("--device-type")
arg_parser.add_argument("--disable-compositing", action="store_true")
arg_parser.add_argument("--disable-persistent-data", action="store_true")
arg_parser.add_argument("--render-output")
arg_parser.add_argument("--render-frames")

argv, unknown = arg_parser.parse_known_args(sys.argv[1:])

@persistent
def main(self):
	# !! Do not move this into the arg parser or the script ceases to work !! #
	if "--custom-script" not in sys.argv: return

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

	try:
		enable_persistent_data()
	except Exception as e:
		print("Unhandled Exception: Could not enable Persistent Data Mode.")
		print(f"Exception Message: {e}")
		raise

def enable_persistent_data():
	# Enabled Persistent Texture/Image usage between renders in job chunks with
	# more than 1 frame.
	blender_scene = bpy.context.scene

	if (
		blender_scene.render.engine != "CYCLES" # Only works with Cycles.
		or ".." not in argv.render_frames # If render frames aren't a range
		or argv.disable_persistent_data  # If this option is explicitly disabled
	): return

	frames_in_job = argv.render_frames.split("..")
	frames_in_job = int(frames_in_job[1]) - int(frames_in_job[0])

	if frames_in_job > 1:
		blender_scene.render.use_persistent_data = True

def enable_gpus():
	blender_scene = bpy.context.scene
	blender_preferences = bpy.context.preferences

	if (
		blender_scene.render.engine != "CYCLES" 
     	or argv.device_type == "CPU"
	): return

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
	print("Detected Devices:")
	for device in device_list:
		print(f"\t{device.name} ({device.type})")
		if device.type != "CPU" and not first_detected_type:
			first_detected_type = device.type

	# Set the device_type
	selected_device_type = argv.device_type
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
			device["use"] = 1 # Enable all devices, include GPU and CPU
			print(f"Device {device.name} will be used ({device.use} - {device.type}).")

	print("Enabled GPUs for Cycles where possible.")

def fix_compositing_paths():
	blender_scene = bpy.context.scene

	if argv.disable_compositing: return

	# Render Output Path Cleanup
	render_output_path = argv.render_output
	render_output_path = render_output_path.replace('\\','/')
	render_output_path = os_path.split(render_output_path)[0]

	if not render_output_path.endswith('/'):
		render_output_path += "/"

	print("Executing compositor startup fixes.")
	print(f"Output path: {render_output_path}")

	# Enable Post Processing and Use Nodes
	blender_scene.render.use_compositing = True
	blender_scene.use_nodes = True

	# Get the File Output Nodes by type and put into a Generator
	fo_nodes = (
		c_node for c_node in blender_scene.node_tree.nodes
		if c_node.bl_rna.identifier == "CompositorNodeOutputFile"
	)

	for node in fo_nodes:
		try:
			node.base_path = render_output_path
			print(f"Using path {node.base_path} for Compositor Node {node.name}")
		except Exception as e:
			print(f"Could not set File Output Nodes (Compositor) - Exception traceback: {e}")

bpy.app.handlers.load_post.append(main)
