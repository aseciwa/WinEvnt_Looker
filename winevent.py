import sys
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
            xmlDom = minidom.parseString(strxml.replace('\n', ''))
            evtID = xmlDom.getElementsByTagName("EventID")[0].childNodes[0].nodeValue

            len_ = xmlDom.getElementsByTagName("Data").length

            if evtID == "4907":
                for i in range(len_):
                    _ , attriValue = xmlDom.getElementsByTagName("Data")[i].attributes.items()[0]
                    try:
                        x = xmlDom.getElementsByTagName("Data")[i].childNodes[0].data
                    except IndexError:
                        x = "-"
                    print(attriValue)
                    print(x)
                break

        buffer.close()
        endTag = "</Events>"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupt by Crtl-C")
        sys.stderr.flush()