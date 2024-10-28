with open("version.txt", "r") as f: QEversion = f.read()

# local imports
from webserver import *
from logger import Log
import AIOMG

import sys
if sys.version_info.major >= 3: pass
else: print("You are not running this program with Python 3, run it with Python 3. (Or update python)"); exit()

try:
    import re, pyttsx3, requests, shutil, time, socket, threading, json, os, argparse, base64, subprocess, importlib
    import sounddevice as sd
    from scipy.io import wavfile
    from datetime import datetime, timezone
    from urllib.request import Request, urlopen
    from EASGen import EASGen
    from EAS2Text import EAS2Text
    #from itertools import zip_longest
    from pydub import AudioSegment
except Exception as e: print(f"IMPORT FAIL: {e}.\nOne or more modules has failed to import, install the requirements!"); exit()

try: import pythoncom
except: pass

if __name__ == "__main__":
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0: print(f"Congrats, QuantumENDEC was able to detect FFMPEG!")
        else:
            print(f"QuantumENDEC failed to detect FFMPEG!: {result.stderr}")
            print("FFMPEG doesn't appear to be installed on your system, you will need to install it so it can be run on a command line. Some functions of QuantumENDEC depend on FFMPEG")
            exit()
    except:
        print("FFMPEG doesn't appear to be installed on your system, you will need to install it so it can be run on a command line. Some functions of QuantumENDEC depend on FFMPEG")
        exit()

def Clear(): os.system('cls' if os.name == 'nt' else 'clear')

def UpdateStatus(service, content):
    try:
        statFolder = "stats"
        with open(f"{statFolder}/{service}_status.txt", "w") as f: f.write(content)
    except: pass

def Plugins_Run(mode=None, ZCZC=None, BROADCASTTEXT=None, XML=None):
    # execute plugin with: GeneratedHeader, BroadcastText, InfoXML
    pluginFolder = "plugins"
    ZCZC = str(ZCZC).replace("\n","")
    BROADCASTTEXT = str(BROADCASTTEXT).replace("\n"," ")
    XML = str(XML).replace("\n"," ")

    if not os.path.exists(pluginFolder): pass
    else:
        print("Attempting to run plugins...")
        pluginList = os.listdir(pluginFolder)

        if mode == "beforeRelay":
            for plug in pluginList:
                if ".py" in plug:
                    plug = plug.replace(".py", "")
                    plug = f"{pluginFolder}.{plug}"
                    try:
                        print("importing... ", plug)
                        module = importlib.import_module(plug)
                        print("Running plugin: ", plug)
                        module.ExecutePlugin_BeforeRelay(ZCZC, BROADCASTTEXT, XML)
                    except Exception as e: print(f"{plug} has failed to run.", e)

        elif mode == "afterRelay":
            for plug in pluginList:
                if ".py" in plug:
                    plug = plug.replace(".py", "")
                    plug = f"{pluginFolder}.{plug}"
                    try:
                        print("importing... ", plug)
                        module = importlib.import_module(plug)
                        print("Running plugin: ", plug)
                        module.ExecutePlugin_AfterRelay(ZCZC, BROADCASTTEXT, XML)
                    except Exception as e: print(f"{plug} has failed to run.", e)
        
        elif mode == "startup":
            for plug in pluginList:
                if ".py" in plug:
                    plug = plug.replace(".py", "")
                    plug = f"{pluginFolder}.{plug}"
                    try:
                        print("importing... ", plug)
                        module = importlib.import_module(plug)
                        print("Running plugin: ", plug)
                        module.ExecutePlugin_OnStart()
                    except Exception as e: print(f"{plug} has failed to run.", e)
        
        else: pass

