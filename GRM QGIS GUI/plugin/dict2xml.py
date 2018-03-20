# -*- coding: utf-8 -*-
from minidom import Document
import copy


class dict2xml(object):
    doc = Document()
    def __init__(self, structure):
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)
            self.doc.toprettyxml(indent="  ")
            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = self.doc.createElement(tagName)
                self.build(tag, l)
                grandFather.appendChild(tag)

        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)

    def display(self):
        test = self.doc.toprettyxml(indent="  ")
        return test

    # # Xml 딕셔너리로 주는거 같은데
    # def dictify(r, root=True):
    #     if root:
    #         return {r.tag: dictify(r, False)}
    #     d = copy(r.attrib)
    #     if r.text:
    #         d["_text"] = r.text
    #     for x in r.findall("./*"):
    #         if x.tag not in d:
    #             d[x.tag] = []
    #         d[x.tag].append(dictify(x, False))
    #     return d