import binascii
from enum import Enum

class Channels(Enum):
    Great = 11
    Swell = 12
    Pedal = 13
    Choir = 14
    Disabled = 0

class StopType(Enum):
    REED = "Reed"
    STRING = "String"
    PRINCIPAL = "Principal"
    COUPLER = "Coupler"
    FLUTE = "Flute"

class Stop:
    def __init__(self, code_name, hex_value, stop_type, is_engaged, label_text):
        self.code_name = code_name
        self.hex_value = hex_value
        self.stop_type = StopType(stop_type)
        self.is_engaged = is_engaged
        self.label_text = label_text  # new property for label text

    def to_dict(self):
        return {
            "code_name": self.code_name,
            "hex_value": self.hex_value,
            "stop_type": self.stop_type.value,
            "is_engaged": self.is_engaged,
            "label_text": self.label_text
        }

class Manual:
    def __init__(self, name):
        self.name = name
        self.stops = {}

    def add_stop(self, stop_name, stop):
        self.stops[stop_name] = stop


class Choir(Enum):
    SPITZ_PRINCIPAL_8 = "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    STILL_GEDACKT_8 =   "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #flute
    UNDA_MARIS_II_8 =   "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    SPITZFLOTE_4 =      "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #flute
    PRINCIPAL_2 =       "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    QUINTE_1_1_3 =      "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    SESQUIALTERA_II =   "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #flute
    MIXTUR_III =        "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal mix
    CROMORNE_8 =        "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #reed
    SWELL_TO_CHOIR =    "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 04 00 00 00 00"
    FANFARE_TRUMPET_8 = "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #reed
            #TREMULANT = "F0AH04DE" #principal mix
    #Man II
class Great(Enum):
    VIOLONE_16 =        "01 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #string
    PRINCIPAL_8 =       "01 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    GEMSHORN_8 =        "01 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #hybrid flute/string
    GEDACKT_8 =         "01 00 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #flute
    OCTAVA_4 =          "01 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    QUINTE_2_2_3 =      "01 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    SUPEROCATVA_2 =     "01 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    MIXTUR_IV =         "01 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal mix
    TRUMPET_8 =         "01 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #reed
    SWELL_TO_GREAT =    "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00"
    CHOIR_TO_GREAT =    "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00"
    #    TREMULANT = "F0AH00C9" #principal mix
    #    CHIMES = "F0AH00CA"
    #    ZIMBELSTERN = "F0AH00CB"
class Swell(Enum):
    GEIGEN_DIAPASON_8 =   "01 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    BOURDON_8 =           "01 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"         #flute
    VIOLA_CELESTE_II_8 =  "01 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"    #string
    PRINCIPAL_4 =         "01 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"       #principal
    FLUTE_TRAVERSIERE_4 = "01 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 " #flute
    NASAT_2_2_3 =         "01 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"      #principal
    PICCOLO_2 =           "01 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"       #flute
    TIERCE_1_3_5 =        "01 00 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"   #principal
    PLEIN_JEU_IV =        "01 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"  #principal
    BASSON_16 =           "01 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"   #reed
    HAUTBOIS_8 =          "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"        #reed
        # TREMULANT = "F0AH00EC" #principal mix
class Pedal(Enum):
    MONTRE_32 =       "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00 00 00 00 00 09 00 00"
    PRINCIPAL_16 =    "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    SUBBASS_16 =      "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00" #principal
    OCTAVA_8 =        "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00 00 00 00 00" #principal
    BOURDON_8 =       "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00"    #flute
    CHORAL_BASS_4 =   "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00" #principal
    POSAUNE_16 =      "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00" 
    TROMPETE_8 =      "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00" #reed
    KLARINE_4 =       "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00" #reed
    CHOIR_TO_PEDAL =  "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00"
    GREAT_TO_PEDAL =  "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 00 00 00 00 00 00"
    SWELL_TO_PEDAL =  "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00"


