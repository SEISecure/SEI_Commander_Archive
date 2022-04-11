import datetime
import logging
import math
import threading
import time
import uuid

import txaio
import zeep
from autobahn.twisted.wamp import ApplicationRunner
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp import auth
from requests import Session
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import inlineCallbacks
from zeep.transports import Transport

# Enable Logging SOI Connection Information
# txaio.start_logging(level='debug')

# SOI Information
# TODO: Make sure this base URL is set to the address or DNS name of the host you are connecting to
SOI_BASE = '10.42.5.41'
# TODO: Make sure this parameter is a name that exists on the certificate of the host you are connecting to
dns_name = u'soi'

SOI = 'wss://{}:443/wss'.format(SOI_BASE)  # SOI Host. Can Use IP Instead Of 'soi' Alias
CERT = 'soi.ca.pem'  # Location Of SOI Certificate (Location On SOI VM: /etc/ssl/certs/soi_crt.pem)

# Service Credentials
# NOTE: The 'admin/admin' Account Can Be Used To Test Your Connection
# NOTE: A Service Account Should Be Created For Your Service (See PSU ARL)
# USER = 'admin'
# PASS = 'admin'
USER = 'python'
PASS = 'python'
# Service Information
SERVICE = 'Service Name'

# SOI Schema Hashes
# NOTE: When The Schemas Are Updated, You Will Need To Update These Hashes
# soi-schemas: 1.0.0.0.2
# intel-collection-schemas: 0.0.0.2.1
HASHES = {
    'collectionAsset': '32217d4fe5bf8b72bbc1c04f8e1043907a1b2df0aea07028df3dd797399f7644',
    'collectionAssetStatus': '9ab0edc9168d6c3a599773dd119ddbf0fb0987041e518a11f3a6b7015eae85a6',
    'collectionDetection': 'f5855acdfe16fa8b1500a1c3c05985712334009e5fae8f94c4cefef819b0e836',
    'collectionDetectionFrame': 'aef020d9909a0120a9214848a11e4fc12ca3881c35ce7ec107c2830d53716820',
    'collectionFlight': 'c689f93ed2206547007143477282e80498fe2acff1a2728d05f0bc544a3a24ec',
    'logisticsStatusReport': '17c2f26584ce2ca96356868b425d6e89a130582de09a9831b9f1f1a983d88278',
    'mineContact': 'a970bcfbe60b56aeecec8a0eca33e2d7f155529fa89d67c8a2ecb3d194f04ed3',
    'auditoryDetection': '632dd95e2f3f3ee9abea6ac0387e0d89b7a9e04b102580418f957aef81417296',
    'mineContactNeutralizationRequest': '8f9c0df2df1ba55573af22c0f84e92e64550873901857d1e9108cb11e6cd3243',
    'track': 'bee0fe2a5a7a0305243b64d14249c28b4b0a4ba2f9d58f68f76ed04e2479fe2e',
    'trackDelete': '67b9ea9ecc3401344b00f3b19b33638a86eaaedf737cf6ee6f53eaa61d5102c1',
    'taskingPackage': '9a086f0c40e92a9e168cc81bbe38364fba5a58958172afb7edc79be5e64da448',
    'task': '7dbdbe09c2a715facc3ef1bfe914d0bb8444b45bbec51acb74e6326a6f7e4efb',
    'assetStatus': '65ff3b274ac237cb3bb863f2b2b1ca82e862ea530ce379b88e8097b31e42214f',
    'assetRegistration': '948fc123cb10f414ed96d2ee753336956dbc681319029b02e174430c871621fa',
    'agentRegistration': 'd0405d96f61bc178784a4af9eedd89214317ca11dcc7636eb43b731f11f70128',
    'agentStatus': '9b0b0eaf8fb082c877353dbbc5fe21d8ff2d3632e1aca8171b5c71d6495917c9',
}

