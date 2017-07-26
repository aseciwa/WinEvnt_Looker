import mmap
from xml.dom import minidom

from Evtx.Evtx import FileHeader
import Evtx.Views


def main():

    with open('Security.evtx', 'r') as file_:
        buffer = mmap.mmap(file_.fileno(), 0, access=mmap.ACCESS_READ)
        fh = FileHeader(buffer, 0x00)

        h_out = "<xml version='1.0' encoding='utf-8' standalone='yes' ?><Events>"

        print(h_out)

        for strxml, record in Evtx.Views.evtx_file_xml_view(fh):
            xmlDoc = minidom.parseString(strxml.replace('\n', ''))
            evtId = xmlDoc.getElementsByTagName("EventID")[0].childNodes[0].nodeValue

            if evtId == '4688':
                print(xmlDoc.toprettyxml())

        buffer.close()
        endTag = "</Events>"


if __name__ == "__main__":
    main()