def GenenerateTTS_UsingAPI(TTSservice=None, VoiceSelection=None, Region=None, APIkey=None, OutputFolder=None, InputTEXT=None, Test=False):
    try:
        if Test is True:
            if OutputFolder is None or OutputFolder == "": TTSoutput = "TestTTS"
            else: TTSoutput = f"{OutputFolder}/TestTTS"
        else:
            if OutputFolder is None or OutputFolder == "": TTSoutput = "GeneratedTTS"
            else: TTSoutput = f"{OutputFolder}/GeneratedTTS"

        if "11labs" in TTSservice:
            API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
            headers = {
                "xi-api-key": APIkey,
                "Content-Type": "application/json"
            }
            payload = {
                "text": InputTEXT,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            response = requests.post(f"{API_URL}/{VoiceSelection}", json=payload, headers=headers)
            if response.status_code == 200:
                with open(f"{TTSoutput}.mp3", "wb") as file:
                    file.write(response.content)
                print(f"MP3 file generated successfully: {TTSoutput}.mp3")
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")

        elif "IBMwatson" in TTSservice:
            pass

        elif "AmazonPolly" in TTSservice:
            pass

        else:
            raise Exception("Invalid TTS service selection!")
        
        return 0
    except Exception as e:
        return f"Failure: {e}"

def GetAlertLevelColor(ConfigData, ZCZC=None):
    colEvtlist = {
        "AVA": 1,
        "CFA": 1,
        "FFA": 1,
        "FLA": 1,
        "HUA": 1,
        "HWA": 1,
        "SSA": 1,
        "SVA": 1,
        "TOA": 1,
        "TRA": 1,
        "TSA": 1,
        "WSA": 1,
        "DBA": 1,
        "EVA": 1,
        "WFA": 1,
        "AVW": 0,
        "BLU": 0,
        "BZW": 0,
        "CDW": 0,
        "CEM": 0,
        "CFW": 0,
        "DSW": 0,
        "EAN": 0,
        "EQW": 0,
        "EVI": 0,
        "EWW": 0,
        "FFW": 0,
        "FLW": 0,
        "FRW": 0,
        "FSW": 0,
        "FZW": 0,
        "HMW": 0,
        "HUW": 0,
        "HWW": 0,
        "LEW": 0,
        "NUW": 0,
        "RHW": 0,
        "SMW": 0,
        "SPW": 0,
        "SQW": 0,
        "SSW": 0,
        "SVR": 0,
        "TOR": 0,
        "TRW": 0,
        "TSW": 0,
        "VOW": 0,
        "WSW": 0,
        "BHW": 0,
        "BWW": 0,
        "CHW": 0,
        "CWW": 0,
        "DBW": 0,
        "DEW": 0,
        "FCW": 0,
        "IBW": 0,
        "IFW": 0,
        "LSW": 0,
        "WFW": 0,
        "MEP": 0
    }

    if ZCZC is not None:
        try:
            ZCZC = ZCZC.split("-")
            evnt = ZCZC[2]

            if evnt in colEvtlist:
                if colEvtlist[evnt] == 0: embed_color = ConfigData["CGENcolor_warning"]
                elif colEvtlist[evnt] == 1: embed_color = ConfigData["CGENcolor_watch"]
            else:
                embed_color = ConfigData["CGENcolor_advisory"]
        except:
            embed_color = ConfigData["CGENcolor_warning"]
    else:
        embed_color = ConfigData["CGENcolor_warning"]

    return embed_color

class Capture:
    def __init__(self, OutputFolder, TCP, name):
        # domain, port = url.split(':')
        self.NAAD, self.PORT = TCP.split(':')
        self.OutputFolder = OutputFolder
        self.nom = name

    def receive(self, host, port, buffer, delimiter):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, int(port)))
                s.settimeout(100)
                UpdateStatus(self.nom, f"Connected to {host}")
                print(f"[TCP Capture]: Connected to {host}")
                data_received = ""
                try:
                    while True:
                        chunk = str(s.recv(buffer), encoding='utf-8', errors='ignore')
                        data_received += chunk
                        if delimiter in chunk:
                            CapturedSent = re.search(r'<sent>\s*(.*?)\s*</sent>', data_received, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                            CapturedIdent = re.search(r'<identifier>\s*(.*?)\s*</identifier>', data_received, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                            NAADsFilename = f"{CapturedSent}I{CapturedIdent}.xml"
                            with open(f"{self.OutputFolder}/{NAADsFilename}", 'w', encoding='utf-8') as file: file.write(data_received)
                            print(f"[TCP Capture]: I captured an XML, and saved it to: {self.OutputFolder}/{NAADsFilename} | From: {host}")
                            data_received = ""
                except socket.timeout: print(f"[TCP Capture]: Connection timed out for {host}"); return False
            except Exception as e: print(f"[TCP Capture]: Something broke when connecting to {host}: {e}"); return False
            except: print("[TCP Capture]: General exception occurred!"); return False

    def start(self):
        while True:
            NAAD = self.receive(self.NAAD, self.PORT, 1024, "</alert>")
            if NAAD is False:
                UpdateStatus(self.nom, f"TCP connection to {self.NAAD} failure")
                time.sleep(30)

class Check:
    def __init__(self):
        pass

    def Config(InfoX, ConfigData, Status, MsgType, Severity, Urgency, BroadcastImmediately):
        if ConfigData[f"status{Status}"] is False: return False
        if "Yes" in str(BroadcastImmediately): Final = True
        else:
            try:
                var1 = ConfigData[f"severity{Severity}"]
                var2 = ConfigData[f"urgency{Urgency}"]
                var3 = ConfigData[f"messagetype{MsgType}"]
                if var1 is True and var2 is True and var3 is True: Final = True
                else: Final = False
            except: Final = False
        if Final is True:
            if len(ConfigData['AllowedLocations_Geocodes']) == 0: pass
            else:
                try:
                    GeocodeList = re.findall(r'<geocode>\s*<valueName>profile:CAP-CP:Location:0.3</valueName>\s*<value>\s*(.*?)\s*</value>', InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    for i in GeocodeList:
                        if i[:2] in ConfigData['AllowedLocations_Geocodes']: return True
                        if i[:3] in ConfigData['AllowedLocations_Geocodes']: return True
                        if i[:4] in ConfigData['AllowedLocations_Geocodes']: return True
                        if i in ConfigData['AllowedLocations_Geocodes']: return True
                except: return True
                return False
        return Final
        
    def MatchCLC(ConfigData, SAMEheader):
        if len(ConfigData['AllowedLocations_CLC']) == 0: return True
        else:
            for i in EAS2Text(SAMEheader).FIPS:
                # Partial county wildcard filter
                partial = "*" + i[1:]
                if partial[:2] in ConfigData['AllowedLocations_CLC']: return True
                if partial[:3] in ConfigData['AllowedLocations_CLC']: return True
                if partial[:4] in ConfigData['AllowedLocations_CLC']: return True
                if partial in ConfigData['AllowedLocations_CLC']: return True

                if i[:2] in ConfigData['AllowedLocations_CLC']: return True
                if i[:3] in ConfigData['AllowedLocations_CLC']: return True
                if i[:4] in ConfigData['AllowedLocations_CLC']: return True
                if i in ConfigData['AllowedLocations_CLC']: return True
            return False

    def DuplicateSAME(GeneratedHeader):
        try:
            with open("SameHistory.txt", "r") as f:
                content = f.read()
                if GeneratedHeader in content: return True
        except:
            with open("SameHistory.txt", "a") as f: f.write(f"ZXZX-STARTER-\n")
        with open("SameHistory.txt", "a") as f: f.write(f"{GeneratedHeader}\n")
        return False

    def CheckEventCodeSAME(ConfigData, GeneratedHeader):
        EVENT = EAS2Text(GeneratedHeader).evnt
        EVENT = str(EVENT)
        if "EAN" in EVENT or "NIC" in EVENT or "NPT" in EVENT or "RMT" in EVENT or "RWT" in EVENT: return True
        
        if len(ConfigData['CAP_SAMEevent_Blocklist']) == 0: return True
        else:
            if EVENT in ConfigData['CAP_SAMEevent_Blocklist']: return False
        
        if len(ConfigData['CAP_SAMEevent_Whitelist']) == 0: return True
        else:
            if EVENT in ConfigData['CAP_SAMEevent_Whitelist']: return True
            else: return False

    def Heartbeat(References, QueueFolder, HistoryFolder):
        print("Downloading alerts from received heartbeat...")
        RefList = References.split(" ")
        for i in RefList:
            j = re.sub(r'^.*?,', '', i)
            j = j.split(",")
            sent = j[1]
            sentDT = sent.split("T", 1)[0]
            sent = sent.replace("-","_").replace("+", "p").replace(":","_")
            identifier = j[0]
            identifier = identifier.replace("-","_").replace("+", "p").replace(":","_")
            Dom1 = 'capcp1.naad-adna.pelmorex.com'
            Dom2 = 'capcp2.naad-adna.pelmorex.com'
            Output = f"{QueueFolder}/{sent}I{identifier}.xml"
            if f"{sent}I{identifier}.xml" in os.listdir(f"{HistoryFolder}"):
                print("Heartbeat, no download: Files matched.")
            else:
                print( f"Downloading: {sent}I{identifier}.xml...")
                req1 = Request(url = f'http://{Dom1}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                req2 = Request(url = f'http://{Dom2}/{sentDT}/{sent}I{identifier}.xml', headers={'User-Agent': 'Mozilla/5.0'})
                try: xml = urlopen(req1).read()
                except:
                    try: xml = urlopen(req2).read()
                    except: pass
                try:
                    with open(Output, "wb") as f: f.write(xml)
                except: print("Heartbeat, download aborted: a general exception occurred, it could be that the URLs are temporarily unavailable.")

    def watchNotify(ListenFolder, HistoryFolder):
        print(f"Waiting for an alert...")
        while True:
            ExitTicket = False
            QueueList = os.listdir(f"{ListenFolder}")
            for file in QueueList:
                with open(f"{ListenFolder}/{file}", "r", encoding='UTF-8') as f: RelayXML = f.read()
                AlertListXML = re.findall(r'<alert\s*(.*?)\s*</alert>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)

                if len(AlertListXML) > 1:
                    print("WHY THE F*** IS THERE 2 ALERT ELEMENTS IN A SINGLE XML FILE?!!?")
                    AlertCount = 0
                    for AlertXML in AlertListXML:
                        AlertCount = AlertCount + 1
                        print("Alert", AlertCount)
                        Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', AlertXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                        Ident = re.search(r'<identifier>\s*(.*?)\s*</identifier>', AlertXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                        NAADsFilename = f"{Sent}I{Ident}.xml"
                        AlertXML = f"<alert {AlertXML}</alert>"
                        with open(f"{ListenFolder}/{NAADsFilename}", 'w', encoding='utf-8') as f: f.write(AlertXML)
                    os.remove(f"{ListenFolder}/{file}")
                elif file in os.listdir(f"{HistoryFolder}"):
                    print("No relay: watch folder files matched.")
                    os.remove(f"{ListenFolder}/{file}")
                    ExitTicket = False
                else:
                    ExitTicket = True
                    break
            if ExitTicket is True: break
            else: time.sleep(1) # Wait a little bit between looking for new files
        return file

class Generate:
    def __init__(self, InfoXML, SentDate, MsgType, SAMEcallsign):
        self.InfoX = InfoXML
        self.MsgType = MsgType
        self.Sent = SentDate
        self.Callsign = SAMEcallsign
        self.CapCatToSameOrg = {
            "Met": "WXR",
            "Admin": "EAS",
            "Other": "CIV",
        }
        self.CapEventToSameEvent = {
            "911Service": "TOE",
            "accident": "CDW",
            "admin":"ADR",
            "aircraftCras":"LAE",
            "airportClose":"ADR",
            "airQuality":"SPS",
            "airspaceClos":"ADR",
            "amber":"CAE",
            "ambulance":"LAE",
            "animalDang":"CDW",
            "animalDiseas":"CDW",
            "animalFeed":"CEM",
            "animalHealth":"CEM",
            "arcticOut":"SVS",
            "avalanche":"AVW",
            "aviation":"LAE",
            "biological":"BHW",
            "blizzard":"BZW",
            "bloodSupply":"LAE",
            "blowingSnow":"WSW",
            "bridgeClose":"LAE",
            "cable":"ADR",
            "chemical":"CHW",
            "civil":"CEM",
            "civilEmerg":"CEM",
            "civilEvent":"CEM",
            "cold":"SVS",
            "coldWave":"SVS",
            "crime":"CDW",
            "damBreach":"DBW",
            "damOverflow":"DBW",
            "dangerPerson":"CDW",
            "diesel":"LAE",
            "drinkingWate":"CWW",
            "dustStorm":"DSW",
            "earthquake":"EQW",
            "electric":"POS",
            "emergFacil":"CEM",
            "emergSupport":"CEM",
            "explosive":"HMW",
            "facility":"CEM",
            "fallObject":"HMW",
            "fire":"FRW",
            "flashFlood":"FFW",
            "flashFreeze":"FSW",
            "flood":"FLW",
            "fog":"SPS",
            "foodSupply":"LAE",
            "forestFire":"WFW",
            "freezeDrzl":"WSW",
            "freezeRain":"WSW",
            "freezngSpray":"WSW",
            "frost":"SPS",
            "galeWind":"HWW",
            "gasoline":"LAE",
            "geophyiscal":"CEM",
            "hazmat":"BHW",
            "health":"BHW",
            "heat":"SVS",
            "heatHumidity":"SVS",
            "heatingOil":"LAE",
            "heatWave":"SVS",
            "highWater":"SVS",
            "homeCrime":"CEM",
            "hospital":"LAE",
            "hurricane":"HUW",
            "hurricFrcWnd":"HUW",
            "ice":"SPS",
            "iceberg":"IBW",
            "icePressure":"SPS",
            "industCrime":"CEM",
            "industryFire":"IFW",
            "infectious":"DEW",
            "internet":"ADR",
            "lahar":"VOW",
            "landslide":"LSW",
            "lavaFlow":"VOW",
            "magnetStorm":"CDW",
            "marine":"SMW",
            "marineSecure":"SMW",
            "meteor":"CDW",
            "missingPer":"MEP",
            "missingVPer":"MEP",
            "naturalGas":"LAE",
            "nautical":"ADR",
            "notam":"ADR",
            "other":"CEM",
            "overflood":"FLW",
            "plant":"LAE",
            "plantInfect":"LAE",
            "product":"LAE",
            "publicServic":"LAE",
            "pyroclasFlow":"VOW",
            "pyroclaSurge":"VOW",
            "radiological":"RHW",
            "railway":"LAE",
            "rainfall":"SPS",
            "rdCondition":"LAE",
            "reminder":"CEM",
            "rescue":"CEM",
            "retailCrime":"CEM",
            "road":"LAE",
            "roadClose":"ADR",
            "roadDelay":"ADR",
            "roadUsage":"ADR",
            "rpdCloseLead":"ADR",
            "satellite":"ADR",
            "schoolBus":"ADR",
            "schoolClose":"ADR",
            "schoolLock":"CDW",
            "sewer":"LAE",
            "silver":"CEM",
            "snowfall":"WSW",
            "snowSquall":"WSW",
            "spclIce":"SPS",
            "spclMarine":"SMW",
            "squall":"SMW",
            "storm":"SVS",
            "stormFrcWnd":"SVS",
            "stormSurge":"SSW",
            "strongWind":"HWW",
            "telephone":"LAE",
            "temperature":"SPS",
            "terrorism":"CDW",
            "testMessage":"DMO",
            "thunderstorm":"SVR",
            "tornado":"TOR",
            "traffic":"ADR",
            "train":"ADR",
            "transit":"ADR",
            "tropStorm":"TRW",
            "tsunami":"TSW",
            "urbanFire":"FRW",
            "utility":"ADR",
            "vehicleCrime":"CEM",
            "volcanicAsh":"VOW",
            "volcano":"VOW",
            "volunteer":"ADR",
            "waste":"ADR",
            "water":"ADR",
            "waterspout":"SMW",
            "weather":"SPS",
            "wildFire":"FRW",
            "wind":"HWW",
            "windchill":"SPS",
            "winterStorm":"WSW"
        }

    def GeoToCLC(self):
        GeocodeList = re.findall(r'<geocode>\s*<valueName>profile:CAP-CP:Location:0.3</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        filepath = './GeoToCLC.csv'
        SameDict = {}
        with open(filepath) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                line = line.replace('\n', '')
                SAMESPLIT = line.split(",")
                SameDict[SAMESPLIT[0]] = SAMESPLIT[1]
                line = fp.readline()
                cnt += 1

        CLC = ""
        for i in GeocodeList:
            try:
                C = SameDict[i]
            except:
                C = ""
            if C == "":
                pass
            else:
                CLC = f"{CLC}" + f"{C},"
        
        # Aaron i know you're kinda gonna cringe at this, but we need it
        CLC = "".join(CLC.rsplit(",",1))
        CLC = CLC.split(",")
        CLC = "-".join(CLC)
        CLC = CLC.split("-")
        CLC = list(set(CLC))
        CLC = "-".join(CLC)
        return CLC
    
    def SAMEheader(self):
        Callsign = self.Callsign
        if len(Callsign) > 8: Callsign = "QUANTUM0"; print("Your callsign is too long!")
        elif len(Callsign) < 8: Callsign = "QUANTUM0"; print("Your callsign is too short!")
        elif "-" in Callsign: Callsign = "QUANTUM0"; print("Your callsign contains an invalid symbol!")
        
        try: ORG = re.search(r'<parameter>\s*<valueName>EAS-ORG</valueName>\s*<value>\s*(.*?)\s*</value>\s*</parameter>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        except:
            try: ORG = self.CapCatToSameOrg[re.search(r'<category>\s*(.*?)\s*</category>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)]
            except: ORG = "CIV"
        
        try:
            EVE = re.search(r'<eventCode>\s*<valueName>SAME</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            if EVE is None or EVE == "": EVE = "CEM"
        except:
            try:
                EVE = re.search(r'<eventCode>\s*<valueName>profile:CAP-CP:Event:0.4</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                EVE = self.CapEventToSameEvent[EVE]
            except: EVE = "CEM"

        try: Effective = datetime.fromisoformat(datetime.fromisoformat(re.search(r'<effective>\s*(.*?)\s*</effective>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)).astimezone(timezone.utc).isoformat()).strftime("%j%H%M")
        except: Effective = datetime.now().astimezone(timezone.utc).strftime("%j%H%M")
        
        try:
            NowTime = datetime.now(timezone.utc)
            NowTime = NowTime.replace(microsecond=0).isoformat()
            NowTime = NowTime[:-6]
            NowTime = datetime.fromisoformat(NowTime)
            ExpireTime = re.search(r'<expires>\s*(.*?)\s*</expires>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            ExpireTime = datetime.fromisoformat(ExpireTime).astimezone(timezone.utc)
            ExpireTime = ExpireTime.isoformat()
            ExpireTime = ExpireTime[:-6]
            ExpireTime = datetime.fromisoformat(ExpireTime)
            Purge = ExpireTime - NowTime
            hours, remainder = divmod(Purge.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            Purge = "{:02}{:02}".format(hours, minutes)
        except: Purge = "0600"

        if "layer:EC-MSC-SMC:1.1:Newly_Active_Areas" in str(self.InfoX):
            try: CLC = re.search(r'<valueName>layer:EC-MSC-SMC:1.1:Newly_Active_Areas</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace(',','-')
            except: CLC = self.GeoToCLC()
        else:
            CLC = re.findall(r'<geocode>\s*<valueName>SAME</valueName>\s*<value>\s*(.*?)\s*</value>\s*</geocode>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            CLC = '-'.join(CLC)
            if str(CLC) == "": CLC = self.GeoToCLC()
        if CLC == "": CLC = "000000"

        GeneratedHeader = f"ZCZC-{ORG}-{EVE}-{CLC}+{Purge}-{Effective}-{Callsign}-"
        return GeneratedHeader
    
    def LastWordThing(self, headline):
        target_words = {"test", "watch", "warning", "alert", "emergency"}
        words = headline.split()
        if words:
            last_word = words[-1].lower()
            return last_word in target_words
        return False
        
    def BroadcastText(self, lang):
        try: BroadcastText = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Text</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n',' ').replace('  ',' ')
        except:
            if lang == "fr": issue = "émis"; update = "mis à jour"; cancel = "annulé"
            else: issue = "issued"; update = "updated"; cancel = "cancelled"
            
            if self.MsgType == "Alert": MsgPrefix = issue
            elif self.MsgType == "Update": MsgPrefix = update
            elif self.MsgType == "Cancel": MsgPrefix = cancel
            else: MsgPrefix = "issued"
            
            Sent = datetime.fromisoformat(datetime.fromisoformat(self.Sent).astimezone(timezone.utc).isoformat())
            Sent = Sent.astimezone()
            if lang == "fr": Sent = Sent.strftime("%Hh%M.")
            else: Sent = Sent.strftime("%H:%M %Z, %B %d, %Y.")
            
            try: EventType = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Name</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            except:
                if lang == "fr":
                    EventType = re.search(r'<event>\s*(.*?)\s*</event>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    EventType = f"alerte {EventType}"
                else:
                    EventType = re.search(r'<event>\s*(.*?)\s*</event>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    if self.LastWordThing(EventType) is True: pass
                    else: EventType = f"{EventType} alert"
            
            try:
                Coverage = re.search(r'<valueName>layer:EC-MSC-SMC:1.0:Alert_Coverage</valueName>\s*<value>\s*(.*?)\s*</value>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                if lang == "fr": Coverage = f"en {Coverage} pour:"
                else: Coverage = f"in {Coverage} for:"
            except:
                if lang == "fr": Coverage = "pour:"
                else: Coverage = "for:" 
            
            AreaDesc = re.findall(r'<areaDesc>\s*(.*?)\s*</areaDesc>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            AreaDesc = ', '.join(AreaDesc) + '.'
            try: SenderName = re.search(r'<senderName>\s*(.*?)\s*</senderName>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            except: SenderName = "an alert issuer"
            try: Description = re.search(r'<description>\s*(.*?)\s*</description>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n', ' ')
            except: Description = ""
            try: Instruction = re.search(r'<instruction>\s*(.*?)\s*</instruction>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace('\n', ' ')
            except: Instruction = ""
            
            if lang == "fr": BroadcastText = f"À {Sent} {SenderName} a {MsgPrefix} une {EventType} {Coverage} {AreaDesc} {Description} {Instruction}".replace('###','').replace('  ',' ')
            else: BroadcastText = f"At {Sent} {SenderName} has {MsgPrefix} a {EventType} {Coverage} {AreaDesc} {Description} {Instruction}".replace('###','').replace('  ',' ')
        
        return BroadcastText

    def GetAudio(self, AudioLink, Output, DecodeType):
        if DecodeType == 1:
            print("Decoding audio from BASE64...")
            with open(Output, "wb") as fh: fh.write(base64.decodebytes(AudioLink))
        elif DecodeType == 0:
            print("Downloading audio...")
            r = requests.get(AudioLink)
            with open(Output, 'wb') as f: f.write(r.content)

    def ConvAudioFormat(self, inputAudio, outputAudio):
        result = subprocess.run(["ffmpeg", "-y", "-i", inputAudio, outputAudio], capture_output=True, text=True)
        if result.returncode == 0: print(f"[RELAY/GENERATE]: {inputAudio} --> {outputAudio} ... Conversion successful!")
        else: print(f"[RELAY/GENERATE]: {inputAudio} --> {outputAudio} ... Conversion failed: {result.stderr}")

    def LoudenAudio(self, inputAudio, outputAudio):
        result = subprocess.run(["ffmpeg", "-y", "-i", inputAudio, "-filter:a", "volume=2.5", outputAudio], capture_output=True, text=True)
        if result.returncode == 0: print(f"[RELAY/GENERATE]: Filter loudening success.")
        else: print(f"[RELAY/GENERATE]: Filter loudening failure: {result.stderr}")

    def TrimAudio(self, input_file, output_file, max_duration_ms=120000):
        # For broadcast audio
        try:
            audio = AudioSegment.from_file(input_file)
            duration_ms = len(audio)
            if duration_ms > max_duration_ms:
                trimmed_audio = audio[:max_duration_ms]
                trimmed_audio.export(output_file, format="wav")
                print(f"Broadcast Audio trimmed to {max_duration_ms / 1000} seconds.")
                shutil.move(output_file, input_file)
            else: pass
        except: print("Failed to trim broadcast audio!")

    def Audio(self, BroadcastText, lang, ConfigData):
        try:
            resources = re.findall(r'<resource>\s*(.*?)\s*</resource>', self.InfoX, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            if "audio/mpeg" in str(resources): pass
            elif "audio/x-ms-wma" in str(resources): pass
            elif "audio/wave" in str(resources): pass
            elif "audio/wav" in str(resources): pass
            elif "audio/x-ipaws-audio-mp3" in str(resources): pass
            else: raise Exception("Generate TTS instead")
            for BroadcastAudioResource in resources:
                if "<derefUri>" in BroadcastAudioResource:
                    AudioLink = bytes(re.search(r'<derefUri>\s*(.*?)\s*</derefUri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1), 'utf-8')
                    AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Decode = 1
                else:
                    AudioLink = re.search(r'<uri>\s*(.*?)\s*</uri>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudioResource, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Decode = 0
                
                if AudioType == "audio/mpeg":
                    self.GetAudio(AudioLink,"Audio/tmp/PreAudio.mp3",Decode)
                    self.ConvAudioFormat("Audio/tmp/PreAudio.mp3", "Audio/tmp/PreAudio.wav")
                    os.remove("Audio/tmp/PreAudio.mp3")
                    self.LoudenAudio("Audio/tmp/PreAudio.wav", "Audio/audio.wav")
                    os.remove("Audio/tmp/PreAudio.wav")

                elif AudioType == "audio/x-ms-wma":
                    self.GetAudio(AudioLink,"Audio/tmp/PreAudio.wma",Decode)
                    self.ConvAudioFormat("Audio/tmp/PreAudio.wma", "Audio/tmp/PreAudio.wav")
                    os.remove("Audio/tmp/PreAudio.wma")
                    self.LoudenAudio("Audio/tmp/PreAudio.wav", "Audio/audio.wav")
                    os.remove("Audio/tmp/PreAudio.wav")

                elif AudioType == "audio/wave":
                    self.GetAudio(AudioLink,"Audio/tmp/PreAudio.wav",Decode)
                    self.LoudenAudio("Audio/tmp/PreAudio.wav", "Audio/audio.wav")
                    os.remove("Audio/tmp/PreAudio.wav")

                elif AudioType == "audio/wav":
                    self.GetAudio(AudioLink,"Audio/tmp/PreAudio.wav",Decode)
                    self.LoudenAudio("Audio/tmp/PreAudio.wav", "Audio/audio.wav")
                    os.remove("Audio/tmp/PreAudio.wav")

                elif AudioType == "audio/x-ipaws-audio-mp3":
                    self.GetAudio(AudioLink,"Audio/tmp/PreAudio.mp3",Decode)
                    self.ConvAudioFormat("Audio/tmp/PreAudio.mp3", "Audio/tmp/PreAudio.wav")
                    os.remove("Audio/tmp/PreAudio.mp3")
                    self.LoudenAudio("Audio/tmp/PreAudio.wav", "Audio/audio.wav")
                    os.remove("Audio/tmp/PreAudio.wav")
                else: pass
        except:
            print("Generating TTS audio...")
            try: pythoncom.CoInitialize()
            except: pass
            
            try: os.remove("Audio/audio.wav")
            except: pass

            try:
                if ConfigData["TTS_Service"] == "pyttsx3":
                    engine = pyttsx3.init()
                    if ConfigData["UseDefaultVoices"] is False:
                        if lang == "fr": ActiveVoice = ConfigData["VoiceFR"]
                        else: ActiveVoice = ConfigData["VoiceEN"]
                        voices = engine.getProperty('voices')
                        ActiveVoice = next((voice for voice in voices if voice.name == ActiveVoice), None)
                        if ActiveVoice: engine.setProperty('voice', ActiveVoice.id)
                    engine.save_to_file(str(BroadcastText), f"Audio/audio.wav")
                    engine.runAndWait()
                elif ConfigData["TTS_Service"] == "flite":
                    BroadcastText = BroadcastText.replace("\n", " ")
                    if ConfigData["UseDefaultVoices"] is False:
                        if lang == "fr": ActiveVoice = ConfigData["FliteVoice_FR"]
                        else: ActiveVoice = ConfigData["FliteVoice_EN"]
                        subprocess.run(["flite", "-t", BroadcastText, "-voice", ActiveVoice, "-o", f"Audio/audio.wav"], capture_output=True, text=True)
                    else: subprocess.run(["flite", "-t", BroadcastText, "-o", f"Audio/audio.wav"], capture_output=True, text=True)
                else:
                    BroadcastText = BroadcastText.replace("\n", " ")
                    if lang == "fr": ActiveVoice = ConfigData["APIvoice_FR"]
                    else: ActiveVoice = ConfigData["APIvoice_EN"]
                    GenenerateTTS_UsingAPI(ConfigData["TTS_Service"], ActiveVoice, ConfigData["APIvoice_Region"], ConfigData["APIvoice_Key"], "Audio/tmp", BroadcastText)
                    self.ConvAudioFormat("Audio/tmp/GeneratedTTS.mp3", "Audio/PreAudio.wav")
            except:
                print("TTS generation failure!")

        if ConfigData['Force120'] is True: self.TrimAudio("./Audio/audio.wav", "./Audio/tmp/trimmedAudio.wav")
        
    def AudioSAME(self, GeneratedHeader):
        print("Generating SAME header...")
        SAMEheader = EASGen.genEAS(header=GeneratedHeader, attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("./Audio/same.wav", SAMEheader)
        EASGen.export_wav("./Audio/eom.wav", SAMEeom)

class Playout:
    def __init__(self, InputConfig, CODE):
        self.CODE = CODE
        self.InputConfig = InputConfig

    def play(self, InputFile):
        UseSpecDevice = self.InputConfig['UseSpecified_AudioOutput']
        SpecDevice = self.InputConfig['Specified_AudioOutput']
        time.sleep(0.5)
        if UseSpecDevice is True:
            sd.default.reset()
            sd.default.device = SpecDevice
            sampling_rate, audio_data = wavfile.read(InputFile)
            sd.play(audio_data, samplerate=sampling_rate)
            sd.wait()
        else:
            sampling_rate, audio_data = wavfile.read(InputFile)
            sd.play(audio_data, samplerate=sampling_rate)
            sd.wait()
        
    def AlertIntro(self):
        UpdateStatus("Relay", f"Transmitting alert.")    
        if os.path.exists("./Audio/pre.wav"):
            try: self.play("./Audio/pre.wav")
            except: pass
    
    def AlertSAME(self):
        try: self.play("./Audio/same.wav")
        except: pass

    def AlertAttn(self):
        try:
            if "CANADA" in str(self.CODE): self.play(f"./Audio/AttnCAN.wav")
            elif "USA" in str(self.CODE): self.play(f"./Audio/AttnEBS.wav")
            else: self.play(f"./Audio/{self.InputConfig['AttentionTone']}")
        except: print("Attention tone error! (Check attention tone audio file)")

    def AlertAudio(self):
        try: self.play("./Audio/audio.wav")
        except: print("Error playing alert audio.")

    def AlertEOM(self):
        try: self.play("./Audio/eom.wav")
        except: pass

    def AlertOutro(self):
        if os.path.exists("./Audio/post.wav"):
            try: self.play("./Audio/post.wav")
            except: pass

def DecodeIntMonitor(inputXML, ConfigData):
    try:
        SourceHEADER = re.search(r'<SAME>\s*(.*?)\s*</SAME>', inputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        BroadcastAudio = re.search(r'<BroadcastAudio>\s*(.*?)\s*</BroadcastAudio>', inputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
        
        if len(ConfigData['SAMEmonitor-FIPS-filter']) == 0: pass
        else:
            try:
                SourceFIPS = EAS2Text(SourceHEADER).FIPS
                FIPSmatch = False
                for i in SourceFIPS:
                    # Partial county wildcard filter
                    partial = "*" + i[1:]
                    if partial[:2] in ConfigData['AllowedLocations_CLC']: return True
                    if partial[:3] in ConfigData['AllowedLocations_CLC']: return True
                    if partial[:4] in ConfigData['AllowedLocations_CLC']: return True
                    if partial in ConfigData['AllowedLocations_CLC']: return True

                    if i[:2] in ConfigData['SAMEmonitor-FIPS-filter']: FIPSmatch = True
                    if i[:3] in ConfigData['SAMEmonitor-FIPS-filter']: FIPSmatch = True
                    if i[:4] in ConfigData['SAMEmonitor-FIPS-filter']: FIPSmatch = True
                    if i in ConfigData['SAMEmonitor-FIPS-filter']: FIPSmatch = True
                if FIPSmatch is False: return False
            except: return False

        if len(ConfigData['SAMEmonitor-EVENT-filter']) == 0: pass
        else:
            try:
                EVENT = EAS2Text(SourceHEADER).evnt
                if "EAN" in EVENT or "NIC" in EVENT or "NPT" in EVENT or "RMT" in EVENT or "RWT" in EVENT: pass
                elif EVENT in ConfigData: pass
                else: return False
            except: return False

        if len(ConfigData['SAMEmonitor-ORIGINATOR-filter']) == 0: pass
        else:
            try:
                if EAS2Text(SourceHEADER).org in ConfigData['SAMEmonitor-ORIGINATOR-filter']: pass
                else: return False
            except: return False

        Callsign = ConfigData['SAME_callsign']
        if len(Callsign) > 8: Callsign = "QUANTUM0"; print("Your callsign is too long!")
        elif len(Callsign) < 8: Callsign = "QUANTUM0"; print("Your callsign is too short!")
        elif "-" in Callsign: Callsign = "QUANTUM0"; print("Your callsign contains an invalid symbol!")
        ZCZC = SourceHEADER.split("-")
        ZCZClen = len(ZCZC) - 2
        ZCZC[ZCZClen] = Callsign
        ZCZC = '-'.join(ZCZC)
        print("Generating SAME header...")
        SAMEheader = EASGen.genEAS(header=ZCZC, attentionTone=False, endOfMessage=False)
        SAMEeom = EASGen.genEAS(header="NNNN", attentionTone=False, endOfMessage=False)
        EASGen.export_wav("./Audio/same.wav", SAMEheader)
        EASGen.export_wav("./Audio/eom.wav", SAMEeom)
        
        try:
            oof = EAS2Text(ZCZC)
            BroadcastText = oof.EASText 
        except: BroadcastText = "This is an emergency alert message."
        
        try:
            AudioLink = bytes(re.search(r'<AudioBASE64>\s*(.*?)\s*</AudioBASE64>', BroadcastAudio, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1), 'utf-8')
            #AudioType = re.search(r'<mimeType>\s*(.*?)\s*</mimeType>', BroadcastAudio, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
            with open("PreAudio.wav", "wb") as fh: fh.write(base64.decodebytes(AudioLink))
            result = subprocess.run(["ffmpeg", "-y", "-i", "PreAudio.wav", "-filter:a", "volume=2.5", "Audio/audio.wav"], capture_output=True, text=True)
            if result.returncode == 0: print(f"[RELAY/GENERATE]: Filter loudening success.")
            else: print(f"[RELAY/GENERATE]: Filter loudening failure: {result.stderr}")
            os.remove("PreAudio.wav")
        except:
            print("Generating TTS audio...")
            try: pythoncom.CoInitialize()
            except: pass
            engine = pyttsx3.init()
            if ConfigData["UseDefaultVoices"] is False:
                ActiveVoice = ConfigData["VoiceEN"]
                voices = engine.getProperty('voices')
                ActiveVoice = next((voice for voice in voices if voice.name == ActiveVoice), None)
                if ActiveVoice: engine.setProperty('voice', ActiveVoice.id)
            engine.save_to_file(str(BroadcastText), f"Audio/audio.wav")
            engine.runAndWait()
        return [ZCZC, BroadcastText]
    except: return "exception"

def GetXML_CODE(inputXML):
    try:
        CODE = re.findall(r'<code>\s*(.*?)\s*</code>', inputXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if "profile:CAP-CP:0.4" in str(CODE): CODE = "CANADA"
        elif "IPAWSv1.0" in str(CODE): CODE = "USA"
        else: CODE = False
        return CODE
    except:
        return False

stopPassthrough = threading.Event()

def audio_callback(indata, outdata, frames, time, status):
    if status: print(status, file=sys.stderr)
    outdata[:] = indata

def passthrough(ConfigData):
    sd.default.reset()
    Nope = False
    input_device_name = ConfigData['Passthrough_AudioInput']
    output_device_name = ConfigData['Specified_AudioOutput']

    if ConfigData['UseSpecified_Passthrough_AudioInput'] is True and ConfigData['UseSpecified_AudioOutput'] is True: sd.default.device = (input_device_name, output_device_name)
    elif ConfigData['UseSpecified_Passthrough_AudioInput'] is True and ConfigData['UseSpecified_AudioOutput'] is False: Nope = True
    elif ConfigData['UseSpecified_Passthrough_AudioInput'] is False and ConfigData['UseSpecified_AudioOutput'] is True: Nope = True
    elif ConfigData['UseSpecified_Passthrough_AudioInput'] is False and ConfigData['UseSpecified_AudioOutput'] is False: pass
    else: pass

    samplerate = 48000  # Sample rate in Hz
    blocksize = 1024     # Number of frames per block
    
    if Nope is True:
        print("In order to use pass-through, you can only have both input and output selected, or both input and outputs at default.")
    else:
        with sd.Stream(
            samplerate=samplerate,
            blocksize=blocksize,
            channels=2,  # Stereo
            callback=audio_callback
        ) as stream:
            while not stopPassthrough.is_set(): stopPassthrough.wait(0.1)  # Wait for 100 ms
            print("Stopping pass-through.")

def Relay():
    PassthroughThread = None
    while True:
        with open("config.json", "r") as JCfile: config = JCfile.read()
        ConfigData = json.loads(config)
        
        if ConfigData['EnablePassThru'] is True:
            if PassthroughThread is None or not PassthroughThread.is_alive():
                stopPassthrough.clear()
                PassthroughThread = threading.Thread(target=passthrough, args=(ConfigData,))
                PassthroughThread.start()
    
        Clear()
        print(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        UpdateStatus("Relay", f"Waiting for alert...")
        ResultFileName = Check.watchNotify("./XMLqueue", "./XMLhistory")
        print(f"Captured: {ResultFileName}")
        
        try:
            shutil.move(f"./XMLqueue/{ResultFileName}", f"./relay.xml")
            file = open("relay.xml", "r", encoding='utf-8')
            RelayXML = file.read()
            file.close()

            if "<sender>NAADS-Heartbeat</sender>" in RelayXML:
                print("\n\n...HEARTBEAT DETECTED...")
                References = re.search(r'<references>\s*(.*?)\s*</references>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Check.Heartbeat(References, "XMLqueue", "XMLhistory")

            elif "<InternalMonitor>SAME</InternalMonitor>" in RelayXML:
                UpdateStatus("Relay", f"Alert detected.")
                print("\n\n...NEW ALERT DETECTED - SAME MONITOR...")
                shutil.copy(f"./relay.xml", str(f"./XMLhistory/{ResultFileName}"))
                Callsign = ConfigData['SAME_callsign']
                print(f"Hello {Callsign}")
                Decoded = DecodeIntMonitor(RelayXML, ConfigData)
                if Decoded == "exception": print("No relay: An exception was raised when trying to decode the SAME alert's XML.")
                else:
                    if Decoded is False: print("No relay: No filter match.")
                    else:
                        if Check.DuplicateSAME(Decoded[0]) is True: print("No relay: duplicate SAME header detected from a previous relay."); continue
                        alertColor = GetAlertLevelColor(ConfigData, Decoded[0])
                        Plugins_Run("beforeRelay", Decoded[0], Decoded[1], None)

                        if ConfigData["ProduceImages"] is True: AIOMG.OutputAlertImage(Fallback=True)
                        
                        try:
                            CGEN_Dict = {
                                "color": alertColor,
                                "headline": "EMERGENCY ALERT SYSTEM",
                                "text": Decoded[1],
                                "alertStat": True
                            }
                            #with open("./alert.txt", "w") as f: f.write(Decoded[1])
                            with open("AlertText.json", 'w') as json_file: json.dump(CGEN_Dict, json_file, indent=2)
                        except: pass

                        try:
                            logge = Log(ConfigData)
                            logge.SendLog("Emergency Alert Transmission", Decoded[1], Decoded[0], "TX", alertColor)
                        except: pass

                        PlayAlert = Playout(ConfigData, False)

                        try: 
                            stopPassthrough.set()
                            PassthroughThread.join()
                            print("Pass-through stopped.")
                        except: pass

                        if ConfigData[f'PlayoutNoSAME'] is True:
                            PlayAlert.AlertIntro()
                            PlayAlert.AlertAttn()
                            PlayAlert.AlertAudio()
                            PlayAlert.AlertOutro()
                        else:
                            PlayAlert.AlertIntro()
                            PlayAlert.AlertSAME()
                            PlayAlert.AlertAttn()
                            PlayAlert.AlertAudio()
                            PlayAlert.AlertEOM()
                            PlayAlert.AlertOutro()

                        Plugins_Run("afterRelay", Decoded[0], Decoded[1], None)

                        try:
                            if ConfigData["CGEN_ClearAfterAlert"] is True:
                                CGEN_Dict = {
                                    "color": "000000",
                                    "headline": "Emergency Alert Details",
                                    "text": ""
                                }
                                #with open("./alert.txt", "w") as f: f.write(Decoded[1])
                                with open("AlertText.json", 'w') as json_file: json.dump(CGEN_Dict, json_file, indent=2)
                        except: pass

            else:
                UpdateStatus("Relay", f"Alert detected.")
                print("\n\n...NEW ALERT DETECTED...")
                shutil.copy(f"./relay.xml", str(f"./XMLhistory/{ResultFileName}"))
                Callsign = ConfigData['SAME_callsign']
                print(f"Hello {Callsign}")
                Sent = re.search(r'<sent>\s*(.*?)\s*</sent>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                Status = re.search(r'<status>\s*(.*?)\s*</status>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                MessageType = re.search(r'<msgType>\s*(.*?)\s*</msgType>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                
                if ConfigData['Attn_BasedOnCountry'] is True: CODE = GetXML_CODE(RelayXML)
                else: CODE = False
                PlayAlert = Playout(ConfigData, CODE)

                RelayXML = re.findall(r'<info>\s*(.*?)\s*</info>', RelayXML, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                InfoProc = 0

                AlertIntro_HasBeenPlayed = False
                Alert_Playout = False

                for InfoEN in RelayXML:
                    InfoProc = InfoProc + 1
                    print(f"\n...Processing <info>: {InfoProc}...\n")
                    InfoEN = f"<info>{InfoEN}</info>"

                    try:
                        if "en" in re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1): lang = "en"
                        elif "fr" in re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1): lang = "fr"
                        elif "es" in re.search(r'<language>\s*(.*?)\s*</language>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1): lang = "es"
                        else:
                            print("Language not supported.")
                            continue
                        if ConfigData[f'relay_{lang}'] is False: print("Not relaying:", lang); continue
                    except:
                        print("Language check failed.")
                        continue

                    try:
                        current_time = datetime.now(timezone.utc)
                        Expires = re.search(r'<expires>\s*(.*?)\s*</expires>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                        Expires = datetime.fromisoformat(datetime.fromisoformat(Expires).astimezone(timezone.utc).isoformat())
                        if current_time > Expires:
                            print("Alert expired, will not relay.")
                            continue
                    except: pass

                    Urgency = re.search(r'<urgency>\s*(.*?)\s*</urgency>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    Severity = re.search(r'<severity>\s*(.*?)\s*</severity>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    try: BroadcastImmediately = re.search(r'<valueName>layer:SOREM:1.0:Broadcast_Immediately</valueName>\s*<value>\s*(.*?)\s*</value>', InfoEN, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    except: BroadcastImmediately = "No"

                    if Check.Config(InfoEN, ConfigData, Status, MessageType, Severity, Urgency, BroadcastImmediately) is False: print("No relay: Config filters reject.")
                    else:
                        print("Generating text products...")
                        Gen = Generate(InfoEN, Sent, MessageType, Callsign)
                        GeneratedHeader = Gen.SAMEheader()
                        print("generated header:", GeneratedHeader)
                        BroadcastText = Gen.BroadcastText(lang)
                        if ConfigData[f'PlayoutNoSAME'] is False:
                            if Check.MatchCLC(ConfigData, GeneratedHeader) is False: print(f"No relay: CLC in generated header ({GeneratedHeader}) did not match config CLC ({ConfigData['AllowedLocations_CLC']})"); continue
                            if Check.CheckEventCodeSAME(ConfigData, GeneratedHeader) is False: print("No relay: Config data, SAME event code blocked for CAP."); continue
                            if AlertIntro_HasBeenPlayed is True:
                                if Check.DuplicateSAME(GeneratedHeader) is True: print("No relay: duplicate SAME header detected from a previous relay."); continue
                            alertColor = GetAlertLevelColor(ConfigData, GeneratedHeader)
                        else:
                            alertColor = GetAlertLevelColor(ConfigData)
                        
                        if ConfigData["ProduceImages"] is True: AIOMG.OutputAlertImage(InfoEN, alertColor)

                        print("Generating audio products...")
                        logge = Log(ConfigData)
                        Gen.Audio(BroadcastText, lang, ConfigData)
                        Alert_Playout = True
                        Plugins_Run("beforeRelay", GeneratedHeader, BroadcastText, InfoEN)
                        
                        try:
                            if lang == "fr": CGEN_headline = "ALERTE D'URGENCE"
                            else: CGEN_headline = "EMERGENCY ALERT"
                            CGEN_Dict = {
                                "color": alertColor,
                                "headline": CGEN_headline,
                                "text": BroadcastText,
                                "alertStat": True
                            }
                            #with open("./alert.txt", "w") as f: f.write(Decoded[1])
                            with open("AlertText.json", 'w') as json_file: json.dump(CGEN_Dict, json_file, indent=2)
                        except: pass

                        if ConfigData[f'PlayoutNoSAME'] is False:
                            print(f"\n...NEW ALERT TO RELAY...\nSAME: {GeneratedHeader}, \nBroadcast Text: {BroadcastText}\nSending alert...")
                            Gen.AudioSAME(GeneratedHeader)
                            try:
                                if lang == "fr": logge.SendLog("ALERTE D'URGENCE", BroadcastText, GeneratedHeader, "TX", alertColor)
                                else: logge.SendLog("EMERGENCY ALERT", BroadcastText, GeneratedHeader, "TX", alertColor)
                            except: pass
                            try: 
                                stopPassthrough.set()
                                PassthroughThread.join()
                                print("Passthrough stopped.")
                            except: pass
                            
                            PlayAlert.AlertIntro()                
                            PlayAlert.AlertSAME()
                            PlayAlert.AlertAttn()
                            PlayAlert.AlertAudio()
                            PlayAlert.AlertEOM()
                            PlayAlert.AlertOutro()
                            Plugins_Run("afterRelay", GeneratedHeader, BroadcastText, InfoEN)
                        else:
                            print(f"\n...NEW ALERT TO RELAY...\nSAME Header is disabled. \nBroadcast Text: {BroadcastText}\nSending alert...")
                            try:
                                if lang == "fr": logge.SendLog("ALERTE D'URGENCE", BroadcastText, "", "TX", alertColor)
                                else: logge.SendLog("EMERGENCY ALERT", BroadcastText, "", "TX", alertColor)
                            except: pass
                            try: 
                                stopPassthrough.set()
                                PassthroughThread.join()
                                print("Passthrough stopped.")
                            except: pass

                            if AlertIntro_HasBeenPlayed is False:
                                PlayAlert.AlertIntro()
                                PlayAlert.AlertAttn()
                                AlertIntro_HasBeenPlayed = True

                            PlayAlert.AlertAudio()

                if Alert_Playout is True:
                    PlayAlert.AlertOutro()

                    if ConfigData["PlayoutNoSAME"] is True:
                        Plugins_Run("afterRelay", GeneratedHeader, BroadcastText, InfoEN)

                    try:
                        if ConfigData["CGEN_ClearAfterAlert"] is True:
                            CGEN_Dict = {
                                "color": "000000",
                                "headline": "Emergency Alert Details",
                                "text": "",
                                "alertStat": False
                            }
                            #with open("./alert.txt", "w") as f: f.write(Decoded[1])
                            with open("AlertText.json", 'w') as json_file: json.dump(CGEN_Dict, json_file, indent=2)
                    except: pass

        except Exception as e:
            UpdateStatus("Relay", f"Relay failure.")
            print("[WARNING] Exception in relay! ", e)
            time.sleep(5)
        except:
            UpdateStatus("Relay", f"Relay failure.")
            print("[WARNING] General exception in relay!")
            time.sleep(5)

def HTTP_CAP(outputFolder, CAP_URL, instance):
    if CAP_URL is None or CAP_URL == "": UpdateStatus(f"HTTPCAPcapture{instance}", f"HTTP CAP capture {instance} disabled.")
    else:
        print(f"[HTTP Capture]: HTTP CAP Capture active! {CAP_URL}")
        while True:
            try:
                UpdateStatus(f"HTTPCAPcapture{instance}", f"HTTP CAP Capture {instance} is active!")
                ReqCAP = Request(url = f'{CAP_URL}')
                CAP = urlopen(ReqCAP).read()
                CAP = CAP.decode('utf-8')
                CAP = re.findall(r'<alert\s*(.*?)\s*</alert>', CAP, re.MULTILINE | re.IGNORECASE | re.DOTALL)

                for alert in CAP:
                    alert = f"<alert {alert}</alert>"
                    CapturedSent = re.search(r'<sent>\s*(.*?)\s*</sent>', alert, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                    CapturedIdent = re.search(r'<identifier>\s*(.*?)\s*</identifier>', alert, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1).replace("-", "_").replace("+", "p").replace(":", "_")
                    filename = f"{CapturedSent}I{CapturedIdent}.xml"
                    with open(f"{outputFolder}/{filename}", 'w', encoding='utf-8') as file: file.write(alert)
                    print(f"[HTTP Capture]: I captured an XML, and saved it to: {outputFolder}/{filename} | From: {CAP_URL}")
                time.sleep(30)
            except Exception as e:
                print("[HTTP Capture] Something went wrong.", e)
                UpdateStatus(f"HTTPCAPcapture{instance}", f"HTTP CAP Capture {instance} error.")
                time.sleep(30)

def NWS_CAP(ATOM_LINK):
    # Goddamnit americans, you have to have every single alert source in their own goddamn way!
    # Why can't you use a centerlized TCP server?!!?!
    print("[NWS CAP Capture]: Activating NWS CAP Capture with: ", ATOM_LINK)
    while True:
        UpdateStatus("NWSCAPcapture", "NWS CAP Capture is active.")
        try:
            HistoryFolder = "XMLhistory"
            req1 = Request(url = ATOM_LINK)
            xml = urlopen(req1).read()
            xml = xml.decode('utf-8')

            entries = re.findall(r'<entry>\s*(.*?)\s*</entry>', xml, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            current_time = datetime.now(timezone.utc)

            for entry in entries:
                try:
                    CAP_LINK = re.search(r'<link\s*rel="alternate"\s*href="\s*(.*?)\s*"/>', entry, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    expires = re.search(r'<cap:expires>\s*(.*?)\s*</cap:expires>', entry, re.MULTILINE | re.IGNORECASE | re.DOTALL).group(1)
                    expires = datetime.fromisoformat(expires).astimezone(timezone.utc).isoformat()
                    expires = datetime.fromisoformat(expires)

                    if current_time > expires: pass #print("expired")
                    else:        
                        last_slash_index = CAP_LINK.rfind('/')
                        if last_slash_index != -1: filename = CAP_LINK[last_slash_index + 1:]
                        else: filename = CAP_LINK 
                        filename = filename.replace("-", "_").replace("+", "p").replace(":", "_").replace("\n", "")
                        filename = filename + ".xml"
                        if filename in os.listdir(f"{HistoryFolder}"): pass #print("already downloaded")
                        elif filename in os.listdir(f"XMLqueue"): pass #print("already downloaded")
                        else:
                            # print(filename, expires)
                            NWSCAP_REQUEST = Request(url = CAP_LINK)
                            NWSCAP_XML = urlopen(NWSCAP_REQUEST).read()
                            NWSCAP_XML = NWSCAP_XML.decode('utf-8')
                            with open(f"XMLqueue/{filename}", "w") as f: f.write(NWSCAP_XML)
                except: pass
        except Exception as e:
            print("[NWS CAP Capture]: An error occured.", e)
            UpdateStatus("NWSCAPcapture", "An error occured.")
        # To put less strain on the network:
        time.sleep(120)

def CheckFolder(folder_path, Clear):
    def ClearFolder(dir):
        for f in os.listdir(dir): os.remove(os.path.join(dir, f))
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    else:
        if Clear is True: ClearFolder(folder_path)

def createDefaultConfig():
    NewConfig = {
        "WebserverPort": "8050",
        "WebserverHost": "0.0.0.0",
        "ProduceImages": False,
        "SAME_callsign": "QUANTUM0",
        "CGENcolor_warning": "ff2a2a",
        "CGENcolor_watch": "ffcc00",
        "CGENcolor_advisory": "00aa00",
        "CGEN_ClearAfterAlert": False,
        "UseSpecified_AudioOutput": False,
        "Specified_AudioOutput": "",
        "EnablePassThru": False,
        "UseSpecified_Passthrough_AudioInput": False,
        "Passthrough_AudioInput": "",
        "AttentionTone": "AttnCAN.wav",
        "Attn_BasedOnCountry": False,
        "Force120": False,
        "PlayoutNoSAME": False,
        "relay_en": True,
        "relay_fr": False,
        "UseDefaultVoices": True,
        "TTS_Service": "pyttsx3",
        "VoiceEN": "",
        "VoiceFR": "",
        "FliteVoice_EN": "",
        "FliteVoice_FR": "",
        "APIvoice_Key": "",
        "APIvoice_Region": "",
        "APIvoice_EN": "",
        "APIvoice_FR": "",
        "enable_discord_webhook": False,
        "webhook_author_name": "",
        "webhook_author_URL": "",
        "webhook_author_iconURL": "",
        "webhook_URL": "",
        "enable_email": False,
        "email_server": "",
        "email_server_port" : 587,
        "email_user": "",
        "email_user_pass": "",
        "email_sendto": [],
        "FancyHTML": True,
        "enable_LogToTxt": True,
        "statusTest": True,
        "statusActual": True,
        "messagetypeAlert": True,
        "messagetypeUpdate": True,
        "messagetypeCancel": True,
        "messagetypeTest": True,
        "severityExtreme": True,
        "severitySevere": True,
        "severityModerate": True,
        "severityMinor": True,
        "severityUnknown": True,
        "urgencyImmediate": True,
        "urgencyExpected": True,
        "urgencyFuture": True,
        "urgencyPast": True,
        "urgencyUnknown": True,
        "AllowedLocations_Geocodes": [],
        "AllowedLocations_CLC": [],
        "CAP_SAMEevent_Whitelist": [],
        "CAP_SAMEevent_Blocklist": [],
        "TCP": False,
        "TCP1": "streaming1.naad-adna.pelmorex.com:8080",
        "TCP2": "streaming2.naad-adna.pelmorex.com:8080",
        "HTTP_CAP": False,
        "HTTP_CAP_ADDR": "",
        "Enable_NWSCAP": False,
        "NWSCAP_AtomLink": "https://api.weather.gov/alerts/active.atom",
        "SAMEmonitor": False,
        "SAMEmonitor-ORIGINATOR-filter": [],
        "SAMEmonitor-EVENT-filter": [],
        "SAMEmonitor-FIPS-filter": [],
        "SAME-AudioDevice-Monitor": False,
        "SAME-AudioStream-Monitor1": "",
        "SAME-AudioStream-Monitor2": "",
        "SAME-AudioStream-Monitor3": "",
        "SAME-AudioStream-Monitor4": ""
    }

    try:
        with open("config.json", 'w') as json_file: json.dump(NewConfig, json_file, indent=2)
    except: return False
    return True

def setup():
    try:
        nothingThing = {
            "nothing":True,
            "alertStat": False
            }
        with open("AlertText.json", 'w') as json_file: json.dump(nothingThing, json_file, indent=2)
        #with open(f"alert.txt", "w") as f: f.write("")
    except: pass
    if os.path.isfile("alertlog.txt") is True: pass
    else:
        with open(f"alertlog.txt", "w", encoding='utf-8') as f: f.write("")
    Clear()
    print(f"\nQuantumENDEC\nVersion: {QEversion}\n\nDeveloped by:\nDell ... ApatheticDELL\nAaron ... secludedfox.com :3\nBunnyTub ... bunnytub.com\n")
    with open("SameHistory.txt", "w") as f: f.write(f"ZXZX-STARTER-\n")
    CheckFolder('stats', True)
    CheckFolder('XMLqueue', True)
    CheckFolder('XMLhistory', True)
    CheckFolder('Audio', False)
    CheckFolder('Audio/tmp', True)
    if os.path.isfile("./config.json") is True: pass
    else:
        print("Can't find config file, creating a default one!")
        if createDefaultConfig() is True: pass
        else: print("Error, failed to create default config file, QuantumENDEC can't run without a config file!"); exit()
    if os.path.isfile("./GeoToCLC.csv") is True: pass
    else: print("GeoToCLC is missing! I can't continue without it."); exit()
    time.sleep(1)


if __name__ == "__main__":
    Plugins_Run("startup")
    parser = argparse.ArgumentParser(description='QuantumENDEC')
    parser.add_argument('-v', '--version', action='store_true', help='Displays QuantumENDECs version and exits.')
    parser.add_argument('-k', '--keepScreen', action='store_true', help='Prevents the terminal screen from clearing.')
    parser.add_argument('-H', '--headless', action='store_true', help='Start QuantumENDEC without starting the webserver.')
    args = parser.parse_args()
    if args.keepScreen is True:
        def Clear(): pass
    if args.version is True: print(f"{QEversion}"); exit()
    setup()
    with open("config.json", "r") as JCfile: config = JCfile.read()
    ConfigData = json.loads(config)

    if args.headless is False: WebThread = threading.Thread(target=StartWEB, daemon=True, args=(ConfigData['WebserverHost'], ConfigData['WebserverPort']))
    RelayThread = threading.Thread(target=Relay, daemon=True)
    
    if ConfigData["TCP"] is True:
        if ConfigData["TCP1"] == "": UpdateStatus("NAAD1", "TCP CAP Capture is disabled.")
        else:
            UpdateStatus("NAAD1", "Starting TCP capture...")
            TCP1cap = Capture("./XMLqueue", ConfigData["TCP1"], "NAAD1")
            TCP1capture_thread = threading.Thread(target=TCP1cap.start, daemon=True)

        if ConfigData["TCP2"] == "": UpdateStatus("NAAD2", "TCP CAP Capture is disabled.")
        else:
            UpdateStatus("NAAD2", "Starting TCP capture...")
            TCP2cap = Capture("./XMLqueue", ConfigData["TCP2"], "NAAD2")
            TCP2capture_thread = threading.Thread(target=TCP2cap.start, daemon=True)
    else:
        UpdateStatus("NAAD1", "TCP CAP Capture is disabled.")
        UpdateStatus("NAAD2", "TCP CAP Capture is disabled.")
        print("[TCP Capture]: TCP CAP capture has been disabled!")

    if ConfigData["HTTP_CAP"] is True:
        HTTPcaptureThread1 = threading.Thread(target=HTTP_CAP, args=("XMLqueue", ConfigData["HTTP_CAP_ADDR"], "1"))
        HTTPcaptureThread2 = threading.Thread(target=HTTP_CAP, args=("XMLqueue", ConfigData["HTTP_CAP_ADDR1"], "2"))
        HTTPcaptureThread3 = threading.Thread(target=HTTP_CAP, args=("XMLqueue", ConfigData["HTTP_CAP_ADDR2"], "3"))
        HTTPcaptureThread4 = threading.Thread(target=HTTP_CAP, args=("XMLqueue", ConfigData["HTTP_CAP_ADDR3"], "4"))
        HTTPcaptureThread5 = threading.Thread(target=HTTP_CAP, args=("XMLqueue", ConfigData["HTTP_CAP_ADDR4"], "5"))

    else:
        print("[HTTP Capture]: HTTP CAP Capture is disabled.")
        UpdateStatus("HTTPCAPcapture", "HTTP CAP Capture is disabled.")

    if ConfigData['Enable_NWSCAP'] is True: NWSCAPthread = threading.Thread(target=NWS_CAP, args=(ConfigData["NWSCAP_AtomLink"],))
    else: UpdateStatus("NWSCAPcapture", "NWS CAP Capture is disabled.")

    if ConfigData[f'SAMEmonitor'] is True:
        print("Starting SAME monitors...")
        from SAMEmonitor import * 
        if ConfigData[f'SAME-AudioDevice-Monitor'] is True: SAMEaudiodevMonitorThread = threading.Thread(target=AUDIOmonitor_run, args=("AudioMonitor",))
        if ConfigData[f'SAME-AudioStream-Monitor1'] != "": SAMEaudiostreamThread_Monitor1 = threading.Thread(target=IPmonitor_run, args=("IpMonitor1", ConfigData[f'SAME-AudioStream-Monitor1']))
        if ConfigData[f'SAME-AudioStream-Monitor2'] != "": SAMEaudiostreamThread_Monitor2 = threading.Thread(target=IPmonitor_run, args=("IpMonitor2", ConfigData[f'SAME-AudioStream-Monitor2']))
        if ConfigData[f'SAME-AudioStream-Monitor3'] != "": SAMEaudiostreamThread_Monitor3 = threading.Thread(target=IPmonitor_run, args=("IpMonitor3", ConfigData[f'SAME-AudioStream-Monitor3']))
        if ConfigData[f'SAME-AudioStream-Monitor4'] != "": SAMEaudiostreamThread_Monitor4 = threading.Thread(target=IPmonitor_run, args=("IpMonitor4", ConfigData[f'SAME-AudioStream-Monitor4']))

    if args.headless is False: WebThread.start()
    print("Starting QuantumENDEC...")
    RelayThread.start()
    
    try: TCP1capture_thread.start()
    except: pass
    try: TCP2capture_thread.start()
    except: pass
    
    try: HTTPcaptureThread1.start()
    except: pass
    try: HTTPcaptureThread2.start()
    except: pass
    try: HTTPcaptureThread3.start()
    except: pass
    try: HTTPcaptureThread4.start()
    except: pass
    try: HTTPcaptureThread5.start()
    except: pass

    try: NWSCAPthread.start()
    except: pass

    try: SAMEaudiodevMonitorThread.start()
    except: pass
    try: SAMEaudiostreamThread_Monitor1.start()
    except: pass
    try: SAMEaudiostreamThread_Monitor2.start()
    except: pass
    try: SAMEaudiostreamThread_Monitor3.start()
    except: pass
    try: SAMEaudiostreamThread_Monitor4.start()
    except: pass

    if args.headless is False: WebThread.join()
    RelayThread.join()
    
    try: TCP1capture_thread.join()
    except: pass

    try: TCP2capture_thread.join()
    except: pass

    try: HTTPcaptureThread1.join()
    except: pass
    try: HTTPcaptureThread2.join()
    except: pass
    try: HTTPcaptureThread3.join()
    except: pass
    try: HTTPcaptureThread4.join()
    except: pass
    try: HTTPcaptureThread5.join()
    except: pass

    try: NWSCAPthread.join()
    except: pass

    try: SAMEaudiodevMonitorThread.join()
    except: pass
    try: SAMEaudiostreamThread_Monitor1.join()
    except: pass
    try: SAMEaudiostreamThread_Monitor2.join()
    except: pass
    try: SAMEaudiostreamThread_Monitor3.join()
    except: pass
    try: SAMEaudiostreamThread_Monitor4.join()
    except: pass

    print("The end of QuantumENDEC")