# Example Track Info Message
# NOTE: Check The Message Tracker App For JSON Schema (Fields, Required, Restrictions, etc.)
TRACK = {
    "entity": {
        "entityId": str(uuid.uuid4()),
        "type": "PLATFORM",
        # This is the type of entity the track represents, UNIT, TBMS, PLATFORM, ORGANIC, INDIVIDUAL, FACILITY, FAA, EVENT, EMITTER, COMMUNICATIONS, and ACOUSTIC are the types
        "alignment": "FRD",  # This is the alignment of the track: FRD, HOS, UNK, NEU, PND, AFD, or SUS
        "environment": "AIR",  # This is the environment the track lives in: AIR, SUB, SUR, LND, SPC, or UNK
        "labels": {
            "name": "the name of the track"
        },
        "symbol": {
            "sidc": "SHUPSNB--------",
            "specification": "C"  # This is the 2525 symbology: A, B, C, or D
        },
        "civilian": False,  # If the track is a civilian
        "classification": "UNCLASSIFIED"
        # If the track is classified: UNKNOWN, UNCLASSIFIED, CONFIDENTIAL, SECRET, SECRET_NO_FOREIGN, TOP_SECRET, SPECIAL
    },
    "report": {
        "dtg": int(time.mktime(datetime.datetime.now().timetuple()) * 1000),
        "position": {
            "latitude": 33.777,
            "longitude": 123.333
        },
        # source is optional but recommended
        "source": {
            "name": "whatever name you want",
            "system": "TSOA"
        }
    }
}