manuals = {
}

#manuals["Manual1"].add_stop("Stop1", Stop("Code1", "Hex1", "Reed", False))

choir = Manual("Choir")
great = Manual("Great")
swell = Manual("Swell")
pedal = Manual("Pedal")

# Add the stops to the Great manual
great.add_stop("VIOLONE_16", Stop("VIOLONE_16", Great.VIOLONE_16.value, StopType.STRING.value, False, "Violone\n16"))
great.add_stop("PRINCIPAL_8", Stop("PRINCIPAL_8", Great.PRINCIPAL_8.value, StopType.PRINCIPAL.value, False, "Principal\n8"))
great.add_stop("GEMSHORN_8", Stop("GEMSHORN_8", Great.GEMSHORN_8.value, StopType.STRING.value, False, "Gemshorn\n8"))
great.add_stop("GEDACKT_8", Stop("GEDACKT_8", Great.GEDACKT_8.value, StopType.FLUTE.value, False, "Gedackt\n8"))
great.add_stop("OCTAVA_4", Stop("OCTAVA_4", Great.OCTAVA_4.value, StopType.PRINCIPAL.value, False, "Octava\n4"))
great.add_stop("QUINTE_2_2_3", Stop("QUINTE_2_2_3", Great.QUINTE_2_2_3.value, StopType.PRINCIPAL.value, False, "Quinte\n2 2/3"))
great.add_stop("SUPEROCATVA_2", Stop("SUPEROCATVA_2", Great.SUPEROCATVA_2.value, StopType.PRINCIPAL.value, False, "Superoctav\n2"))
great.add_stop("MIXTUR_IV", Stop("MIXTUR_IV", Great.MIXTUR_IV.value, StopType.PRINCIPAL.value, False, "Mixtur\nIV"))
great.add_stop("TRUMPET_8", Stop("TRUMPET_8", Great.TRUMPET_8.value, StopType.REED.value, False, "Trumpet\n8"))
great.add_stop("SWELL_TO_GREAT", Stop("SWELL_TO_GREAT", Great.SWELL_TO_GREAT.value, StopType.COUPLER.value, False, "III/II"))
great.add_stop("CHOIR_TO_GREAT", Stop("CHOIR_TO_GREAT", Great.CHOIR_TO_GREAT.value, StopType.COUPLER.value, False, "I/II"))


# Add the stops to the Swell manual
swell.add_stop("GEIGEN_DIAPASON_8", Stop("GEIGEN_DIAPASON_8", Swell.GEIGEN_DIAPASON_8.value, StopType.STRING.value, False, "Geigen\nDiapason\n8"))
swell.add_stop("BOURDON_8", Stop("BOURDON_8", Swell.BOURDON_8.value, StopType.FLUTE.value, False, "Bourdon\n8"))
swell.add_stop("VIOLA_CELESTE_II_8", Stop("VIOLA_CELESTE_II_8", Swell.VIOLA_CELESTE_II_8.value, StopType.STRING.value, False, "Voila\nCeleste\nII"))
swell.add_stop("PRINCIPAL_4", Stop("PRINCIPAL_4", Swell.PRINCIPAL_4.value, StopType.PRINCIPAL.value, False, "Principal\n4"))
swell.add_stop("FLUTE_TRAVERSIERE_4", Stop("FLUTE_TRAVERSIERE_4", Swell.FLUTE_TRAVERSIERE_4.value, StopType.FLUTE.value, False, "Flût\nTraversière\n4"))
swell.add_stop("NASAT_2_2_3", Stop("NASAT_2_2_3", Swell.NASAT_2_2_3.value, StopType.PRINCIPAL.value, False, "Nasat\n2 2/3"))
swell.add_stop("PICCOLO_2", Stop("PICCOLO_2", Swell.PICCOLO_2.value, StopType.FLUTE.value, False, "Piccolo\n2"))
swell.add_stop("TIERCE_1_3_5", Stop("TIERCE_1_3_5", Swell.TIERCE_1_3_5.value, StopType.PRINCIPAL.value, False, "Tierce\n1 3/5"))
swell.add_stop("PLEIN_JEU_IV", Stop("PLEIN_JEU_IV", Swell.PLEIN_JEU_IV.value, StopType.PRINCIPAL.value, False, "Plein\nJeu\nIV"))
swell.add_stop("BASSON_16", Stop("BASSON_16", Swell.BASSON_16.value, StopType.REED.value, False, "Basson\n16"))
swell.add_stop("HAUTBOIS_8", Stop("HAUTBOIS_8", Swell.HAUTBOIS_8.value, StopType.REED.value, False, "Hautbois\n8"))


