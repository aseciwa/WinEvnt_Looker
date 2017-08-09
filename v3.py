"""
Windows Event Parser
Parses windows event logs and stores data in an ElasticSearch mapping.
Version: 1.0
@author Alan Seciwa
"""
import sys
import mmap

from xml.dom import minidom

from Evtx.Evtx import FileHeader
import Evtx.Views

# look out for <UserData><EventXML></EventXML></UserData>


def get_data(xml_dom, cnodes):

    for n in cnodes:

        # example: Parent -> <System>
        #              ChildNodes -> <Provider>, <EventID>, <Version>, etc.
        # n = Provider

        # check if tag is there
        if xml_dom.getElementsByTagName(n):

            # check if tag (i.e. Provider) has Attributes
            # if it has attributes: returns dict_keys([n, n+1])
            # it NOT: returns dict_keys([]) -- This is empty
            #
            # Example: dict_keys(["Guid", "Name", "EventSourceName"])
            e = xml_dom.getElementsByTagName(n)[0].attributes.keys()

            #print(e)

            # Convert dict_keys() to List
            attr = list(e)
            count = 0

            if len(attr) is not 0:

                for i in attr:
                    a = xml_dom.getElementsByTagName(n)[0].attributes[i].value
                    #print(a)
                    print("Element: " + n + " --- Attribute: "+ str(attr[count] + " ---- Value: " + a))
                    count += 1

    print("\n --------------------- \n")
    #sys.exit(1)


def get_sysTag(xml_dom, n_list):

    # Loop through child nodes of Event
    # example: <System> , <EventData>, <UserData>
    for type in n_list:
        print('--->'+type)

        # get child node tag
        elem = xml_dom.getElementsByTagName(type)

        # list stores elem's Child Nodes
        e_cnodes = []

        # Now loop through childNodes of elem
        for item in elem[0].childNodes:
            try:
                # append all Child nodes of elem
                # example: Parent -> <System>
                #              ChildNodes -> <Provider>, <EventID>, <Version>, etc.
                e_cnodes.append(item.nodeName)
            except TypeError:
                raise "TypeError"

        get_data(xml_dom, e_cnodes)



def main():
    u = set()

    with open('System.evtx', 'r') as file_:

        buffer = mmap.mmap(file_.fileno(), 0, access=mmap.ACCESS_READ)
        fh = FileHeader(buffer, 0x00)

        # record holds offset of file. This is a throwaway variable (__)
        for strxml, record in Evtx.Views.evtx_file_xml_view(fh):

            xml_dom = minidom.parseString(strxml.replace('\n', ''))

            # Get root node. All event logs start with an Event tag aka root.
            event = xml_dom.getElementsByTagName("Event")

            if event:
                # list to store all child nodes of Event
                name = []

                for item in event[0].childNodes:
                    #u.add(item.nodeName)
                    name.append(item.nodeName)

            get_sysTag(xml_dom, name)


        #print(u)
            #break
        buffer.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupt by Crtl-C")
        sys.stderr.flush()