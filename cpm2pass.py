import os
import gzip
import argparse
import subprocess
from lxml import etree
from cStringIO import StringIO


class Password(object):
    def __init__(self, host, service, user, passwd):
        self.host = host
        self.service = service
        self.user = user
        self.passwd = passwd
        
    def __repr__(self):
        return "Pass for: /" + "/".join([self.host,
                                         self.service,
                                         self.user])


def read_passwords(filename):
    path = os.path.abspath(os.path.expanduser(filename))
    proc = subprocess.Popen(['gpg','-d', path],stdout=subprocess.PIPE)
    assert 0 == proc.wait()
    compressed = proc.stdout.read()
    gzip_stream = gzip.GzipFile("", mode="r", fileobj=StringIO(compressed))

    return etree.parse(gzip_stream)


def iter_passwords(document):
    root = document.getroot()
    for host in root.iterfind("./node"):
        for service in host.iterfind("./node"):
            for user in service.iterfind("./node"):
                for passwd in service.iterfind("./node"):
                    yield Password(host.attrib["label"],
                                   service.attrib["label"],
                                   user.attrib["label"],
                                   passwd.attrib["label"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", required=True, help="input file")

    args = parser.parse_args()

    doc = read_passwords(args.infile)
    for pw in iter_passwords(doc):
        print pw
