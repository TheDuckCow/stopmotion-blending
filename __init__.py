# -----------------------------------------------------------------------------
# BLENDER STOPMOTION ADDON
# -----------------------------------------------------------------------------
# [ MIT license ]
# -----------------------------------------------------------------------------
# This addon is meant to assist with creating stopmotion animations in blender
# through a variety of importing and image capture tools.
# -----------------------------------------------------------------------------

bl_info = {
    "name": "Stopmotion Blending",
    "author": "Patrick W. Crawford",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "TBD",
    "description": "Help create stopmotion animations leveraging blender",
    "warning": "In development",
    "wiki_url": "https://github.com/TheDuckCow/stopmotion-blending",
    "tracker_url": "https://github.com/TheDuckCow/stopmotion-blending/issues",
    "category": "Sequencer"
}


if "bpy" in locals():

    import importlib
    importlib.reload(stopmotion_blending)

else:

    from . import stopmotion_blending

import bpy



def register():
    bpy.utils.register_module(__name__)
    stopmotion_blending.register()


def unregister():
    bpy.utils.unregister_module(__name__)
    stopmotion_blending.unregister()


if __name__ == "__main__":
    register()
