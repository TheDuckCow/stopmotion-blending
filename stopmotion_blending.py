# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import re


# -----------------------------------------------------------------------------
# This addon is meant to assist with creating stopmotion animations in blender
# through a variety of importing and image capture tools.
# -----------------------------------------------------------------------------


bl_info = {
	"name": "Stopmotion Blending",
	"author": "Patrick W. Crawford",
	"version": (0, 3, 0),
	"blender": (2, 79, 0),
	"location": "Sequence Editor",
	"description": "Help create stopmotion animations leveraging blender",
	"warning": "In development",
	"wiki_url": "https://github.com/TheDuckCow/stopmotion-blending",
	"tracker_url": "https://github.com/TheDuckCow/stopmotion-blending/issues",
	"category": "Sequencer"
}

# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------


VERBOSE = True
def printlog(*args):
	"""Custom print function which takes in verbose to account."""
	if VERBOSE:
		prt_str = " ".join(str(i) for i in args)
		print("{}".format(prt_str))


# -----------------------------------------------------------------------------
# Utility functions and classes for propertyies, including update functions
# -----------------------------------------------------------------------------


def resequence_folder_default(context, path, order=None, delete_unused=False):
	"""Given path and order of image names (or just path), rename to order.

	Args
		order: list, e.g. ["frame_001.png", "frame_003.png"]
		delete_unused: not yet implemented, if true will delete frames not in
		order (if order is not empty) (not yet implemented)
	Returns
		first_frame_basename
	"""
	if not path:
		seq_active = context.scene.sequence_editor.active_strip
		if seq_active.type != "IMAGE":
			return {"ERROR","Select an image sequence"}
		npath = bpy.path.abspath(seq_active.directory)
		if os.path.isdir(npath):
			path = npath
		else:
			return {"ERROR","Invalid directory detected on sequence"}

	onlyfiles = [f for f in os.listdir(path)
				if os.path.isfile(os.path.join(path, f))]
	printlog(onlyfiles)

	# convert to make use of self.extension_filter
	pngs = sum([1 for a in onlyfiles if "png" in a.lower()])
	jpgs = sum([1 for a in onlyfiles if "jpg" in a.lower()])
	jpegs = sum([1 for a in onlyfiles if "jpeg" in a.lower()])

	ext = None
	if pngs>jpegs:
		printlog("doing png re-ordering")
		ext = "png"
	elif jpgs>0:
		printlog("doing jpeg re-ordering")
		ext = "jpg"
	elif jpegs>0:
		printlog("doing jpeg re-ordering")
		ext = "jpeg"
	else:
		return {"ERROR","Valid image extention not found"}

	# get just the sequence of files we need
	# adjust later in case of no extensions or 4 letter extentions
	sequence = [f for f in onlyfiles if f[-3:].lower()==ext]
	sequence.sort()
	printlog(sequence)

	# get the common prefix and remove trailing digits
	# this also does not account for there being multiple
	# sequences in the same folder
	prefix = os.path.commonprefix(sequence).rstrip("1234567890")
	printlog("Prefix is:", prefix)

	first_frame = None
	for i,frame in enumerate(sequence):
		orig_name = os.path.join(path,frame)
		new_name = os.path.join(path,prefix+str(i).zfill(4)+frame[-4:])
		os.rename(orig_name, new_name) # to keep orignal format of extention caps etc
		printlog(os.path.basename(orig_name), os.path.basename(new_name))
		if not first_frame:
			first_frame = new_name

	printlog("Finish resequencing")
	return first_frame


# -----------------------------------------------------------------------------
# Blender Operators
# -----------------------------------------------------------------------------


class SMB_resequence_folder(bpy.types.Operator):
	bl_idname = "stopmotion.resequence_folder"
	bl_label = "Resequence"
	bl_description = "Rename the images of a folder to be sequential without gaps"
	# bl_options = {"REGISTER", "UNDO"}

	folder = bpy.props.StringProperty(
		name = "Folder",
		description = "Folder containing images to resequence",
		subtype = "DIR_PATH",
		default = ""
		)

	def execute(self, context):

		path = self.folder
		order = []
		res = resequence_folder_default(context, path, order)
		if "ERROR" in res:
			self.report({"ERROR"}, res["ERROR"])
			printlog(res["ERROR"])
			return {"CANCELLED"}

		printlog(res)

		# now reload the sequence
		# get starting frame:
		# active_strip.frame_start
		# or can we just change the directory to update?

		return {"FINISHED"}


