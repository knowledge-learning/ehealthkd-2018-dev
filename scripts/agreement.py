# coding: utf8

import click
import random


class AnnotationElement:
    def __init__(self, description, **kwargs):
        self.description = description

        for k,v in kwargs.items():
            setattr(self, k, v)


class Annotation:
    def __init__(self, annotation_line, parent):
        self.parent = parent
        line = annotation_line.strip().split("\t")
        self.id = line[0]
        self.args = line[1].split()
        self.text = line[2] if len(line) == 3 else ""
        self.type = dict(T='Token', R='Relation', E='Event', A='Attribute')[self.id[0]]

        if self.type == 'Token':
            self.label = self.args[0]
            self._start = int(self.args[1])
            self._end = int(self.args[2])

        elif self.type == 'Relation':
            self.label = self.args[0]
            self._start = self.args[1].split(":")[1]
            self._end = self.args[2].split(":")[1]

        elif self.type == 'Event':
            self._entity = self.args[0].split(':')[1]
            self._arguments = { k[0]:k[1] for k in
                               [a.split(':') for a in self.args[1:]] }

        elif self.type == 'Attribute':
            self.label = self.args[0]
            self._entity = self.args[1]

    @property
    def arguments(self):
        return { key: self.parent.find(value) for key, value in self._arguments.items() }

    @property
    def start(self):
        if isinstance(self._start, int):
            return self._start

        return self.parent.find(self._start)

    @property
    def end(self):
        if isinstance(self._end, int):
            return self._end

        return self.parent.find(self._end)

    @property
    def entity(self):
        return self.parent.find(self._entity)

    def eqv(self, other):
        if other is None:
            return False

        if self.type != other.type:
            return False

        if self.type == 'Token':
            return self.start == other.start and \
                   self.end == other.end

        elif self.type == 'Relation':
            return self.start.eqv(other.start) and \
                   self.end.eqv(other.end)

        elif self.type == 'Event':
            return self.entity.eqv(other.entity)

        elif self.type == 'Attribute':
            return self.entity.eqv(other.entity)

        return False

    def __repr__(self):
        if self.type == 'Token':
            return "<Token (%s), label=%s, start=%i, end=%i, text='%s'>" % \
                   (self.id, self.label, self.start, self.end, self.text)

        if self.type == 'Relation':
            return "<Relation (%s), label=%s, start=%s, end=%s>" % \
                   (self.id, self.label, self.start.id, self.end.id)

        if self.type == 'Event':
            return "<Event (%s), entity=%s, args=[%s]>" % \
                   (self.id, self.entity.id, ", ".join("%s: %s" % (k,v.id) for k,v in self.arguments.items()))

        if self.type == 'Attribute':
            return "<Attribute (%s), label=%s, entity=%s>" % \
                   (self.id, self.label, self.entity.id)


class AnnotationSet:
    def __init__(self, annotations):
        self.items = [self._make_item(ann) for ann in annotations]
        self._ids = {i.id: i for i in self.items}

    def _make_item(self, ann):
        if isinstance(ann, str):
            return Annotation(ann, self)

        if isinstance(ann, Annotation):
            return ann

    def __contains__(self, item):
        return self.find(item) is not None

    def __iter__(self):
        return iter(self.items)

    def find_eqv(self, item):
        for i in self.items:
            if item.eqv(i):
                return i

        return None

    def find(self, item):
        if isinstance(item, Annotation):
            for i in self.items:
                if i == item:
                    return i
            else:
                return None

        return self._ids.get(item, None)

    @staticmethod
    def compare(*anotations):
        comparison = []
        used = set()

        for ann in anotations:
            others = [a for a in anotations if a != ann]
            comparison.extend(AnnotationSet.compare_one(ann, *others, used=used))

        return comparison

    @staticmethod
    def compare_one(ann, *others, used=None):
        if not used:
            used = set()

        # print(others)

        for item in ann:
            if item in used:
                continue

            eqvs = [item] + [other.find_eqv(item) for other in others]


        return []

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "\n".join(str(i) for i in self.items)


def compute_kappa(text, annotations):
    print(len(annotations))

    annotations = [AnnotationSet(ann) for ann in annotations]
    comparison = AnnotationSet.compare(*annotations)

    print(comparison)


@click.command()
@click.argument('text_file', type=click.File('r'))
@click.argument('ann_files', nargs=-1, type=click.File('r'))
def main(text_file, ann_files):
    text = text_file.read()
    annotations = [f.readlines() for f in ann_files]

    text_file.close()
    for ann_file in ann_files:
        ann_file.close()

    compute_kappa(text, annotations)
