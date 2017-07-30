import sys
import json
import mmap
from xml.dom import minidom

from Evtx.Evtx import FileHeader
import Evtx.Views


def toXml(dom):
    """
    Print xml to console
    return: None
    """
    h_out = "<xml version='1.0' encoding='utf-8' standalone='yes' ?><Events>"
    print(h_out)
    print(dom.toprettyxml())
    print("</Events.")


def getEventData(xmlDom):

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


def getSysStruct(dom):
    # Windows Event Properties.
    # This current structure applies to Win7, Win Server 2008/r2, & Vista
    # Varies with Win 8, Win 10, & newer versions. ** Research this **.

    guid = dom.getElementsByTagName("Provider")[0].attributes["Guid"].value
    pname = dom.getElementsByTagName("Provider")[0].attributes["Name"].value
    evtID = dom.getElementsByTagName("EventID")[0].childNodes[0].nodeValue
    version = dom.getElementsByTagName("Version")[0].childNodes[0].nodeValue
    level = dom.getElementsByTagName("Level")[0].childNodes[0].nodeValue
    task = dom.getElementsByTagName("Task")[0].childNodes[0].nodeValue
    opCode = dom.getElementsByTagName("Opcode")[0].childNodes[0].nodeValue
    keywords = dom.getElementsByTagName("Keywords")[0].childNodes[0].nodeValue
    timeCreated = dom.getElementsByTagName("TimeCreated")[0].attributes["SystemTime"].value
    eventRecID = dom.getElementsByTagName("EventRecordID")[0].childNodes[0].nodeValue
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
                        "ProvideName": pname,
                        "EventID": evtID,
                        "Version": version,
                        "Level": level,
                        "Task": task,
                        "OpCode": opCode,
                        "Keywords": keywords,
                        "TimeCreate": timeCreated,
                        "EventRecordID": eventRecID,
                        "ProcessID": {"type": "string"},
                        "ThreadID": {"type": "string"},
                        "Channel": channel,
                        "Computer": computer,
                        "UserID": security
                    },
                    "EventData": getEventData(dom)
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
            xmlDom = minidom.parseString(strxml.replace('\n', ''))

            # get System node names and values
            getSysStruct(xmlDom)

            break

        buffer.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupt by Crtl-C")
        sys.stderr.flush()