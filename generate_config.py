import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("AthenaSender")
# ADD SETTINGS TO SECTION
config_file.set("AthenaSender", "ipAddress", "\"192.168.10.37\"")
config_file.set("AthenaSender", "port", "\"11130\"")
# ADD SECTION
config_file.add_section("ArthemisSender")
# ADD SETTINGS TO SECTION
config_file.set("ArthemisSender", "ipAddress", "\"10.1.0.60\"")
config_file.set("ArthemisSender", "port", "\"11130\"")
# ADD SECTION
config_file.add_section("AthenaStatus")
# ADD SETTINGS TO SECTION
config_file.set("AthenaStatus", "ipAddress", "\"172.16.18.7\"")
config_file.set("AthenaStatus", "port", "\"11130\"")
# ADD SECTION
config_file.add_section("AthenaReceiverLocal")
# ADD SETTINGS TO SECTION
config_file.set("AthenaReceiverLocal", "ipAddress", "\"172.16.18.7\"")
config_file.set("AthenaReceiverLocal", "port", "\"11130\"")
# ADD SECTION
config_file.add_section("AthenaDetections")
# ADD SETTINGS TO SECTION
config_file.set("AthenaDetections", "ipAddress", "\"172.16.18.7\"")
config_file.set("AthenaDetections", "port", "\"11130\"")
# ADD SECTION
config_file.add_section("soi")
# ADD SETTINGS TO SECTION
config_file.set("soi", "ipAddress", "\"172.16.18.7\"")
config_file.set("soi", "port", "\"11130\"")

config_file.add_section("vc")
# ADD SETTINGS TO SECTION
config_file.set("vc", "simPlatform", "\"IRL\"")
config_file.set("vc", "side", "\"blue\"")
config_file.set("vc", "unitName", "\"msrugv_1\"")
config_file.set("vc", "waypointType", "\"longlat\"")

config_file.add_section("soi")
config_file.set("soi", "assetName", "\"SEI_1\"")



# SAVE CONFIG FILE
with open(r"configurations.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'configurations.ini' created")

# PRINT FILE CONTENT
read_file = open("configurations.ini", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()