#!/usr/bin/env python3

import rospy, math, time, datetime
from action_processor.artemis_mode import *
import socket, errno, sys, struct, subprocess, re
from std_msgs.msg import UInt16, Bool, UInt8, String, Float32, UInt64
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PointStamped, Point
from saft_msgs.msg import contact_group_msg, ael_state_msg, command_msg, scan_point_list, single_scan_point
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
from subprocess import check_output
import threading
from atak_cot_sender import tak_cot_sdk
from athena_messages import Principal_Athena_Message, Artemis_Message, Artemis_General_Order, Scan_Point
import numpy as np


import mgrs

class AthenaInterfaceNode(object):
    """
    Interface implementation between Athena and Artemis.

    Parameters
    -----------
    None

    Attributes
    ----------
    self.asset_type : type of assest, currently match artemis_id
    self.artemis_id : last 3 digits of ip
    self.destination_id : last 3 digits of Athena ip
    self.uid_self : Cot message id
    self.self_type : CoT message type

    Outputs to Athena
    -----------------
    Protobuff : contains Artemis specific details.
    CoT : sends targets to Athena (wip)

    Inputs from Athena
    ------------------
    Protobuff : Contains orders to Artemis
    CoT : Contains a slew to cue target
    """
    def __init__(self):


        ips = check_output(['hostname', '--all-ip-addresses']).split()
        ips_filtered = [ip for ip in ips if ip[0:3].decode() == '10.']
        # self.artemis_ip  = "10.1.0.132"
        # self.artemis_ip = "10.1.0.135"
        self.artemis_ip = self.get_ip_address()
        self.ip_split_str = self.artemis_ip.split('.')
        self.ip_split_str = self.artemis_ip[-3:]
        self.ip_split_int = int(self.ip_split_str)
        print("Artemis IP  : {}".format(self.artemis_ip))
        split = self.artemis_ip.split(".")
        self.asset_type = self.ip_split_int
        self.artemis_id = self.ip_split_int
        self.destination_id = "Athena_1"
        self.uid_self = 'Artemis-'+ self.ip_split_str
        self.self_type = 'a-f-G'
        self.continue_looping = 1
        self.uid_target = "Artemis-Target-" + self.ip_split_str + "."
        self.target_id = 1
        self.hostile_type = 'a-h-G'
        self.unknown_type = 'a-s-G'
        self.selected_track_id = 0
        self.recent_general_order = None
        self.UTM_coordinate = ""

        self.current_artemis_mode = ArtemisMode()

        self.current_pan_position = 0
        self.current_tilt_position = 0
        self.current_gps_lat = 38.350326
        self.current_gps_long = -77.061612
        self.current_gps_alt = 0
        self.current_heading = 0
        self.zoom = 0
        self.current_target_list = 0
        self.fire_fan_left = 0
        self.fire_fan_right = 0
        self.ammo_count = 100000
        self.current_scan_pattern = None

        self.principal_proto = Principal_Athena_Message()

        self.update_message()

        self.go_lock = threading.Lock()
        self.last_data = 0.0
        """
        Set up Subscribers for node
        """
        rospy.Subscriber('/position_feedback', PointStamped, self.position_callback)
        rospy.Subscriber("tracking_system/contact_group", contact_group_msg,
                         self.target_list_callback, queue_size=1)
        rospy.Subscriber('configuration/athena_ip', String,
                         self.athena_ip_callback, queue_size=1)
        rospy.Subscriber('configuration/artemis_id', String,
                         self.artemis_id_callback, queue_size=1)
        rospy.Subscriber('lrf_response', Float32,
                          self.lrf_data_callback, queue_size=1)
        rospy.Subscriber('/current_gps_location', NavSatFix, self.update_gps_callback)
        rospy.Subscriber('/current_heading', Float32, self.update_heading_callback)
        rospy.Subscriber('/ael_state', ael_state_msg, self.current_artemis_mode.update_states)
        rospy.Subscriber("select_track", UInt64, self.selected_track_callback)
        rospy.Subscriber('client_connected', String, self.client_connected_callback)
        rospy.Subscriber('client_disconnected', String, self.client_disconnected_callback)
        rospy.Subscriber('general_order_status', command_msg, self.general_order_callback)
        rospy.Subscriber('set_scan_points', scan_point_list, self.explict_set_scan_points_callback, queue_size=1)
        rospy.Subscriber('camera_eo/current_fov_rad', Float32, self.fov_callback, queue_size=1)

        """
        Set up Publishers for Node
        """
        self.auto_acquire_pub = rospy.Publisher("auto_acquire", Bool, queue_size=1)
        self.auto_scan_pub = rospy.Publisher('auto_scan', Bool, queue_size=1)
        self.auto_fire_pub = rospy.Publisher('auto_fire_mode', UInt16, queue_size=1)
        self.slew_to_cue_mode_pub = rospy.Publisher('slew_to_cue_mode', UInt16, queue_size=1)
        self.athena_enable_pub = rospy.Publisher('athena_enable', Bool, queue_size=1)
        self.gps_publsih = rospy.Publisher('current_gps_location', NavSatFix, queue_size=1)
        self.cue_coordinate = rospy.Publisher('cue_coordinate', Point, queue_size=1)
        self.reported_target_pub = rospy.Publisher('reported_target', UInt64, queue_size=1)
        self.order_pub = rospy.Publisher('internal/external_general_order', command_msg, queue_size=1)
        self.scan_point_pub = rospy.Publisher('internal/external_scan_point_list', scan_point_list, queue_size=1)
        self.lrf_request_pub = rospy.Publisher('lrf_request', Bool, queue_size=1)

        self.utm_coord_pub = rospy.Publisher('lrf_target_position', String, queue_size=1)
        """
        Member variables
        """


        self.cot_to_send = 0

        """
        Member Variables to store Artemis State Information
        """

        """ Start trying to set up sockets """
        self.sockets_not_set_up = True
        self.send_sockets = []

        """
        ROS Rate
        """
        self.rate = rospy.Rate(1)

        """
        Threads
        """

        self.set_up_sockets = None
        self.read_protobuff_thread = None
        self.receive_cot_thread = None
        self.spin_thread = None

        self.receive_cot_socket = None
        self.athena_socket = None
        self.athena_receive_socket = None
        self.athena_send_cot_socket = None
        self.cot_receive_socket = None


        """
        Socket to Recieve CoT from Athena.
        """
        self.cot_receive_port = int(rospy.get_param("cot_receive_port"))
        self.cot_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cot_receive_socket.bind((self.artemis_ip, self.cot_receive_port))
        self.cot_receive_socket.setblocking(0)
        print("Receive cot to Athena socket set up")
        """
        Needed for Context Manager
        """
        self.set_up_connections()
        self.stop_event = threading.Event()


    # Either Function works

    # def run_cmd(self,cmd):
    #     return subprocess.check_output(cmd, shell=True).decode('utf-8')

    # def get_udp_ip(self):
    #     try:
    #         cmd = "hostname -I"
    #         result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    #         result = re.findall(r'10\.1\.\d*\.\d*',result)[0]
    #         return result
    #     except Exception as error:
    #         print("{}: error in get_udp_ip: {}".format(self.get_current_time(),error))

    def get_ip_address(self):
        """Get Self IP address on the kobol network"""
        try:
            ips = check_output(['hostname', '--all-ip-addresses']).split()
            for ip in ips:
                ip = ip.decode('utf-8')
                if(ip[0:4] == '10.1'):
                    return ip

        except Exception as error:
            print("{}: Error in get ip address :{}".format(self.get_current_time(),error))
            return None

    def __enter__(self):
        """ Context Manager Start """
        self.start()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """ Context Manager Stop """
        self.stop()

    def start(self):
        """ Begin Thread Execution """
        if self.read_protobuff_thread is not None or self.receive_cot_thread is not None or self.spin_thread is not None:
            self.stop()
        self.stop_event.clear()
        print("starting read protobuf thread")
        self.read_protobuff_thread = threading.Thread(target=self.receive_protobuf_data, args=())
        self.read_protobuff_thread.start()
        print("protobuf thread started")
        self.receive_cot_thread = threading.Thread(target=self.receive_cot, args=())
        self.receive_cot_thread.start()
        print("cot thread started")
        self.spin_thread = threading.Thread(target=self.spin, args=())
        self.spin_thread.start()
        print("spin thread started")

        rospy.logdebug(' Began Protobuff and CoT Receive Threads.')

    def stop(self):
        """ End Thread Execution """
        self.continue_looping = 0
        self.stop_event.set()
        self.read_protobuff_thread.join()
        self.receive_cot_thread.join()
        self.read_protobuff_thread = None
        rospy.logdebug(' Ended Protobuff and CoT Receive Threads.')

    def set_up_connections(self):

        while self.sockets_not_set_up == True:

            try:
                """
                Socket for Sending Protobuff to Athena.
                """
                self.athena_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.athena_ip = rospy.get_param("athena_ip")
                self.athena_port = int(rospy.get_param("athena_port"))
                self.send_sockets.append([self.athena_socket, self.athena_ip, self.athena_port, "athena"])
                print("Send protobuf to Athena socket set up")

                """
                Socket to Send CoT to Athena.
                """
                self.cot_port = int(rospy.get_param("cot_port"))
                self.athena_send_cot_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("Send Cot to Athena socket set up")
                self.sockets_not_set_up = False
                print("Athena Interface - Athena sockets Set Up")

            except:
                time.sleep(2)

    def spin(self):
        """ Sends information at rate to Athena about Artemis State"""
        while self.continue_looping == 1:
            with self.go_lock:
                self.update_message()
                #print(self.principal_proto)
                messageToSend = self.principal_proto.SerializeToString()
                for socket_instance in self.send_sockets:
                    try:
                        socket_instance[0].sendto(messageToSend, (socket_instance[1], socket_instance[2]))
                    except:
                        print('protobuff socket send error')

            try:
                update_cot_message = self.create_cot_message(self.uid_self, self.current_gps_lat, self.current_gps_long, self.self_type, self.current_gps_alt)
                self.athena_send_cot_socket.sendto(update_cot_message, (self.athena_ip, self.cot_port))
                if self.cot_to_send != 0:
                    #print("sending TARGET cot ", self.cot_to_send)
                    self.athena_send_cot_socket.sendto(self.cot_to_send, (self.athena_ip, self.cot_port))
                    self.cot_to_send = 0

            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    self.rate.sleep()

            except:
                print("Athena Interface Some Socket Error ", socket.error)

            self.rate.sleep()

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def receive_protobuf_data(self):
        """ Receives and parses protobuff messages. Sends out state changes. """
        while self.continue_looping == 1:
            try:
                if self.athena_receive_socket != None:
                    data = self.athena_receive_socket.recv(1024)
                    # print("{}:Data Received: {}".format(self.get_current_time(),data))
                    # message = athena_artemis_message_pb2.Artemis_Message()
                    principal_message = Principal_Athena_Message()
                    principal_message.ParseFromString(data)

                    #print(principal_message)

                    #print(principal_message)
                    # print("{}: Proto Message is :{}".format(self.get_current_time(),principal_message))
                    for artemis_message in principal_message.artemis:
                        # print("{}: Artemis message is: {}".format(self.get_current_time(),artemis_message))
                        if self.current_gps_lat == 0 and self.current_gps_lat != artemis_message.latitude:
                            self.current_gps_lat = artemis_message.latitude

                        if self.current_gps_long == 0 and self.current_gps_long != artemis_message.longitude:
                            self.current_gps_long = artemis_message.longitude

                        if self.current_heading != 0:
                            self.current_heading = artemis_message.heading

                        if self.current_gps_lat !=0 and self.current_gps_long !=0:
                            gps_msg = NavSatFix()
                            gps_msg.latitude = self.current_gps_lat
                            gps_msg.longitude = self.current_gps_long
                            self.gps_publsih.publish(gps_msg)


                        scan_msg = scan_point_list()
                        order_msg = command_msg()

                        for general_order in artemis_message.orders:
                            # print("{}: General Order: {}".format(self.get_current_time(),general_order))

                            if general_order.trigger == "general":
                                order_msg.trigger = 0
                                #order_msg.behavior_running = True
                            elif general_order.trigger == "slew_to_cue":
                                order_msg.trigger = 1
                                #order_msg.behavior_running = False

                            order_msg.weapon_control_order = general_order.weapon_control_order
                            order_msg.selected_behavior = general_order.behavior
                            order_msg.select_scan_pattern = general_order.select_scan_pattern
                            # order_msg.set_scan_pattern = general_order.set_scan_pattern

                            order_msg.left_limit = general_order.left_aor
                            order_msg.right_limit = general_order.right_aor
                            order_msg.continuing_order = general_order.continuing_order


                            for scan_point in general_order.create_scan_pattern:
                                # print("{}: Scan Points: {}".format(self.get_current_time(),scan_point))
                                single_scan_pt = single_scan_point()
                                pan, tilt, distance, zoom = self.calc_scan_from_gps(scan_point.pan, scan_point.tilt, scan_point.zoom)
                                single_scan_pt.point_number = scan_point.point_number
                                single_scan_pt.pan = pan
                                single_scan_pt.tilt = tilt
                                single_scan_pt.zoom = zoom

                                scan_msg.scan_point_list.append(single_scan_pt)
                            if len(scan_msg.scan_point_list) > 1:
                                order_msg.set_scan_pattern = 2

                        self.scan_point_pub.publish(scan_msg)


                        if artemis_message.current_order_running == "General":
                            order_msg.behavior_running = True
                        elif artemis_message.current_order_running == "Off":
                            order_msg.behavior_running = False

                        order_msg.source = 9
                        self.order_pub.publish(order_msg)


                else:
                    """
                    Socket to recieve Protobuf message from Athena.
                    """

                    self.recieve_port = int(rospy.get_param("athena_receive_port"))
                    self.athena_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.athena_receive_socket.bind((self.artemis_ip, self.recieve_port))
                    self.athena_receive_socket.setblocking(0)

                    print("Receive protobuf to Athena socket set up")

            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    self.rate.sleep()
                else:
                   print("Athena Interface Recieve Protobuf Socket Error ", err)
                   #sys.exit(1)


    def receive_cot(self):
        """
        Recieves CoT messages from Athena. Interpreted as a Slew to Cue and
        published to Artemis.
        """
        while self.continue_looping == 1:
            data = 0
            try:
                if self.cot_receive_socket != None:
                    data = self.cot_receive_socket.recv(1024)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK or errno.ETIME:
                    self.rate.sleep()
                else:
                    print("Athena Interface Recieve Cot Socket Error ", err)
                    #sys.exit(1)
            if data != 0:
                root = ET.fromstring(data)

                lat = 0
                lon = 0
                alt = 0
                stale_time = datetime.datetime.strptime(root.get('stale'), "%Y-%m-%dT%H:%M:%SZ")
                current_time = datetime.datetime.utcnow()
                if current_time < stale_time:
                    for child in root:
                        if child.get('lat') != None:
                            #print child.get('lat')
                            lat = float(child.get('lat'))
                        if child.get('lon') != None:
                            #print child.get('lon')
                            lon = float(child.get('lon'))
                        if child.get('hae') != None:
                            alt = float(child.get('hae'))

                    if lat != 0 and lon != 0:
                        msg = Point()
                        msg.x = lat
                        msg.y = lon
                        msg.z = alt
                        self.cue_coordinate.publish(msg)

    def update_message(self):
        new_principal_msg = Principal_Athena_Message()

        new_principal_msg.sender_uuid = self.uid_self
        new_principal_msg.message_type = "Status"
        new_principal_msg.destination_id.extend([self.destination_id]) #top level
        time = datetime.datetime.utcnow()
        str_time = time.isoformat()
        new_principal_msg.timestamp_utc_time = str_time

        artemis_msg = Artemis_Message()
        artemis_msg.uuid  = self.uid_self
        artemis_msg.latitude = self.current_gps_lat
        artemis_msg.longitude = self.current_gps_long
        artemis_msg.altitude = self.current_gps_alt
        artemis_msg.heading = self.current_heading
        artemis_msg.fire_fan_left = self.fire_fan_left
        artemis_msg.fire_fan_right = self.fire_fan_right
        artemis_msg.ammo_count = self.ammo_count
        artemis_msg.ptu_pan = self.current_pan_position
        artemis_msg.ptu_tilt = self.current_tilt_position
        artemis_msg.zoom = self.zoom


        arti_go = Artemis_General_Order()
        if self.recent_general_order == None:

            artemis_msg.current_order_running = "Off"

            arti_go.weapon_control_order = 1
            arti_go.behavior = 1
            arti_go.select_scan_pattern = 0
            scn_pt = Scan_Point()
            scn_pt.point_number = 1
            scn_pt.pan = .5
            scn_pt.tilt = .25
            scn_pt.zoom = 1

            arti_go.create_scan_pattern.extend([scn_pt])

            arti_go.left_aor = 0
            arti_go.right_aor = 0
            arti_go.enabled_triggers.extend(['slew_to_cue', 'search', 'manual_slew_to_cue'])

            arti_go.continuing_order = 'general'

            arti_go.action_point.extend([0, 0])


            artemis_msg.orders.extend([arti_go])

        else:
            if self.recent_general_order.behavior_running == True:
                print("recent_general_order.behavior_running", True)
                if self.recent_general_order.trigger == 0:
                    artemis_msg.current_order_running = 'General'
                elif self.recent_general_order.trigger == 1:
                    artemis_msg.current_order_running = 'Slew_To_Cue'
                elif self.recent_general_order.trigger == 2:
                    artemis_msg.current_order_running = 'Search'
                elif self.recent_general_order.trigger == 3:
                    artemis_msg.current_order_running = 'manual_slew_to_cue'
            else:
                artemis_msg.current_order_running = "Off"

            arti_go.weapon_control_order = self.recent_general_order.weapon_control_order + 1
            arti_go.behavior = self.recent_general_order.selected_behavior + 1
            arti_go.select_scan_pattern = self.recent_general_order.select_scan_pattern + 1
            if self.current_scan_pattern != None:
                for scan_point in self.current_scan_pattern.scan_point_list:

                    scn_pt = Scan_Point()
                    scn_pt.point_number = scan_point.point_number
                    scn_pt.pan = scan_point.pan
                    scn_pt.tilt = scan_point.tilt
                    scn_pt.zoom = scan_point.zoom

                    arti_go.create_scan_pattern.extend([scn_pt])

            else:

                scn_pt = Scan_Point()
                scn_pt.point_number = 1
                scn_pt.pan = .5
                scn_pt.tilt = .25
                scn_pt.zoom = 1

                arti_go.create_scan_pattern.extend([scn_pt])


            arti_go.left_aor = 0
            arti_go.right_aor = 0
            arti_go.enabled_triggers.extend(['slew_to_cue', 'search', 'manual_slew_to_cue'])

            arti_go.continuing_order = self.recent_general_order.continuing_order

            arti_go.action_point.extend([0, 0])


            artemis_msg.orders.extend([arti_go])


        new_principal_msg.artemis.extend([artemis_msg])

        self.principal_proto = new_principal_msg

    def athena_ip_callback(self, data):
        self.athena_ip = data.data

    def artemis_id_callback(self, data):
        self.artemis_id = int(data.data)

    def set_auto_engage(self, data):
        self.current_artemis_mode.auto_engage_mode.current_mode = data.data

    def set_auto_target(self, data):
        self.current_artemis_mode.auto_target_auth = data.data

    def set_auto_scan(self, data):
        self.current_artemis_mode.auto_scan_auth = data.data

    def rws_mode_callback(self, data):
        self.current_artemis_mode.rws_mode = data.data

    def slew_to_cue_mode_callback(self, data):
        self.current_artemis_mode.slew_to_cue_mode.current_mode = data.data

    def position_callback(self, data):
        self.current_pan_position = data.point.x
        self.current_tilt_position = data.point.y

    def target_list_callback(self, data):
        self.current_target_list = data
        for track in data.contact_group:

            if track.selected:
                self.target_id = track.id

    def athena_auth_callback(self, data):
        self.current_artemis_mode.athena_auth = data.data

    def lrf_data_callback(self, data):
        back_heading = self.current_heading
        if back_heading < 0:
            back_heading = 360 + back_heading

        adjusted_heading = 0
        if(back_heading > 180):
            adjusted_heading = 360 - back_heading
        else:
            adjusted_heading = (-1) * back_heading

        #This probably gives heading...provided correct heading
        brng = (math.pi/180) * ((self.current_pan_position * 360) + back_heading + adjusted_heading)

        if brng > (2*math.pi):
            brng = brng - 2*math.pi


        #For t_heading of 335, pan position of 0.5 / 180 degrees, bearing should be around 160
        if data.data > 65000:
            d = 0.0
        else:
            d = data.data/1000 #take lrf reading in meters, conver to KM
        R = 6378.1   #radius of the earth
        lat1 = self.current_gps_lat * (math.pi/180)
        lon1 = self.current_gps_long * (math.pi/180)

        lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng))
        lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1),math.cos(d/R)-math.sin(lat1)*math.sin(lat2))

        lat2 = lat2*(180/math.pi)
        lon2 = lon2*(180/math.pi)

        hypot = data.data/100000
        try:
            altitude = math.cos(self.current_tilt_position*360)/hypot
        except ZeroDivisionError:
            altitude = 0



        uid = self.uid_target + str(self.selected_track_id)
        self.target_id += 1
        if self.recent_general_order.behavior_running == True:
            type = self.unknown_type
        else:
            type = self.hostile_type
        cot_msg = self.create_cot_message(uid, lat2, lon2, type, altitude)
        #cot_msg = tostring(cot_msg)100000

        self.cot_to_send = cot_msg
        #self.athena_send_cot_socket.sendto(cot_msg, (self.athena_ip, self.cot_port))

        self.reported_target_pub.publish(self.selected_track_id)

        if(self.last_data != data.data):
            self.UTM_coordinate = self.calculate_UTM(lat2, lon2)
            self.utm_coord_pub.publish(self.UTM_coordinate)
            self.last_data = data.data


    def calculate_UTM(self, lat, lon):
        m = mgrs.MGRS()

        UTM_str = m.toMGRS(lat, lon)


        str_len = len(UTM_str)
        GZD = UTM_str[0: str_len - 12]
        SQI = UTM_str[str_len - 12: str_len - 10]
        easting = UTM_str[str_len - 10:str_len - 5]
        northing = UTM_str[str_len - 5:str_len]

        return GZD + " " + SQI + " " + easting + " " + northing




    def update_gps_callback(self, data):
        self.current_gps_lat = data.latitude
        self.current_gps_long = data.longitude
        self.current_gps_alt = data.altitude

    def update_heading_callback(self, data):
        self.current_heading = data.data

    def selected_track_callback(self, data):
        self.selected_track_id = data.data

    def client_connected_callback(self, data):
        """
        Socket for ACU GUI.
        """
        self.gui_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        splt_string = data.data.split(":")
        self.gui_ip = splt_string[0]
        self.gui_port = int(rospy.get_param("gui_port"))
        self.send_sockets.append([self.gui_socket, self.gui_ip, self.gui_port, "GUI"])

    def client_disconnected_callback(self, data):
        """
        Disconeect socket for RAVN GUI.
        """
        for socket in range(len(self.send_sockets)):
            if self.send_sockets[socket][1] == data.data and self.send_sockets[socket][3]=="GUI":
                self.send_sockets.pop(socket)
                break

    def general_order_callback(self, data):
        self.recent_general_order = data

    def explict_set_scan_points_callback(self, scan_points_msg):
        self.current_scan_pattern = scan_points_msg

    def fov_callback(self, msg):
        self.zoom = msg.data

    def publish_updates(self, message):
        pass


    def create_cot_message(self, uid, lat, log, u_type, altitude):

        """
        Creates CoT Message

        Args:
            uid : CoT formated UID
            lat : latitude
            log : longitude
            u_type : CoT formated type
        """
        try:
            msg_obj = tak_cot_sdk.TakCotAtom(lat, log, uid_num = uid, e_type=u_type, stale_offset_seconds=10, hae=altitude)
            message = msg_obj.gen_cot_msg()
            return message
        except Exception as error:
            print("{} Error in create cot message".format(error))


    def calc_scan_from_gps(self, targetLat,targetLong,targetAlt):
        baseLat = self.current_gps_lat
        baseLong = self.current_gps_long
        baseAlt = self.current_gps_alt
        baseHeading = self.current_heading
        #baseLat = 3.0
        #baseLong = 3.0
        #baseAlt = 2.0
        basePitch = 0 #/= 57.296
        baseRoll = 0 #/= 57.296
        baseHeading /= 57.296 #convert to rad

        # constants
        r = 6.371 * pow(10,6) #radius of Earth
        k1 = r / 57.296
        k2 = r / 57.296 * math.cos(baseLat/57.296)

        targetVector_NED = np.array([[k1*(targetLat-baseLat)],
        			[k2*(targetLong-baseLong)],
        			[-1*(targetAlt-baseAlt)],
        			[1.0]])

        # tf from north-east-down to front-right-down
        tfNED2BaseFRD = np.array([[math.cos(baseHeading), math.sin(baseHeading), 0.0, 0.0],
        			[-math.sin(baseHeading), math.cos(baseHeading), 0.0, 0.0],
        			[0.0, 0.0, 1.0, 0.0],
        			[0.0, 0.0, 0.0, 1.0]])

        # tf base FRD to front-up-right
        tfBaseFRD2BaseFUR = np.array([[1.0, 0.0, 0.0, 0.0],
        				[0.0, 0.0, -1.0, 0.0],
        				[0.0, 1.0, 0.0, 0.0],
        				[0.0, 0.0, 0.0, 1.0]])

        cp = math.cos(basePitch)
        sp = math.sin(basePitch)
        cr = math.cos(baseRoll)
        sr = math.sin(baseRoll)

        # tf front-up-right to front-up-right with pitch and roll
        tfBaseFUR2BodyFUR = np.array([[cp, sp, 0, 0],
        				[-sp*cr, cp*cr, sr, 0],
        				[sp*sr, -cp*sr, cr, 0],
        				[0, 0, 0, 1.0]])



        targetVector_BodyFUR = tfBaseFUR2BodyFUR.dot(tfBaseFRD2BaseFUR).dot(tfNED2BaseFRD).dot(targetVector_NED)


        panFraction = math.atan2(targetVector_BodyFUR[2,0],
        			targetVector_BodyFUR[0,0]) / (2*np.pi) + 0.5
        #tiltFraction = math.atan2(targetVector_BodyFUR[1,0],
        #			math.sqrt(pow(targetVector_BodyFUR[0,0],2)+pow(targetVector_BodyFUR[2,0],2))) / (2.0/3.0*np.pi) +.25
        tiltFraction = .25

        # Calculate Distance - Haversine formula
        R = 6373.0
        latBase = math.radians(baseLat)
        lonBase = math.radians(baseLong)

        latTarget = math.radians(targetLat)
        lonTarget = math.radians(targetLong)

        dlon = lonTarget - lonBase
        dlat = latTarget - latBase

        a = math.sin(dlat / 2)**2 + math.cos(latBase) * math.cos(latTarget) * math.sin(dlon / 2) **2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        #Zoom lookup will relate (range, zoom_level), search the list until range > actual range
        zoom_lookup = {(10, 0),(25, 1),(50, 2),(100, 3),(150,4),(200,5),(250,6)}
        zoom_level = 0
        for item in zoom_lookup:
            if item[0] > distance:
                zoom_level = item[1]
                break

        return panFraction, tiltFraction, distance, zoom_level

if __name__ == '__main__':
    # Create Node
    rospy.init_node('athena_interface_node')
    node = AthenaInterfaceNode()

    # Start Context Manager
    with node as running_node:
        while not rospy.is_shutdown():
            try:
                rospy.spin()
            except KeyboardInterrupt:
                rospy.logdebug('Keyboard Interrupt')
