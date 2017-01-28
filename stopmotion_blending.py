

import bpy
import os

# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------

v = True # verbose printing


# -----------------------------------------------------------------------------
# Utility functions and classes for propertyies, including update functions
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Blender Operators
# -----------------------------------------------------------------------------


class SMB_resequence_dir(bpy.types.Operator):
	bl_idname = "stopmotion.resequence_dir"
	bl_label = "Resequence"
	bl_description = "Rename the images of a folder to be sequential without gaps"
	#bl_options = {'REGISTER', 'UNDO'}

	folder = bpy.props.StringProperty(
		name = "Folder",
		description = "Folder containing images to resequence",
		subtype = 'DIR_PATH',
		default = ""
		)

	extension_filter = [".png",".jpg",".jpeg"]

	def execute(self, context):

		path = self.folder
		if path == "":
			seq_active = context.scene.sequence_editor.active_strip
			if seq_active.type != 'IMAGE':
				self.report({'ERROR',"Select an image sequence"})
				return {'CANCELLED'}
			npath = bpy.path.abspath(seq_active.directory)
			if os.path.isdir(npath):
				path = npath
			else:
				self.report({'ERROR',"Invalid directory detected on sequence"})
				return {'CANCELLED'}

		onlyfiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		if v:print( onlyfiles)
		
		# convert to make use of self.extension_filter
		pngs = sum( [1 for a in onlyfiles if "png" in a.lower() ])
		jpegs = sum( [1 for a in onlyfiles if "jpg" in a.lower() ])

		ext = None
		if pngs>jpegs:
			if v:print("doing png re-ordering")
			ext = "png"
		elif jpegs>0:
			print("doing jpeg re-ordering")
			ext = "jpg"
		else:
			self.report({'ERROR',"Valid image extention not found"})
			return {'CANCELLED'}
		
		# get just the sequence of files we need
		# adjust later in case of no extensions or 4 letter extentions
		sequence = [ f for f in onlyfiles if f[-3:].lower()==ext ]
		if v:print(sequence)
		
		# get the common prefix and remove trailing digits
		prefix = os.path.commonprefix( sequence ).rstrip('1234567890')
		# this also does not account for there being multiple
		# sequences in the same folder
		
		if v:print("Prefix is:", prefix)

		prefix = os.path.join(path,prefix)
		count = 1
		for p in sequence:
			os.rename(
				os.path.join(path,p),
				prefix+str(count).zfill(4)+p[-4:]
				) # to keep orignal format of extention caps etc
			# detect number of zfill digits in future?
			count+=1
		if v:print("success! But need to reload the sequence")

		# now reload the sequence
		# get starting frame:
		# active_strip.frame_start
		# or can we just change the directory to update?

		return {'FINISHED'}

		


# -----------------------------------------------------------------------------
# Property group
# -----------------------------------------------------------------------------

# possibly eventually

# -----------------------------------------------------------------------------
# User Interface
# -----------------------------------------------------------------------------


def panel_append(self, context):
	layout = self.layout
	col = layout.column()

	#seq_active = context.scene.sequence_editor.active_strip
	col.operator(SMB_resequence_dir.bl_idname, text="Resequence")



# -----------------------------------------------------------------------------
# Preferences
# -----------------------------------------------------------------------------



class SMB_preferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	#scriptdir = bpy.path.abspath(os.path.dirname(__file__))


	project_root = bpy.props.StringProperty(
		name = "Default project folder",
		description = "Path to default project folder for frame capture and watching",
		subtype = 'DIR_PATH',
		default = os.path.join(os.path.expanduser('~'),"stopmotion_frames")
		)

	def draw(self, context):

		layout = self.layout
		layout.label("Default project folder")
		layout.prop(self,"project_root")




def register():
	bpy.types.SEQUENCER_PT_edit.append(panel_append)


def unregister():
	bpy.types.SEQUENCER_PT_edit.remove(panel_append)
	
