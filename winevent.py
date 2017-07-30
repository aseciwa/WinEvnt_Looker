"""
Windows Event Parser
Parses windows event logs and stores data in an ElasticSearch mapping.
Version: 1.0
@author Alan Seciwa
"""
import sys
import json
import mmap
from xml.dom import minidom

from Evtx.Evtx import FileHeader
import Evtx.Views

# TODO Test on other Windows Event logs (e.g. Application, Setup, etc.)
# TODO Categorize events based on EventID
# TODO Create a class
# TODO Use Argparse for command-line options


def to_xml(dom):
    """
    Print xml to console
    return: None
    """
    h_out = "<xml version='1.0' encoding='utf-8' standalone='yes' ?><Events>"
    print(h_out)
    print(dom.toprettyxml())
    print("</Events.")


def get_event_data(xmlDom):
    """
    Method loops through the Data childnodes to gather node names and
    node values.
    :param xmlDom: xml dom object
    :return: parsed event data in dictionary format
    """

    # holder for event data
    data = {}

    # get the number of subnodes in parent node
    len_ = xmlDom.getElementsByTagName("Data").length

    # loop through number of nodes
    for i in range(len_):

        # returns a tuple -> (Attribute Name, NodeValue)
        # throwaway AttributeName: not needed
        __, attriTag = xmlDom.getElementsByTagName("Data")[i].attributes.items()[0]

        # Some nodes do NOT have any values so catch the IndexError and handle
        # it by assigning attriValue with a tack (-).
        try:
            attriValue = xmlDom.getElementsByTagName("Data")[i].childNodes[0].data
        except IndexError:
            attriValue = "-"

        # append all values to dictionary
        data[attriTag] = attriValue

    return data


def get_sys_data(dom):
    """
    Retrieves System nodes and values
    :param dom: xml dom object
    :return: elasticsearch mapping object
    """
    # Windows Event Properties.
    # This current structure applies to Win7, Win Server 2008/r2, & Vista
    # Varies with Win 8, Win 10, & newer versions. ** Research this **.

    guid = dom.getElementsByTagName("Provider")[0].attributes["Guid"].value
    prov_name = dom.getElementsByTagName("Provider")[0].attributes["Name"].value
    evt_id = dom.getElementsByTagName("EventID")[0].childNodes[0].nodeValue
    version = dom.getElementsByTagName("Version")[0].childNodes[0].nodeValue
    level = dom.getElementsByTagName("Level")[0].childNodes[0].nodeValue
    task = dom.getElementsByTagName("Task")[0].childNodes[0].nodeValue
    op_code = dom.getElementsByTagName("Opcode")[0].childNodes[0].nodeValue
    keywords = dom.getElementsByTagName("Keywords")[0].childNodes[0].nodeValue
    time_created = dom.getElementsByTagName("TimeCreated")[0].attributes["SystemTime"].value
    event_rec_id = dom.getElementsByTagName("EventRecordID")[0].childNodes[0].nodeValue
    channel = dom.getElementsByTagName("Channel")[0].childNodes[0].nodeValue
    # correlation -> ActivityID & RelatedActivityID
    # Execution -> ProcessID & ThreadID
    computer = dom.getElementsByTagName("Computer")[0].childNodes[0].nodeValue
    security = dom.getElementsByTagName("Security")[0].attributes["UserID"].value

    jsObj = {
        "mappings": {
            "properties": {
                "Event": {
                    "System": {
                        "Guid": guid,
                        "ProvideName": prov_name,
                        "EventID": evt_id,
                        "Version": version,
                        "Level": level,
                        "Task": task,
                        "OpCode": op_code,
                        "Keywords": keywords,
                        "TimeCreate": time_created,
                        "EventRecordID": event_rec_id,
                        "ProcessID": {"type": "string"},
                        "ThreadID": {"type": "string"},
                        "Channel": channel,
                        "Computer": computer,
                        "UserID": security
                    },
                    "EventData": get_event_data(dom)
                }
            }
        }
    }

    print(json.dumps(jsObj))


def main():

    with open('Security.evtx', 'r') as file_:

        # memory map the file to improve I/O performances to avoid a separate system
        # call for each access and does not require copying data between buffers.
        # use "with contextlib.closing() as m" statement for opening and closing file w/mmap
        # TODO Create try-except in case the file is empty (Windows will raise an exception).
        # TODO Cannot create empty mapping on Windows. Unix will be fine.
        buffer = mmap.mmap(file_.fileno(), 0, access=mmap.ACCESS_READ)
        fh = FileHeader(buffer, 0x00)

        # record holds offset of file. This is a throwaway variable (__)
        for strxml, record in Evtx.Views.evtx_file_xml_view(fh):
            xml_dom = minidom.parseString(strxml.replace('\n', ''))

            # get System node names and values
            get_sys_data(xml_dom)

        buffer.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupt by Crtl-C")
        sys.stderr.flush()