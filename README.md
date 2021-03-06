# stopmotion-blending
A blender 3d addon with a collection of tools assisting with stopmotion animation

This is intended to assist creating stopmotion animations using blender as part of the capturing workflow (not to be confused with attempts to make CG animation look like stopmotion).

Note that these features are based on a workflow where an external program performs remote capture on a DSLR or webcam and auto saves the result into a folder. The tools here refelct management of these images or "frames" added to this output folder for faster/automatic preview of the stopmotion sequences inside blender, as well as dealing with deleting frames mid-sequence, or inserting new frames into different parts of the sequence.

# Implemented features

- Refresh Sequence:
  - Takes the actively selected VSE image sequence and reloads all frames for that image sequence. This means added or removed frames from the sequence will be reflected
  - Reloads based on taking the string pattern of the first image sequence frame filename and the sequence's folder.
  - Refresh respects the first image already set in the image sequence; even if lower-numbered frames are in the existing folder, the firs refreshed frame will always be the currently selected one.
  - Auto extends the length of the strip to match last found image
  - Images do not need to be sequential, or technically even have frame numbers!
- Resequence:
  - Take the target folder (or if none specified, take the folder of the currently active image sequence) and rename all image files in that folder to have a common sub name and sequentially increasing 4-digit number afterwards. Useful if taking the sequences into
  - Does not necessiarly take in the current frame order of the strip, and does not yet reload the strip (in fact, will need to run refresh sequence on it afterwards!)
  - Note: this does not yet refresh the sequence itself, only renames the files.
  - Note: this operator currently assumes only one image sequence per folder.
- Auto refresh active & refresh frame:
  - If enabled, will run refresh sequence on the active VSE sequence every time the frame changes, so playing the animation will always ensure the latest sequence of frames are loaded in

# Future plans

**Nothing has yet been implemented, so this is a wish-list**

- Watch folder
  - While enabled, folders can be selected (enabled/toggled) under a list view to mark as being watched. This is then used elsewhere by the addon.
  - Would also be nice to have the ability to auto load folders or have saved "project" sets of folders from preferences
- Sequence re-ordering of alraedy (not necessairly aphabetically) ordered image sequence
  - An operator that when used, will re-sequence the corresponding image folders given the order of the current image sequence strip, so that any deleted/reordered frames, or lapses in numbers generated by the camera are resolved into a sequential list of image file frames.
  - It could also handle in a special way "deleted frames" or "retakes" with a prefix
- Stopmotion frame operators
  - Delete a frame
  - Copy a frame forward/backwards
  - Retake a frame
  - Keep track of parallel angles/cameras, for multi cam. If two sequences are selected to operate in parallel, functions such as frame insertion, re-sequencing etc should keep in mind parallel operations on those linked sequences
  - Onion skinning
    - Again, if sequence setup in meta strip, this could be somewhat easily acocmplished by layered opacity strips. May have slow playback, though could use proxies for the faded out onion frames.
- Self-managed caching and resolutions
  - If enabled, auto create low resolution image sequences
  - If enabled, auto create (and update at time of blend-file saving) a low res movie of the sequence
- Image capture
  - Stretch goal, making use of existing python libraries to directly control remote image capture from DSLR's (first priority) and webcams.
  - Note: It is not an intended goal to make a live-capture window, but rather create a dedicated runtime program which shows the capture window and is controlled/communicates directly the blender addon.

# Additional notes

For all support related items, please [open a new issue](https://github.com/TheDuckCow/stopmotion-blending/issues).