ASSET_STATUS = {
    "statusId": "status-1",
    "assetId": "nibbler-1",
    "timestamp": 1643815276000,
    "location": {
        "type": "POSITION",
        "position": [0, 0],
        "grid": "31N",
        "area": [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
        "relative": {
            "reference": "lighthouse-1",
            "bearing": 43.1,
            "distance": 189.7
        },
        "named": "bn-1-5-hq",
        "uncertainty": 100,
        "measured": True,
        "stationary": False,
        "arrival": 1643815276000,
        "departs": 1643815276000
    },
    "height": 1000,
    "movement": {
        "heading": 43.2,
        "speed": 5.4,
        "roll": 3.2,
        "pitch": 1.2
    },
    "weapons": [{
        "weaponId": "weapon-1",
        "state": "POWERED",
        "ranges": [{
            "outerRadius": 50,
            "innerRadius": 25,
            "bearing": 23,
            "length": 98
        }]
    }],
    "sensors": [{
        "sensorId": "sensor-1",
        "state": "PASSIVE",
        "ranges": [{
            "outerRadius": 50,
            "innerRadius": 25,
            "bearing": 23,
            "length": 98
        }]
    }],
    "engines": [{
        "engineId": "engine-1",
        "state": "OPERATIONAL"
    }],
    "power": [{
        "powerSourceId": "battery-1",
        "measurement": 15.2,
        "unit": "V"
    }],
    "munitions": [{
        "dodic": "G881",
        "measurement": 2
    }],
    "radios": [{
        "radioId": "radio-1",
        "state": "ACTIVE",
        "ranges": [{
            "outerRadius": 100,
            "innerRadius": 0,
            "bearing": 0,
            "length": 360
        }]
    }],
    "authority": "agent-1",
    "schedule": {
        "location": {
            "type": "POSITION",
            "position": [1, 1],
            "measured": False,
            "arrival": 1643815276000
        },
        "communications": 1643815276000
    },
    "logs": [{
        "code": "e.asset.sensor.movement.failed",
        "timestamp": 1643815276000,
        "level": "ERROR",
        "subjectId": "sensor-1",
        "message": "Go Pro 5 movement is jammed."
    }]
}

ASSET_REGISTRATION = {
    "assetId": "nibbler-1",
    "name": "NIBBLER 1",
    "timestamp": 1643815276000,
    "symbol": {
        "specification": "C",
        "sidc": "SFAPMHQ-----"
    },
    "sensors": [{
        "sensorId": "sensor-1",
        "modelId": "go.pro.5"
    }, {
        "sensorId": "sensor-2",
        "modelId": "gps"
    }],
    "weapons": [{
        "weaponId": "weapon-1",
        "modelId": "grenade.launcher",
    }],
    "engines": [
        {"engineId": "sensor-1", "modelId": "rotary.quad", "powerSourceId": "battery-1"},
        {"engineId": "sensor-2", "modelId": "rotary.quad", "powerSourceId": "battery-1"},
        {"engineId": "sensor-3", "modelId": "rotary.quad", "powerSourceId": "battery-1"},
        {"engineId": "sensor-4", "modelId": "rotary.quad", "powerSourceId": "battery-1"}
    ],
    "power": [{
        "powerSourceId": "battery-1",
        "modelId": "battery.lithium.ion"
    }],
    "munitions": [{
        "dodic": "G881",
        "payload": False
    }],
    "radios": [{
        "radioId": "radio-1",
        "modelId": "wifi"
    }],
    "taskbook": [{
        "entryId": "1.2",
        "fidelity": 2
    }]
}

MESSAGE = {
    "detectionId": str(uuid.uuid4()),
    "sensorId": "Sensor_Name",
    "latitude": 22.111,
    "longitude": 33.111,
    "soundClass": "unknown",
    "ampRMS": 3.018,
    "dataType": "FLOAT32",
    "shapeX": int(11298),
    "shapeY": int(1),
    "sampleRate": 44100,
    "timestamp": int(time.mktime(datetime.datetime.now().timetuple()) * 1000),
    "fileURL": "sample"
}
TASKING_PACKAGE = {
  "packageId": "package-1",
  "pedigree": {
    "node": {
      "nodeId": "node-1",
      "name": "BN 1/5 Node"
    },
    "user": {
      "dodId": 1,
      "name": "Capt. John Smith",
      "username": "j.smith"
    },
    "agent": {
      "agentId": "agent-1",
      "name": "AI Squad A"
    },
    "unit": {
      "urn": 2030847,
      "uic": "M11160",
      "name": "BN 1/5"
    },
    "service": {
      "name": "Mission Planning",
      "system": "TSOA",
      "version": "0.0.0.1.0"
    }
  },
  "temporal": {
    "created": 1642604559000,
    "updated": 1642604559000
  },
  "environment": {
    "arcs": [{
      "graphicId": "arc-1",
      "center": [0, 0],
      "radius": 10,
      "bearing": 45,
      "length": 90
    }],
    "boxes": [{
      "graphicId": "box-1",
      "center": [0, 0],
      "height": 20,
      "width": 20
    }],
    "circles": [{
      "graphicId": "circle-1",
      "center": [0, 0],
      "radius": 20
    }],
    "ellipses": [{
      "graphicId": "ellipse-1",
      "center": [0, 0],
      "semiMajor": 20,
      "semiMinor": 25
    }],
    "points": [{
      "graphicId": "point-1",
      "location": [0, 0]
    }],
    "polygons": [{
      "graphicId": "polygon-1",
      "points": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    }],
    "polylines": [{
      "graphicId": "polyline-1",
      "points": [[0, 0], [0.5, 0.5], [1, 1]]
    }],
    "sectors": [{
      "graphicId": "sector-1",
      "center": [0, 0],
      "outerRadius": 25,
      "innerRadius": 20,
      "bearing": 45,
      "length": 90
    }]
  },
  "forces": {
    "type": "UNIT",
    "unit": {
      "urn": 2030847,
      "uic": "M11160",
      "name": "BN 1/5"
    },
    "subordinates": [
      {
        "type": "AGENT",
        "agent": {
          "agentId": "agent-1",
          "name": "AI Squad A"
        },
        "subordinates": [
          {
            "type": "ASSET",
            "asset": {
              "assetId": "asset-1",
              "name": "Quad 1"
            }
          },
          {
            "type": "ASSET",
            "asset": {
              "assetId": "asset-2",
              "name": "Swarm 1"
            }
          }
        ]
      },
      {
        "type": "ASSET",
        "asset": {
          "assetId": "asset-3",
          "name": "Puma 1"
        }
      }
    ]
  },
  "criteria": [
    {
      "criteriaId": "criteria.timeline.1",
      "type": "TIMELINE",
      "timeline": {
        "before": 1642604559000,
        "after": 1642604559000,
        "elapsed": 10000
      }
    },
    {
      "criteriaId": "criteria.event.1",
      "type": "EVENT",
      "event": {
        "type": "OBSERVATION",
        "affiliation": "HOS",
        "reliability": "CONFIDENT",
        "within": ["polygon-1"],
        "excludes": ["circle-1"]
      }
    }
  ],
  "constraints": [
    {
      "constraintId": "constraint.timeline.1",
      "type": "TIMELINE",
      "timeline": {
        "before": 1642604559000,
        "after": 1642604559000,
        "elapsed": 10000
      }
    },
    {
      "constraintId": "constraint.area.1",
      "type": "GEOSPATIAL",
      "geospatial": {
        "type": "NO_FLY_ZONE",
        "boundary": "WITHIN",
        "graphicId": "polygon-1"
      }
    },
    {
      "constraintId": "constraint.communications.1",
      "type": "COMMUNICATIONS",
      "communications": {
        "type": "PASSIVE"
      }
    }
  ],
  "behaviors": [
    {
      "behaviorId": "posture.observe.area.1",
      "default": True,
      "forces": ["asset-1"],
      "constraints": ["constraint.communications.1"],
      "tasks": [
        {
          "taskId": "behavior.1.task.1.launch.asset.1",
          "objective": "LAUNCH",
          "location": {
            "type": "NAMED",
            "named": "point-1"
          },
          "target": "asset-1"
        },
        {
          "taskId": "behavior.1.task.2.move.asset.point.1",
          "objective": "MOVE",
          "location": {
            "type": "POSITION",
            "position": [0, 0]
          },
          "concurrent": [
            {
              "taskId": "behavior.1.task.2.A.move.asset.point.1",
              "objective": "OBSERVE"
            }
          ],
          "alternate": "behavior.1.task.3.move.asset.point.3"
        },
        {
          "taskId": "behavior.1.task.3.move.asset.point.2",
          "objective": "MOVE",
          "location": {
            "type": "POSITION",
            "position": [1, 1]
          },
          "concurrent": [
            {
              "taskId": "behavior.1.task.3.A.move.asset.point.2",
              "objective": "OBSERVE"
            },
            {
              "taskId": "behavior.1.task.3.B.move.asset.point.2",
              "objective": "COMMUNICATE",
              "permit": ["constraint.communications.1"]
            }
          ]
        },
        {
          "taskId": "behavior.1.task.3.move.asset.point.3",
          "objective": "MOVE",
          "location": {
            "type": "POSITION",
            "position": [2, 2]
          }
        },
        {
          "taskId": "behavior.1.task.2.observe.area.1",
          "objective": "OBSERVE",
          "constraints": ["constraint.area.1", "constraint.communications.1"],
          "location": {
            "type": "NAMED",
            "named": "polygon-1"
          }
        }
      ]
    },
    {
      "behaviorId": "behavior.return.to.base",
      "forces": ["asset-1"],
      "conditions": [
        {
          "criteriaId": "criteria.timeline.1"
        },
        {
          "logic": "OR",
          "conditions": [
            {
              "criteriaId": "criteria.event.1"
            },
            {
              "criteriaId": "criteria.event.2"
            }
          ]
        }
      ],
      "constraints": ["constraint.communications.1"],
      "tasks": [
        {
          "taskId": "behavior.2.task.1.move.asset.point.2",
          "objective": "MOVE",
          "location": {
            "type": "POSITION",
            "position": [0, 0]
          }
        },
        {
          "taskId": "behavior.2.task.1.move.asset.point.2",
          "objective": "LAND",
          "location": {
            "type": "POSITION",
            "position": [0, 0]
          }
        }
      ]
    }
  ]
}

# SOI Client
def onTaskingPackage(*args, **kargs):
    print("\n\nGot Tasking Package:")
    #print("\n\nGot Tasking Package: {}".format(kargs['message']))
    #print("\n\nargs: ", args)
    #print("\n\nkargs: ", kargs)
    message = kargs['message']
    packId = message['packageId']
    print ("packageId: " , packId)
    waypoints = message['environment']['polygons'][0]
    print ("waypoints: " , waypoints)


def onTrack(*args, **kargs):
    print("\n\nGot Track Info: {}".format(kargs['message']))


def onAudio(*args, **kargs):
    print("\n\nGet Audio Detection: {}".format(kargs['message']))

def onAssetStatus(*args, **kargs):
    print("\n\nGet Asset Status: {}".format(kargs['message']))

def onAssetRegistration(*args, **kargs):
    print("\n\nGet Asset Registration: {}".format(kargs['message']))


def buildGeospatialCoverage(latitude, longitude):
    # Calculate Positive Lat / Lon
    # NOTE: DMS Does Not Use Negative Values
    latP = abs(latitude)
    lonP = abs(longitude)

    # Determine Base Degrees (D), Minutes (M) and Seconds (S) For Latitude
    latD = math.floor(latP)
    latM = math.floor((latP - latD) * 60)
    latS = (((latP - latD) * 60) - latM) * 60

    # Determine Base Degrees (D), Minutes (M) and Seconds (S) For Longitude
    lonD = math.floor(lonP)
    lonM = math.floor((lonP - lonD) * 60)
    lonS = (((lonP - lonD) * 60) - lonM) * 60

    # Determine Hemispheres
    latH = 'north' if latitude >= 0 else 'south'
    lonH = 'east' if longitude >= 0 else 'west'

    # Set Point D/M/S/Hemisphere
    point = {
        'geoLatHemisphere': latH,
        'geoLongHemisphere': lonH,
        'geoDegree': {
            'latitude': latD,
            'longitude': lonD
        },
        'geoDegreeFraction': {},
        'geoMinute': {
            'latitude': latM,
            'longitude': lonM
        },
        'geoMinuteFraction': {},
        'geoSecond': {
            'latitude': math.floor(latS),
            'longitude': math.floor(lonS)
        },
        'geoSecondFraction': {
            'decisecond': {
                'latitude': 0,
                'longitude': 0
            },
            'centisecond': {
                'latitude': 0,
                'longitude': 0
            },
            'millisecond': {
                'latitude': 0,
                'longitude': 0
            },
        },
    }

    # Get Fractional Seconds
    latSF = latS - math.floor(latS)
    lonSF = lonS - math.floor(lonS)

    # Get Milliseconds
    latMs = latSF * 1000.0
    lonMs = lonSF * 1000.0

    # Calculate Fraction
    latFraction = math.floor(latMs)
    lonFraction = math.floor(lonMs)

    # Check For Latitude Millisecond Round
    if latFraction == 1000:
        # Add One To The Second
        point['geoSecond']['latitude'] = point['geoSecond']['latitude'] + 1

        # Clear The Fraction
        latFraction = 0

    # Check For Longitude Millisecond Round
    if lonFraction == 1000:
        # Add One To The Second
        point['geoSecond']['longitude'] = point['geoSecond']['longitude'] + 1

        # Clear The Fraction
        lonFraction = 0

    # Set The Latitude Fractions
    if len(str(latFraction)) == 1:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['latitude'] = int(str(latFraction)[0], 10)
    elif len(str(latFraction)) == 2:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['latitude'] = int(str(latFraction)[0], 10)

        # Set The Centisecond
        point['geoSecondFraction']['centisecond']['latitude'] = int(str(latFraction)[1], 10)
    else:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['latitude'] = int(str(latFraction)[0], 10)

        # Set The Centisecond
        point['geoSecondFraction']['centisecond']['latitude'] = int(str(latFraction)[1], 10)

        # Set The Millisecond
        point['geoSecondFraction']['centisecond']['latitude'] = int(str(latFraction)[2], 10)

    # Set The longitude Fractions
    if len(str(lonFraction)) == 1:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['longitude'] = int(str(lonFraction)[0], 10)
    elif len(str(lonFraction)) == 2:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['longitude'] = int(str(lonFraction)[0], 10)

        # Set The Centisecond
        point['geoSecondFraction']['centisecond']['longitude'] = int(str(lonFraction)[1], 10)
    else:
        # Set The Decisecond
        point['geoSecondFraction']['decisecond']['longitude'] = int(str(lonFraction)[0], 10)

        # Set The Centisecond
        point['geoSecondFraction']['centisecond']['longitude'] = int(str(lonFraction)[1], 10)

        # Set The Millisecond
        point['geoSecondFraction']['centisecond']['longitude'] = int(str(lonFraction)[2], 10)

    return [
        {
            'boundingGeometry': [
                {
                    'point': [
                        {
                            'pointType': {
                                'horizPresentation': {
                                    'sexagesimalLocation': [
                                        point
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]


class ClientSession(ApplicationSession):
    def __init__(self, queue, ghub):
        super().__init__()
        self._queue = queue
        self.ghub_connection = ghub

    # Invoke WAMP CRA Authentication Upon SOI Connection

    def sendMessage(self, msg):
        return self.call('f.soi.validate',
                         hash=msg['hash'],
                         message=msg['message'],
                         identifiers=msg['identifiers'],

                         # Time The Message Was Relevant - Milliseconds since 1970
                         reference_time=msg['reference_time'],
                         metadata=msg['metadata'],
                         nodes=[]
                         )

    def onConnect(self):
        print("Authenticating With SOI")
        self.join("soi", ["wampcra"], USER)

    # Respond With Password On Authentication Challenge
    def onChallenge(self, challenge):
        if challenge.method == "wampcra":
            signature = auth.compute_wcs(PASS, challenge.extra['challenge'])
            return signature
        else:
            raise Exception("Invalid Authentication Method {}".format(challenge.method))

    # When The Client Leaves The WAMP Session
    def onLeave(self, details):
        print("SOI Client Left Session: {}".format(details))

        # NOTE: This Is Here So The Example Service Will End When The Client Is Disconnected
        self.disconnect()

    # When The Client Is Disconnected From SOI
    # NOTE: Reconnect Should Happen Automatically
    def onDisconnect(self):
        print("SOI Client Disconnected.")

        # NOTE: This Is Here So The Example Service Will End When The Client Is Disconnected
        if reactor.running:
            reactor.stop()

    #
    # Runs When Connected To SOI. Initialize Your Logic Here.
    #
    @inlineCallbacks
    def onJoin(self, details):
        print("Connected To SOI!")

        # Subscribe For Messages
        # NOTE: You will receive messages that you sent to SOI if you're subscribed to the same message type
        yield self.subscribe(onTrack, 'c.soi.valid.' + HASHES['track'])
        yield self.subscribe(onAudio, 'c.soi.valid.' + HASHES['auditoryDetection'])
        yield self.subscribe(onTaskingPackage, 'c.soi.valid.' + HASHES['taskingPackage'])
        yield self.subscribe(onAssetRegistration, 'c.soi.valid.' + HASHES['assetRegistration'])
        yield self.subscribe(onAssetStatus, 'c.soi.valid.' + HASHES['assetStatus'])

        while True:
            msg = yield self._queue.get()
            # TODO: sanity checks on the message to make sure it contains relevent fields
            self.sendMessage(msg)


class GHubClient:
    # Create client with endpoint being the IP of SOI, for example: "http://xxx.xxx.xxx.xx:8780/ghub/BasicGHubWebService?wsdl"
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.soap_client = None
        session = Session()
        session.verify = False
        transport = Transport(session=session)
        try:
            print("trying to connect")
            self.soap_client = zeep.Client(self.endpoint, transport=transport)
            print("GHubClient client connected.")
        except Exception as e:
            print("[ error ] GHubClient: error connecting to GHub.")
            print(e)

    def folder_exists(self, folder_name):
        # Return if folder_name already exists
        request_data = {
            'ghubRef': '/{}'.format(folder_name)
        }
        response = self.soap_client.service.exists(**request_data)
        # response == True/False
        return response

    def create_folder(self, folder_name):
        if self.folder_exists(folder_name):
            return
        request_data = {
            'parentGHubPathStr': '/',
            'folderName': folder_name
        }
        response = self.soap_client.service.createFolder(**request_data)
        folder_uuid = response
        return folder_uuid

    def dataset_exists(self, folder_name, dataset_name):
        # Return if folder_name already exists
        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name)
        }
        response = self.soap_client.service.exists(**request_data)
        # response == True/False
        return response

    def get_dataset_uuid(self, folder_name, dataset_name):
        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name)
        }
        response = self.soap_client.service.getDatasetInfo(**request_data)
        return response['datasetID']

    def create_dataset(self, folder_name, dataset_name):
        print("GHubClient.create_dataset: creating dataset {}".format(dataset_name))
        if self.dataset_exists(folder_name, dataset_name):
            print("GHubClient.create_dataset: dataset {} already exists!".format(dataset_name))
            return self.get_dataset_uuid(folder_name, dataset_name)
        request_data = {
            'ghubRef': '/{}'.format(folder_name),
            'metadata': {
                'Title': dataset_name,
                'ID': dataset_name,
                'Creator': '?',
                'security': '?',
                'GeographicExtent': {
                    'BoundingBox': {
                        'minx': '?',
                        'maxx': '?',
                        'miny': '?',
                        'maxy': '?'
                    }
                },
                'CreationDate': '?',
                'SearchRank': '?',
                'SetType': 'Generic Files'
            }
        }
        response = self.soap_client.service.createDataset(**request_data)
        print("GHubClient.create_dataset: response {}".format(response))
        # response is the (UU)ID of the new dataset
        return response

    def add_file(self, filename, data, folder_name, dataset_name):
        request_data = {
            'ghubRef': '/{}/{}'.format(folder_name, dataset_name),
            'addFileList': [
                {
                    'name': filename,
                    'contents': data
                }
            ]
        }
        response = self.soap_client.service.updateDataset(**request_data)
        print("GHubClient.add_file: response {}".format(response))

    def get_URL(self, filename, dataset, folder):
        return "{}/ghub/repo/{}/{}/!file/{}".format("http://is2ops:8780", folder, dataset, filename)


class ClientConnection:
    def __init__(self):
        self._session = None
        self._queue = DeferredQueue(size=500)
        self._ghub_connection = None
        with open(CERT) as certAuthCertFile:
            # Set The CA To The SOI Certificate
            authority = ssl.Certificate.loadPEM(certAuthCertFile.read())
            # Add The CA TO The SSL Client
            options = ssl.optionsForClientTLS(dns_name, authority)
            # Create The SOI Client
            self.runner = ApplicationRunner(url=SOI, realm='soi', ssl=options)

    def run(self):
        # Start The SOI Client
        self._session = ClientSession(self._queue, self._ghub_connection)
        self.runner.run(self._session, auto_reconnect=True)

    def publish(self, schema_hash, entity_id, message, latitude, longitude, reference_time):
        if self._session is None:
            logging.warning("SOI session not started")
            return
        # reactor.callInThread(self.session.sendTrack, asset)
        self._queue.put({
            "hash": schema_hash,
            "message": message,
            "identifiers": {
                'entity_id': entity_id
            },
            "metadata": {
                # Optional: Creator Can Be An Asset (Shown Fields) Or Person (Different Fields)
                'creator': [
                    {
                        'service': {
                            'name': ['Asset Name']
                        }
                    }
                ],

                # Optional: Service Publishing Message
                'publisher': [
                    {
                        'service': {
                            'name': [SERVICE]
                        }
                    }
                ],

                # Source Of The Message (Always TSOA)
                'source': [
                    {
                        'value': 'ORG'
                    }
                ],

                # Optional: Location (lat/lon) referenced in message content
                'geospatialCoverage': buildGeospatialCoverage(
                    latitude,
                    longitude
                )
            },
            "reference_time": reference_time
        })
        # update sync list here


# Main Service
if __name__ == '__main__':
    client = ClientConnection()
    th = threading.Thread(None, client.run, None, (), {})
    th.start()

    #client.publish(HASHES['assetRegistration'], "nibbler-1", ASSET_REGISTRATION, 1, 1, 100)
    #client.publish(HASHES['assetStatus'], "nibbler-1", ASSET_STATUS, 1, 1, 200)
    #client.publish(HASHES['track'], "nibbler-1", TRACK, 1, 1, 300)
    client.publish(HASHES['taskingPackage'], "nibbler-1", TASKING_PACKAGE, 1, 1, 400)
