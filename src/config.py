# config.py

import sys
import os

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

PLAYLISTSAVESPATH = os.path.join(BASE_DIR, 'PlaylistSaves')
HYMNPATH = os.path.join(BASE_DIR, "Hymns")
LITURGYPATH = os.path.join(BASE_DIR, "Liturgy")
PSALMNOTESPATH = os.path.join(BASE_DIR, "PsalmNotes")
OTHERPATH = os.path.join(BASE_DIR, "Other")

kind_to_folder = {
    "Hymn": HYMNPATH,
    "DivineService": LITURGYPATH,
    "PsalmNotes": PSALMNOTESPATH,
    "Vespers": LITURGYPATH,
    "Other": OTHERPATH
}