# Add the stops to the Pedal manual
pedal.add_stop("MONTRE_32", Stop("MONTRE_32", Pedal.MONTRE_32.value, StopType.PRINCIPAL.value, False, "Montre\n32"))
pedal.add_stop("PRINCIPAL_16", Stop("PRINCIPAL_16", Pedal.PRINCIPAL_16.value, StopType.PRINCIPAL.value, False, "Principal\n16"))
pedal.add_stop("SUBBASS_16", Stop("SUBBASS_16", Pedal.SUBBASS_16.value, StopType.PRINCIPAL.value, False, "Subbass\n16"))
pedal.add_stop("OCTAVA_8", Stop("OCTAVA_8", Pedal.OCTAVA_8.value, StopType.PRINCIPAL.value, False, "Octava\n8"))
pedal.add_stop("BOURDON_8", Stop("BOURDON_8", Pedal.BOURDON_8.value, StopType.FLUTE.value, False, "Bourdon\n8"))
pedal.add_stop("CHORAL_BASS_4", Stop("CHORAL_BASS_4", Pedal.CHORAL_BASS_4.value, StopType.PRINCIPAL.value, False, "Choralbass\n4"))
pedal.add_stop("POSAUNE_16", Stop("POSAUNE_16", Pedal.POSAUNE_16.value, StopType.REED.value, False, "Posaune\n16"))
pedal.add_stop("TROMPETE_8", Stop("TROMPETE_8", Pedal.TROMPETE_8.value, StopType.REED.value, False, "Trompete\n8"))
pedal.add_stop("KLARINE_4", Stop("KLARINE_4", Pedal.KLARINE_4.value, StopType.REED.value, False, "Klarine\n4"))
pedal.add_stop("CHOIR_TO_PEDAL", Stop("CHOIR_TO_PEDAL", Pedal.CHOIR_TO_PEDAL.value, StopType.COUPLER.value, False, "I/P"))
pedal.add_stop("GREAT_TO_PEDAL", Stop("GREAT_TO_PEDAL", Pedal.GREAT_TO_PEDAL.value, StopType.COUPLER.value, False, "II/P"))
pedal.add_stop("SWELL_TO_PEDAL", Stop("SWELL_TO_PEDAL", Pedal.SWELL_TO_PEDAL.value, StopType.COUPLER.value, False, "III/P"))

