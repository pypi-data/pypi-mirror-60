# -*- mode: python; coding: utf-8 -*-
# Copyright 2019 the .NET Foundation
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

__all__ = '''
indent_xml
write_xml_doc
stringify_xml_doc
'''.split()

from xml.etree import ElementTree as etree

def indent_xml(elem, level=0):
    """A dumb XML indenter.

    We create XML files using xml.etree.ElementTree, which is careful about
    spacing and so by default creates ugly files with no linewraps or
    indentation. This function is copied from `ElementLib
    <http://effbot.org/zone/element-lib.htm#prettyprint>`_ and implements
    basic, sensible indentation using "tail" text.

    """
    i = "\n" + level * "  "

    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:  # intentionally updating "elem" here!
            indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def write_xml_doc(root_element, indent=True, dest_stream=None, dest_wants_bytes=False):
    """Write out some XML elements, indenting them by default

    When *indent* is true, the default setting, this function modifies *root_element*.

    If *dest_stream* is left unspecified, ``sys.stdout`` is used.

    """
    if dest_stream is None:
        import sys
        dest_stream = sys.stdout

    if indent:
        indent_xml(root_element)

    doc = etree.ElementTree(root_element)

    # We could in principle auto-detect this with a 0-byte write(), I guess?
    if dest_wants_bytes:
        encoding = 'UTF-8'
    else:
        encoding = 'Unicode'

    doc.write(dest_stream, encoding=encoding, xml_declaration=True)


def stringify_xml_doc(root_element, indent=True):
    """Stringify some XML elements, indenting them by default.

    When *indent* is true, the default setting, this function modifies *root_element*.

    """
    from io import StringIO
    with StringIO() as dest:
        write_xml_doc(root_element, indent, dest, dest_wants_bytes=False)
        result = dest.getvalue()
    return result
