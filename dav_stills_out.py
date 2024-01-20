#!/usr/bin/env python
# Olivier PATRON - 2023 v1.04
# DaVinci Resolve API driven script to export all marked frames in a timeline as a still

import sys
import os
import glob

print("\n\n[DAV script] Starting script execution (export stills) \U0001F4A1\n")

# from https://stackoverflow.com/questions/8884188/how-to-read-and-write-ini-file-with-python3
class IniOpen:
    def __init__(self, inifile):
        self.parse = {}
        self.file = inifile
        self.open = open(inifile, "r")
        self.f_read = self.open.read()
        split_content = self.f_read.split("\n")

        section = ""
        pairs = ""

        for i in range(len(split_content)):
            if split_content[i].find("#") == 0:
                continue
            elif split_content[i].find("#") == -1 and split_content[i].find(":"):
                pairs = split_content[i]
                split_pairs = pairs.split(":")
                inikey = split_pairs[0]
                value = split_pairs[1]
                self.parse.update({inikey: value})

    def read(self, inikey):
        try:
            return self.parse[inikey]
        except KeyError:
            print("[DAV script] \U0000274C ERROR: config file error trying to access key " + inikey)

def GetResolve():
    try:
    # The PYTHONPATH needs to be set correctly for this import statement to work.
    # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
        import DaVinciResolveScript as bmd
    except ImportError:
        if sys.platform.startswith("darwin"):
            expectedPath="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            import os
            expectedPath=os.getenv('PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
        elif sys.platform.startswith("linux"):
            expectedPath="/opt/resolve/libs/Fusion/Modules/"

        # check if the default path has it...
        # print("[DAV script] Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
        try:
            import imp
            bmd = imp.load_source('DaVinciResolveScript', expectedPath+"DaVinciResolveScript.py")
        except ImportError:
            # No fallbacks ... report error:
            print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
            print("For a default DaVinci Resolve installation, the module is expected to be located in: "+expectedPath)
            sys.exit()

    return bmd.scriptapp("Resolve")

def frameToTimecode(framenumber, fps):
    ff = framenumber % fps
    ss = framenumber // fps
    mm = ss // 60
    hh = mm // 60
    ss = ss % 60
    mm = mm % 60
    return str(hh).zfill(2) + ":" + str(mm).zfill(2) + ":" + str(ss).zfill(2) + ":" + str(ff).zfill(2)

def timecodeToFrame(timecode, fps):
    tc_val = timecode.split(":")
    return int(tc_val[0])*3600*fps + int(tc_val[1])*60*fps + int(tc_val[2])*fps + int(tc_val[3])

# add timecodes, return timecode
def tc_addTimecodes(tc1, tc2, fps):
    return frameToTimecode(timecodeToFrame(tc1, fps) + timecodeToFrame(tc2, fps), fps)

# add timecodes, return framenumber
def frame_addTimecodes(tc1, tc2, fps):
    return timecodeToFrame(tc1, fps) + timecodeToFrame(tc2, fps)

# add timecode and frame, return timecode
def tc_addTimecodeFrame(tc1, frame2, fps):
    return frameToTimecode(timecodeToFrame(tc1, fps) + frame2, fps)

# add timecode and frame, return framenumber
def frame_addTimecodeFrame(tc1, frame2, fps):
    return timecodeToFrame(tc1, fps) + frame2

# walk all project folders (bins) and subfolders, return list of every bins included in @parentFolder
def scrubDavBins(parentFolder):
    bins = []
    bins += parentFolder.GetSubFolderList()
    for subbin in bins:
        bins += scrubDavBins(subbin)
    return bins


resolve = GetResolve()
if not resolve:
    print("[DAV script] \U0000274C ERROR: Unable to get to Resolve!")
    sys.exit()


projectManager = resolve.GetProjectManager()
resolve.OpenPage("Color")

iniSettings = IniOpen(os.path.join(os.path.dirname(sys.argv[0]), "config.ini"))
# print(iniSettings.parse)  # DEBUG

project = projectManager.GetCurrentProject()
if not project:
    print("[DAV script] \U0000274C ERROR: Please open the expected project!")
    sys.exit()


timeline = project.GetCurrentTimeline()  # idem as in project but for timeline : current with check or by name ?
if not timeline:
    print("[DAV script] \U0000274C ERROR: No timeline found in project")
    sys.exit()

framerate = timeline.GetSetting("timelineFrameRate")

gallery = project.GetGallery()  # prepare stills gallery for gathering new stills (delete all...)
galleryAllAlbums = gallery.GetGalleryStillAlbums()

galleryName = iniSettings.read("Gallery")
if len(sys.argv) == 3:
    galleryName = sys.argv[2]

galleryAlbum = None
for album in galleryAllAlbums:
    if gallery.GetAlbumName(album) == galleryName:
        album.DeleteStills(album.GetStills())
        galleryAlbum = album

if not galleryAlbum:
    print("[DAV script] \U0000274C ERROR: You need to set a new still album named \"" + galleryName + "\" (or edit your config file)")
    sys.exit()

# print(timeline.GetSetting())  # DEBUG

gallery.SetCurrentStillAlbum(galleryAlbum)
markers = timeline.GetMarkers()  # get all markers from timeline, will sort by [color]type later

if len(markers) == 0:
    print("[DAV script] \U00002757 WARNING: No stills marked to export... Exiting the script")
    print("Turning off the light \U0001F319\n\n")
    sys.exit()

for key in markers.copy():
    if not markers[key]['color'] == iniSettings.read("MarkerColor"):
        markers.pop(key)

if len(markers) == 0:
    print("[DAV script] \U00002757 WARNING: No stills marked to export... Exiting the script")
    print("Turning off the light \U0001F319\n\n")
    sys.exit()

# if we want to export only markers inside in/out timeline's marks
# we need to scrub all media pool folders to look for timeline and get its "clip settings" (thanks f*ck resolve api)
if iniSettings.read("LimitInOut") == "Yes":
    markIn = ""
    markOut = ""
    allBins = []
    allBins.append(project.GetMediaPool().GetRootFolder())
    allBins += scrubDavBins(allBins[0])
    for bi in allBins:
        allClipList = bi.GetClipList()
        hasFound = False
        for clip in allClipList:
            if clip.GetName() == timeline.GetName():
                markIn = clip.GetClipProperty("Start TC")
                markOut = clip.GetClipProperty("End TC")
                if clip.GetClipProperty("In") != "":
                    markIn = clip.GetClipProperty("In")
                if clip.GetClipProperty("Out") != "":
                    markOut = clip.GetClipProperty("Out")
                hasFound = True
                break
        if hasFound:
            break

    markIn_frame = timecodeToFrame(markIn, framerate)
    markOut_frame = timecodeToFrame(markOut, framerate)
    for key in markers.copy():
        keyFrameNb = frame_addTimecodeFrame(timeline.GetStartTimecode(), key, framerate)
        if keyFrameNb < markIn_frame:
            markers.pop(key)
            continue
        if keyFrameNb > markOut_frame:
            markers.pop(key)
            continue

    if len(markers) == 0:
        print("[DAV script] \U00002757 WARNING: No stills marked to export inside in/out timeline's marks... Exiting the script")
        print("Turning off the light \U0001F319\n\n")
        sys.exit()

gradedStillsPath = iniSettings.read("OutputPath")
if gradedStillsPath == "":
    gradedStillsPath = os.path.join(os.path.expanduser('~'), "Documents")

timelineNamed = iniSettings.read("TimelineNamedFolder")
if len(sys.argv) == 2:
    gradedStillsPath = os.path.join(gradedStillsPath, sys.argv[1])
elif timelineNamed != "":
    gradedStillsPath = os.path.join(gradedStillsPath, timeline.GetName())



print("\n[DAV script] Exporting GRADED stills...")
print("\n\t\U0001F916\t\U0001F916\t\U0001F916")
print("\tproject: " + project.GetName())
print("\ttimeline: " + timeline.GetName())
print("\tgallery: " + galleryName)
print("\tstills output folder: " + gradedStillsPath)
print("\n")
print("\tstills marker color: " + iniSettings.read("MarkerColor"))
timelineInOut = "No"
if iniSettings.read("LimitInOut") == "Yes":
    timelineInOut = "Yes"
print("\ttimeline in/out only: " + timelineInOut)
drxDelete = "No"
if iniSettings.read("DeleteDRX") == "Yes":
    drxDelete = "Yes"
print("\t.drx deletion: " + drxDelete)
stillWidth = timeline.GetSetting('timelineResolutionWidth')
stillHeight = timeline.GetSetting('timelineResolutionHeight')
if iniSettings.read("StillResolutionOverride") == "Yes":
    stillWidth = iniSettings.read("StillWidth")
    stillHeight = iniSettings.read("StillHeight")
print("\tstill width: " + stillWidth)
print("\tstill height: " + stillHeight)

print("\t\U0001F916\t\U0001F916\t\U0001F916")

print("\n[DAV script] Expected number of stills:", len(markers))

stillsOverride = False
if iniSettings.read("StillResolutionOverride") == "Yes":
    if iniSettings.read("StillWidth") != "" and iniSettings.read("StillHeight") != "":
        resTimelineWidth = timeline.GetSetting('timelineResolutionWidth')
        resTimelineHeight = timeline.GetSetting('timelineResolutionHeight')
        resProjectWidth = project.GetSetting('timelineResolutionWidth')
        resProjectHeight = project.GetSetting('timelineResolutionHeight')
        timeline.SetSetting('timelineResolutionWidth', '3840')
        timeline.SetSetting('timelineResolutionHeight', '2160')
        project.SetSetting('timelineResolutionWidth', '3840')
        project.SetSetting('timelineResolutionHeight', '2160')
        stillsOverride = True

for key in markers:
    if markers[key]['color'] == iniSettings.read("MarkerColor"):
        # print("is blue")  # DEBUG
        timeline.SetCurrentTimecode(tc_addTimecodeFrame(timeline.GetStartTimecode(), key, framerate))
        timeline.GrabStill()

if stillsOverride:
    timeline.SetSetting('timelineResolutionWidth', resTimelineWidth)
    timeline.SetSetting('timelineResolutionHeight', resTimelineHeight)
    project.SetSetting('timelineResolutionWidth', resProjectWidth)
    project.SetSetting('timelineResolutionHeight', resProjectHeight)

print("[DAV script] Returned " + str(len(galleryAlbum.GetStills())) + " GRADED stills.")
if not len(markers) == len(galleryAlbum.GetStills()):
    print("[DAV script] \U0000274C ERROR: DaV did not grab every marked stills!")
    req = input("[DAV script] Do you want to continue nonetheless? [y/n]")
    if not req == "y":
        print("[DAV script] Script exited.")
        sys.exit()
else:
    print("[DAV script] SUCCESS: All stills were grabbed!")

print("\n[DAV script] Writing GRADED stills to disk.")

if not os.path.exists(gradedStillsPath):
    os.makedirs(gradedStillsPath)

if galleryAlbum.ExportStills(galleryAlbum.GetStills(), gradedStillsPath, "", "jpg"):
    print("[DAV script] SUCCESS: All stills were exported to disk.")
    if iniSettings.read("DeleteDRX") == "Yes":
        for file in glob.glob(gradedStillsPath + "/*.drx"):
            os.remove(file)
else:
    print("[DAV script] \U0000274C ERROR: GRADED Stills were not exported to disk!")
    print("[DAV script] check if still folder name exists, even if lower or upper case (case insensitive lookup)")
    req = input("[DAV script] Do you want to continue nonetheless? [y/n]")
    if not req == "y":
        print("[DAV script] Script exited.")
        sys.exit()

print("\n[DAV script] Finished script (dav_stills.py). Turning off the light \U0001F319\n\n")