class SMB_refresh_sequence(bpy.types.Operator):
	bl_idname = "stopmotion.refresh_sequence"
	bl_label = "Refresh sequence"
	bl_description = "Looks for more images found in directory of active sequence and appends to end any found"

	def execute(self, context):
		"""Operator called when refreshing scene based on frame change."""

		active = context.scene.sequence_editor.active_strip
		if not active:
			return {"CANCELLED"}
		elif active.type != "IMAGE":
			return {"CANCELLED"}
		frames = [elem.filename for elem in active.elements]
		if not frames:
			return {"CANCELLED"}

		path = bpy.path.abspath(active.directory)
		# prefix = os.path.commonprefix(frames) #.rstrip("1234567890")

		# Take first image in set, strip out last number chunk but keep rest
		prefix_reg = r"[0-9]+(?!.*[0-9])"
		prefix = active.elements[0].filename
		prefix = re.sub(prefix_reg, "", prefix)
		# format of: IMG_001.jpg -> IMG_.jpg
		printlog("Found prefix:", prefix)
		new_frames = [f for f in os.listdir(path)
					if os.path.isfile(os.path.join(path, f))
					and prefix==re.sub(prefix_reg, "", f)]
		new_frames.sort()
		printlog("Sorted frames:", new_frames)
		printlog("Old frames:", frames)

		if not new_frames:
			printlog("No matching subframes found, skipping")
			self.report({"ERROR"}, "Could not find matching image files")
			return {"CANCELLED"}
		elif frames == new_frames:
			printlog("All frames match, not updating")
			return {"CANCELLED"}

		# clear elements all excepet first (can"t remove all elements)
		for _ in range(len(active.elements)-1):
			active.elements.pop(-1)
		if active.elements[0].filename not in new_frames:
			# base file was removed, so replace it with first from new_frames
			active.elements.append(new_frames[0])
			active.elements.pop(0)

		# now append all the new (ordered) frames
		ind = new_frames.index(active.elements[0].filename) + 1
		if ind == len(new_frames):
			printlog("Not adding more frames after the base one")
			return {"FINISHED"}
		for frame in new_frames[ind:]:
			active.elements.append(frame)

		# be sure to refresh any caches
		bpy.ops.sequencer.refresh_all()

		return {"FINISHED"}


# -----------------------------------------------------------------------------
# Frame update handler
# -----------------------------------------------------------------------------


def frame_change_handler(scene):
	"""Handler which runs every frame to update active sequence."""
	printlog("Frame change handler")
	if not scene:
		return
	elif not scene.stopmotion_auto_refresh:
		return

	active = scene.sequence_editor.active_strip

	#folder = bpy.path.abspath(active.directory)
	bpy.ops.stopmotion.refresh_sequence()

	# final end is actual handle positions, even if end handles are slid
	if scene.stopmotion_auto_refresh_frames == 0:
		scene.frame_start = active.frame_final_start
	else:
		scene.frame_start = active.frame_final_end - scene.stopmotion_auto_refresh_frames
	scene.frame_end = active.frame_final_end - 1

	# compare elements of active to active directory
	# if mismathc, then trigger refresh


# -----------------------------------------------------------------------------
# User Interface
# -----------------------------------------------------------------------------


def SMB_panel_append(self, context):
	"""Panel placed under the main n-info draw for a selected sequence."""
	layout = self.layout
	col = layout.column()

	#seq_active = context.scene.sequence_editor.active_strip
	# col.operator(SMB_resequence_folder.bl_idname)


class SMB_vse_tools_panel(bpy.types.Panel):
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	bl_label = "Stopmotion Tools"
	bl_category = "Tools"

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)

		# active = context.scene.sequence_editor.active_strip
		# if active and active.type == "IMAGE" and active.elements:
		# 	folder = bpy.path.abspath(active.directory)
		# else:
		# 	folder = ""

		col.prop(context.scene, "stopmotion_auto_refresh")
		row = col.row()
		row.enabled = context.scene.stopmotion_auto_refresh
		row.prop(context.scene, "stopmotion_auto_refresh_frames")

		col.split()
		row = col.row()
		subcol = row.column(align=True)
		subcol.operator(SMB_refresh_sequence.bl_idname)
		subcol.operator(SMB_resequence_folder.bl_idname)

		if hasattr(bpy.ops, "sequencer") and \
				hasattr(bpy.ops.sequencer, "match_sequence_resolution"):
			subcol.operator("sequencer.match_sequence_resolution")

		row = layout.row()


class SMB_preferences(bpy.types.AddonPreferences):
	"""Preferences drawn and settings saved to default blend session."""
	bl_idname = __package__

	project_root = bpy.props.StringProperty(
		name = "Default project folder",
		description = "Path to default project folder for frame capture and watching",
		subtype = "DIR_PATH",
		default = os.path.join(os.path.expanduser("~"),"stopmotion_frames")
		)

	def draw(self, context):
		layout = self.layout
		layout.label("Default project folder")
		layout.prop(self,"project_root")


# -----------------------------------------------------------------------------
# Registration
# -----------------------------------------------------------------------------


def register():
	bpy.utils.register_module(__name__)
	bpy.types.SEQUENCER_PT_edit.append(SMB_panel_append)
	bpy.types.Scene.stopmotion_auto_refresh = bpy.props.BoolProperty(
		name = "Auto refresh active",
		description = "Auto-updated active strip if new image files appear in folder",
		default = False)
	bpy.types.Scene.stopmotion_auto_refresh_frames = bpy.props.IntProperty(
		name = "Refresh frames",
		description = "Number of frames to set scene to from end after refresh, 0 leaves unchanged",
		default = 0,
		min = 0)

	bpy.app.handlers.frame_change_pre.append(frame_change_handler)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.SEQUENCER_PT_edit.remove(SMB_panel_append)

	del bpy.types.Scene.stopmotion_auto_refresh
	if frame_change_handler in bpy.app.handlers.frame_change_pre:
		bpy.app.handlers.frame_change_pre.remove(frame_change_handler)


if __name__ == "__main__":
	register()