# Create Stop objects for each stop in the Choir and add them to the Choir manual
choir.add_stop("SPITZ_PRINCIPAL_8", Stop("SPITZ_PRINCIPAL_8", Choir.SPITZ_PRINCIPAL_8.value, StopType.PRINCIPAL.value, False, "Spitz\nPrincipal\n8"))
choir.add_stop("STILL_GEDACKT_8", Stop("STILL_GEDACKT_8", Choir.STILL_GEDACKT_8.value, StopType.FLUTE.value, False, "Still\nGedackt\n8"))
choir.add_stop("UNDA_MARIS_II_8", Stop("UNDA_MARIS_II_8", Choir.UNDA_MARIS_II_8.value, StopType.STRING.value, False, "Unda\nMaris\nII"))
choir.add_stop("SPITZFLOTE_4", Stop("SPITZFLOTE_4", Choir.SPITZFLOTE_4.value, StopType.FLUTE.value, False, "Spitzflöte\n4"))
choir.add_stop("PRINCIPAL_2", Stop("PRINCIPAL_2", Choir.PRINCIPAL_2.value, StopType.PRINCIPAL.value, False, "Principal\n2"))
choir.add_stop("QUINTE_1_1_3", Stop("QUINTE_1_1_3", Choir.QUINTE_1_1_3.value, StopType.PRINCIPAL.value, False, "Quinte\n1 1/3"))
choir.add_stop("SESQUIALTERA_II", Stop("SESQUIALTERA_II", Choir.SESQUIALTERA_II.value, StopType.FLUTE.value, False, "Sesquialtera\nII"))
choir.add_stop("MIXTUR_III", Stop("MIXTUR_III", Choir.MIXTUR_III.value, StopType.PRINCIPAL.value, False, "Mixtur\nIII"))
choir.add_stop("CROMORNE_8", Stop("CROMORNE_8", Choir.CROMORNE_8.value, StopType.REED.value, False, "Cromorne\n8"))
choir.add_stop("SWELL_TO_CHOIR", Stop("SWELL_TO_CHOIR", Choir.SWELL_TO_CHOIR.value, StopType.COUPLER.value, False, "III/I"))
choir.add_stop("FANFARE_TRUMPET_8", Stop("FANFARE_TRUMPET_8", Choir.FANFARE_TRUMPET_8.value, StopType.REED.value, False, "Fanfare\nTrumpet\n8"))

# Add the Choir manual to the manuals dictionary
manuals["Choir"] = choir
manuals["Great"] = great
manuals["Swell"] = swell
manuals["Pedal"] = pedal


# Add more stops to manuals as needed

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) % 128
    checksum = 128 - checksum
    return checksum

NO_STOPS = "01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
HEADER = "41 10 30 12"
FOOTER = "F7"
def get_sysex(stops):

    sysex = bytes.fromhex("F0" + HEADER)
    data = bytes.fromhex(NO_STOPS)
    for stop in stops:
      #  print(stop)
        data_bytes = bytes.fromhex(stop.hex_value)
      #  print(data_bytes)
        data = bytes(a | b for a, b in zip(data, data_bytes))
    
    calculated_checksum = calculate_checksum(data)
    sysex += data + bytes([calculated_checksum]) + bytes.fromhex(FOOTER)
    sysex_string = ' '.join(binascii.hexlify(sysex).decode()[i:i+2] for i in range(0, len(binascii.hexlify(sysex).decode()), 2))
    return sysex_string

def get_stops_from_sysex(sysex_string):
    sysex_string = sysex_string[len(HEADER)+1:-len(FOOTER)-1]
    data = bytes.fromhex(sysex_string)
    stops = []
    for manual in manuals.values():
        for stop in manual.stops.values():  # Assuming Stops.ALL_STOPS contains all possible stops
            stop_bytes = bytes.fromhex(stop.hex_value)
            if all((a & b) == b for a, b in zip(data, stop_bytes)):  # If all bits in stop are set in data
                stops.append(stop)
    return stops

