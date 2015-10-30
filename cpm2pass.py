import os
import gzip
import argparse
import subprocess
from lxml import etree
from itertools import chain
from cStringIO import StringIO


class Password(object):
    def __init__(self, path, passwd):
        self.path = path
        self.passwd = passwd
        
    def __repr__(self):
        return "Pass for: /" + "/".join(self.path)


def cpm_stream(filename):
    path = os.path.abspath(os.path.expanduser(filename))
    proc = subprocess.Popen(['gpg','-d', path],stdout=subprocess.PIPE)
    assert 0 == proc.wait()
    compressed = proc.stdout.read()
    return gzip.GzipFile("", mode="r", fileobj=StringIO(compressed))


def read_passwords(filename, ftype):
    if ftype == "cpm":
        gzip_stream = cpm_stream(filename)
    else:
        gzip_stream = open(filename, "r")
    return etree.parse(gzip_stream)


def iter_subnodes(node, path):
    if node.find("./node") is not None:
        path = path + [node.attrib["label"]]
        return chain.from_iterable((
            iter_subnodes(n, path) for n in node.iterfind("./node")))
    else:
        return [Password(path, node.attrib["label"])]


def iter_passwords(document):
    root = document.getroot()
    return chain.from_iterable(
            (iter_subnodes(node, []) for node in root.iterfind("./node")))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", required=True,
                        help="input file")
    parser.add_argument("-t", "--type", required=False, choices=("cpm", "plain"),
                        help="cpm file type (for debugging)", default="cpm")

    args = parser.parse_args()

    doc = read_passwords(args.infile, args.type)
    for pw in iter_passwords(doc):
        print pw
