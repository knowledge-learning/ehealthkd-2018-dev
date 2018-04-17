# coding: utf8

import fire
import typing


class Annotation:
    def solve_references(self, annotations):
        return

    def assign_annotations(self, sentences):
        return True


class EntityAnnotation(Annotation):
    def __init__(self, id:str, type:str, offsets:typing.Tuple[int,int], text:str):
        self.id = id
        self.type = type
        self.global_offsets = offsets
        self.text = text
        self.sentence = None

    def __repr__(self):
        return f"EntityAnnotation({self.id}, {self.type}, {self.global_offsets}, {self.text})"

    def assign_annotations(self, sentences):
        for s in sentences:
            start, end = self.global_offsets

            if start >= s.offset and end < s.offset + len(s):
                s.annotations.append(self)
                self.local_offsets = (start - s.offset, end - s.offset)
                self.sentence = s

                return True

        return False


class RelationAnnotation(Annotation):
    def __init__(self, id:str, type:str, args:typing.Mapping[str,str]):
        self.id = id
        self.type = type
        self.args = args
        self.sentence = None

    def solve_references(self, annotations:typing.Mapping[str,Annotation]):
        ref_args = {}

        for type, ref in self.args.items():
            ref_args[type] = annotations[ref]

        self.ref_args = ref_args

    def __repr__(self):
        return f"RelationAnnotation({self.id}, {self.type}, {self.args})"

    def assign_annotations(self, sentences):
        possible_sentences = set()

        for arg in self.ref_args.values():
            if not arg.sentence:
                return False

            possible_sentences.add(arg.sentence)

        if len(possible_sentences) > 1:
            raise ValueError("Args belong to different sentences.")

        if len(possible_sentences) == 1:
            self.sentence = possible_sentences.pop()
            self.sentence.annotations.append(self)
            return True

        return False


class AttributeAnnotation(Annotation):
    def __init__(self, id:str, type:str, ref:str):
        self.id = id
        self.type = type
        self.ref = ref
        self.sentence = None

    def solve_references(self, annotations:typing.Mapping[str,Annotation]):
        self.ref_ref = annotations[self.ref]

    def assign_annotations(self, sentences):
        if not self.ref_ref.sentence:
            return False

        self.sentence = self.ref_ref.sentence
        self.sentence.annotations.append(self)

        return True

    def __repr__(self):
        return f"AttributeAnnotation({self.id}, {self.type}, {self.ref})"


class EventAnnotation(Annotation):
    def __init__(self, id:str, args:typing.Mapping[str,str]):
        self.id = id
        self.args = args
        self.sentence = None

    def solve_references(self, annotations:typing.Mapping[str,Annotation]):
        ref_args = {}

        for type, ref in self.args.items():
            ref_args[type] = annotations[ref]

        self.ref_args = ref_args

    def assign_annotations(self, sentences):
        possible_sentences = set()

        for arg in self.ref_args.values():
            if not arg.sentence:
                return False

            possible_sentences.add(arg.sentence)

        if len(possible_sentences) > 1:
            raise ValueError("Args belong to different sentences.")

        if len(possible_sentences) == 1:
            self.sentence = possible_sentences.pop()
            self.sentence.annotations.append(self)
            return True

        return False

    def __repr__(self):
        return f"EventAnnotation({self.id}, {self.args})"


class Sentence:
    def __init__(self, text:str):
        self.text = text
        self.annotations = []
        self.offset = None

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return f"Sentence({repr(self.text)})"


class AnnotationSet:
    def __init__(self, annotations:typing.List[Annotation], sentences=typing.List[str]):
        self.annotations = { ann.id: ann for ann in annotations }
        self.sentences = [Sentence(s) for s in sentences]

        self.offset_sentences()
        self.solve_references()
        self.assign_annotations()

    def __iter__(self):
        return iter(self.annotations)

    def solve_references(self):
        for ann in self.annotations.values():
            ann.solve_references(self.annotations)

    def offset_sentences(self):
        l = 0

        for s in self.sentences:
            s.offset = l
            l += len(s)

    def assign_annotations(self):
        todo = list(self.annotations.values())

        while todo:
            ann = todo.pop(0)

            if not ann.assign_annotations(self.sentences):
                todo.append(ann)


def parse_ann(filename:str) -> AnnotationSet:
    annotations = []

    with open(filename) as fd:
        lines = fd.readlines()

    for line in lines:
        annotations.append(parse_line(line))

    with open(filename[:-4] + '.txt') as fd:
        sentences = fd.readlines()

    return AnnotationSet(annotations, sentences)


def parse_line(line:str) -> Annotation:
    if line.startswith('T'):
        return parse_entity(line)
    if line.startswith('E'):
        return parse_event(line)
    if line.startswith('R'):
        return parse_relation(line)
    if line.startswith('A'):
        return parse_attribute(line)

    raise ValueError(f"Invalid line: {line}")


def parse_entity(line:str) -> EntityAnnotation:
    parts = line.strip().split("\t")

    if len(parts) != 3:
        raise ValueError(f"Invalid line: {line}")

    id = parts[0]
    text = parts[2]

    middle = parts[1].split()

    if len(middle) != 3:
        raise ValueError(f"Expected only 3 items in {middle}")

    type = middle[0]
    start = int(middle[1])
    end = int(middle[2])

    return EntityAnnotation(id, type, (start, end), text)


def parse_event(line:str) -> RelationAnnotation:
    parts = line.strip().split("\t")

    if len(parts) != 2:
        raise ValueError(f"Invalid line: {line}")

    id = parts[0]
    rest = parts[1].split()
    args = [item.split(":") for item in rest]
    args = { k:v for k,v in args }

    return EventAnnotation(id, args)


def parse_relation(line:str) -> RelationAnnotation:
    parts = line.strip().split("\t")

    if len(parts) != 2:
        raise ValueError(f"Invalid line: {line}")

    id = parts[0]
    rest = parts[1].split()
    type = rest[0]
    args = [item.split(":") for item in rest[1:]]
    args = { k:v for k,v in args }

    return RelationAnnotation(id, type, args)


def parse_attribute(line:str) -> AttributeAnnotation:
    parts = line.strip().split("\t")

    if len(parts) != 2:
        raise ValueError(f"Invalid line: {line}")

    id = parts[0]
    rest = parts[1].split()

    if len(rest) != 2:
        raise ValueError(f"Expected 2 items in {rest}")

    type = rest[0]
    ref = rest[1]

    return AttributeAnnotation(id, type, ref)


def main():
    fire.Fire()


if __name__ == '__main__':
    main()