class DefaultSettings:
    def __init__(self):
        self.default_stop_settings = [
            choir.stops["SPITZ_PRINCIPAL_8"],
            choir.stops["SPITZFLOTE_4"],
            choir.stops["SWELL_TO_CHOIR"],
            great.stops["PRINCIPAL_8"],
            great.stops["OCTAVA_4"],
            great.stops["SWELL_TO_GREAT"],
            swell.stops["GEIGEN_DIAPASON_8"],
            swell.stops["PRINCIPAL_4"],
            swell.stops["PICCOLO_2"],
            pedal.stops["PRINCIPAL_16"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["BOURDON_8"],
        ]
        self.intro_stop_settings = [
            great.stops["VIOLONE_16"],
            great.stops["GEMSHORN_8"],
            pedal.stops["CHOIR_TO_PEDAL"],
            choir.stops["STILL_GEDACKT_8"],
            choir.stops["UNDA_MARIS_II_8"],
        ]
        self.prelude_stop_settings = [
            #great.stops["PRINCIPAL_8"],
            great.stops["GEMSHORN_8"],
            great.stops["OCTAVA_4"],
            great.stops["SWELL_TO_GREAT"],
            swell.stops["GEIGEN_DIAPASON_8"],
            swell.stops["PRINCIPAL_4"],
            swell.stops["BOURDON_8"],
            swell.stops["FLUTE_TRAVERSIERE_4"],
            pedal.stops["PRINCIPAL_16"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["BOURDON_8"]
        ]
        self.grand_symphony_stop_settings = [
            great.stops["VIOLONE_16"],
            great.stops["PRINCIPAL_8"],
            great.stops["GEMSHORN_8"],
            great.stops["OCTAVA_4"],
            swell.stops["GEIGEN_DIAPASON_8"],
            swell.stops["NASAT_2_2_3"],
            swell.stops["HAUTBOIS_8"],
            great.stops["SWELL_TO_GREAT"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["CHORAL_BASS_4"],
            pedal.stops["OCTAVA_8"],
        ]
        
        self.choir_serenade_stop_settings = [
            choir.stops["SPITZ_PRINCIPAL_8"],
            choir.stops["UNDA_MARIS_II_8"],
            choir.stops["SPITZFLOTE_4"],
            great.stops["PRINCIPAL_8"],
            great.stops["OCTAVA_4"],
            great.stops["CHOIR_TO_GREAT"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["CHORAL_BASS_4"],
            pedal.stops["OCTAVA_8"],
        ]

        self.baroque_brilliance_stop_settings = [
            great.stops["PRINCIPAL_8"],
            great.stops["QUINTE_2_2_3"],
            great.stops["MIXTUR_IV"],
            swell.stops["GEIGEN_DIAPASON_8"],
            swell.stops["NASAT_2_2_3"],
            swell.stops["HAUTBOIS_8"],
            pedal.stops["SWELL_TO_PEDAL"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["CHORAL_BASS_4"],
            pedal.stops["OCTAVA_8"],
        ]

        self.celestial_strings_stop_settings = [
            great.stops["VIOLONE_16"],
            great.stops["GEMSHORN_8"],
            great.stops["GEDACKT_8"],
            swell.stops["VIOLA_CELESTE_II_8"],
            swell.stops["FLUTE_TRAVERSIERE_4"],
            great.stops["SWELL_TO_GREAT"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["CHORAL_BASS_4"],
            pedal.stops["OCTAVA_8"],
        ]

        self.majestic_mix_stop_settings = [
            great.stops["VIOLONE_16"],
            great.stops["PRINCIPAL_8"],
            great.stops["MIXTUR_IV"],
            great.stops["TRUMPET_8"],
            swell.stops["GEIGEN_DIAPASON_8"],
            swell.stops["NASAT_2_2_3"],
            swell.stops["PICCOLO_2"],
            swell.stops["TIERCE_1_3_5"],
            pedal.stops["SWELL_TO_PEDAL"],
            pedal.stops["SUBBASS_16"],
            pedal.stops["POSAUNE_16"],
            pedal.stops["OCTAVA_8"],
        ]


    def get_default_stops(self, preset):
        if preset == "default":
            return self.default_stop_settings
        elif preset == "intro":
            return self.intro_stop_settings
        elif preset == "prelude":
            return self.prelude_stop_settings
        elif preset == "g1":
            return self.grand_symphony_stop_settings
        elif preset == "g2":
            return self.choir_serenade_stop_settings
        elif preset == "g3":
            return self.baroque_brilliance_stop_settings
        elif preset == "g4":
            return self.celestial_strings_stop_settings
        elif preset == "g5":
            return self.majestic_mix_stop_settings
        else:
            return self.default_stop_settings
        
program_change_dict = {}
program_changes = '''1	Acoustic Grand Piano
2	Bright Acoustic Piano
3	Electric Grand Piano
4	Honky-tonk Piano
5	Electric Piano 1 (Rhodes Piano)
6	Electric Piano 2 (Chorused Piano)
7	Harpsichord
8	Clavinet
9	Celesta
10	Glockenspiel
11	Music Box
12	Vibraphone
13	Marimba
14	Xylophone
15	Tubular Bells
16	Dulcimer (Santur)
17	Drawbar Organ (Hammond)
18	Percussive Organ
19	Rock Organ
20	Church Organ
21	Reed Organ
22	Accordion (French)
23	Harmonica
24	Tango Accordion (Band neon)
25	Acoustic Guitar (nylon)
26	Acoustic Guitar (steel)
27	Electric Guitar (jazz)
28	Electric Guitar (clean)
29	Electric Guitar (muted)
30	Overdriven Guitar
31	Distortion Guitar
32	Guitar harmonics
33	Acoustic Bass
34	Electric Bass (fingered)
35	Electric Bass (picked)
36	Fretless Bass
37	Slap Bass 1
38	Slap Bass 2
39	Synth Bass 1
40	Synth Bass 2
41	Violin
42	Viola
43	Cello
44	Contrabass
45	Tremolo Strings
46	Pizzicato Strings
47	Orchestral Harp
48	Timpani
49	String Ensemble 1 (strings)
50	String Ensemble 2 (slow strings)
51	SynthStrings 1
52	SynthStrings 2
53	Choir Aahs
54	Voice Oohs
55	Synth Voice
56	Orchestra Hit
57	Trumpet
58	Trombone
59	Tuba
60	Muted Trumpet
61	French Horn
62	Brass Section
63	SynthBrass 1
64	SynthBrass 2
65	Soprano Sax
66	Alto Sax
67	Tenor Sax
68	Baritone Sax
69	Oboe
70	English Horn
71	Bassoon
72	Clarinet
73	Piccolo
74	Flute
75	Recorder
76	Pan Flute
77	Blown Bottle
78	Shakuhachi
79	Whistle
80	Ocarina
81	Lead 1 (square wave)
82	Lead 2 (sawtooth wave)
83	Lead 3 (calliope)
84	Lead 4 (chiffer)
85	Lead 5 (charang)
86	Lead 6 (voice solo)
87	Lead 7 (fifths)
88	Lead 8 (bass + lead)
89	Pad 1 (new age Fantasia)
90	Pad 2 (warm)
91	Pad 3 (polysynth)
92	Pad 4 (choir space voice)
93	Pad 5 (bowed glass)
94	Pad 6 (metallic pro)
95	Pad 7 (halo)
96	Pad 8 (sweep)
97	FX 1 (rain)
98	FX 2 (soundtrack)
99	FX 3 (crystal)
100	FX 4 (atmosphere)
101	FX 5 (brightness)
102	FX 6 (goblins)
103	FX 7 (echoes, drops)
104	FX 8 (sci-fi, star theme)
105	Sitar
106	Banjo
107	Shamisen
108	Koto
109	Kalimba
110	Bag pipe
111	Fiddle
112	Shanai
113	Tinkle Bell
114	Agogo
115	Steel Drums
116	Woodblock
117	Taiko Drum
118	Melodic Tom
119	Synth Drum
120	Reverse Cymbal
121	Guitar Fret Noise
122	Breath Noise
123	Seashore
124	Bird Tweet
125	Telephone Ring
126	Helicopter
127	Applause
128	Gunshot'''

lines = program_changes.split('\n')
for line in lines:
    parts = line.split('\t')
    program_number = int(parts[0])
    program_name = parts[1]
    program_change_dict[program_number] = program_name
