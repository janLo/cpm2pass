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
        return u"Pass for: " + self.pretty_path()

    def pretty_path(self):
        return u"/" + "/".join(self.path)

    def full_repr(self):
        return u"%s -> '%s'" % (repr(self), self.passwd)


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


def fix_password(password):
    while True:
        print "Modify pass for '%s':" % password.pretty_path()
        action = raw_input(("(s) skip,\n"
                            "(e) edit,\n"
                            "(p) edit part,\n"
                            "(d) delete part,\n"
                            "(c) continue\n"))

        if action == "s":
            return None
        elif action == "e":
            path = raw_input(u"Enter new path: ")
            if len(path):
                password.path = path.strip("/").split("/")
                return password
        elif action == "p":
            part = raw_input("select part (1 - %d): " % len(password.path))
            part = int(part)
            if 0 < part <= len(password.path):
                newpart = raw_input("replace '%s': " % password.path[part - 1])
                if len(newpart):
                    password.path[part - 1] = newpart
        elif action == "d":
            part = raw_input("select part (1 - %d): " % len(password.path))
            part = int(part)
            if 0 < part <= len(password.path):
                del password.path[part - 1]
        elif action == "c":
            return password



def prefix_passwd(passwd, prefix):
    passwd.path = prefix + passwd.path
    return passwd


def import_entry(passwd):
    print "IMPORT %s ... " % passwd.pretty_path,
    proc = subprocess.Popen(['pass', 'insert', '--multiline', '--force',
                             passwd.pretty_path],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(passwd.passwd.encode('utf8'))
    proc.wait()
    print "Done."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", required=True,
                        help="input file")
    parser.add_argument("-t", "--type", required=False, choices=("cpm", "plain"),
                        help="cpm file type (for debugging)", default="cpm")
    parser.add_argument("-m", "--method", required=True,
                        choices=("simple", "manual"),
                        help="choose which method to use to create pass entries")
    parser.add_argument("-p", "--prefix", required=False,
                        help="add a prefix to all entries")

    args = parser.parse_args()

    doc = read_passwords(args.infile, args.type)

    passwds = iter_passwords(doc)

    if "prefix" in args and args.prefix is not None:
        prefix = args.prefix.strip("/").split("/")
        passwds = (prefix_passwd(pwd, prefix) for pwd in passwds)
    if args.method == "manual":
        passwds = (fix_password(pwd) for pwd in passwds)

    passwds = (pwd for pwd in passwds if pwd is not None)

    for pw in passwds:
        import_entry(pw)
