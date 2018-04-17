# coding: utf8

import fire
import typing
import os
import random


class Annotation:
    def solve_references(self, annotations):
        return

    def assign_annotations(self, sentences):
        return True

    def as_text(self):
        return None


class EntityAnnotation(Annotation):
    def __init__(self, id:str, type:str, offsets:typing.Tuple[int,int], text:str):
        self.id = id
        self.type = type
        self.global_offsets = offsets
        self.text = text
        self.sentence = None

    def set_id(self, id):
        self.id = f"T{id}"

    def fix_references(self):
        pass

    def __repr__(self):
        return f"EntityAnnotation({self.id}, {self.type}, {self.global_offsets}, {self.text})"

    def __str__(self):
        return f"{self.id}\t{self.type} {self.global_offsets[0]} {self.global_offsets[1]}\t{self.text}"

    def assign_annotations(self, sentences):
        for s in sentences:
            start, end = self.global_offsets

            if start >= s.offset and end < s.offset + len(s):
                s.annotations.append(self)
                self.local_offsets = (start - s.offset, end - s.offset)
                self.sentence = s

                return True

        return False

    def as_text(self):
        return self.text


class RelationAnnotation(Annotation):
    def __init__(self, id:str, type:str, args:typing.Mapping[str,str]):
        self.id = id
        self.type = type
        self.args = args
        self.sentence = None

    def set_id(self, id):
        self.id = f"R{id}"

    def fix_references(self):
        self.args = { k: e.id for k,e in self.ref_args.items() }

    def solve_references(self, annotations:typing.Mapping[str,Annotation]):
        ref_args = {}

        for type, ref in self.args.items():
            ref_args[type] = annotations[ref]

        self.ref_args = ref_args

    def __repr__(self):
        return f"RelationAnnotation({self.id}, {self.type}, {self.args})"

    def __str__(self):
        args = " ".join(f"{k}:{v}" for k,v in self.args.items())
        return f"{self.id}\t{self.type} {args}"

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

    def as_text(self):
        return f"{self.ref_args['Arg1'].as_text()}:{self.type}:{self.ref_args['Arg2'].as_text()}"


class AttributeAnnotation(Annotation):
    def __init__(self, id:str, type:str, ref:str):
        self.id = id
        self.type = type
        self.ref = ref
        self.sentence = None

    def solve_references(self, annotations:typing.Mapping[str,Annotation]):
        self.ref_ref = annotations[self.ref]

    def set_id(self, id):
        self.id = f"A{id}"

    def fix_references(self):
        self.ref = self.ref_ref.id

    def assign_annotations(self, sentences):
        if not self.ref_ref.sentence:
            return False

        self.sentence = self.ref_ref.sentence
        self.sentence.annotations.append(self)

        return True

    def __repr__(self):
        return f"AttributeAnnotation({self.id}, {self.type}, {self.ref})"

    def __str__(self):
        return f"{self.id}\t{self.type} {self.ref}"


class EventAnnotation(Annotation):
    def __init__(self, id:str, args:typing.Mapping[str,str]):
        self.id = id
        self.args = args
        self.sentence = None

    def set_id(self, id):
        self.id = f"E{id}"

    def fix_references(self):
        self.args = { k: e.id for k,e in self.ref_args.items() }

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

    def __str__(self):
        args = " ".join(f"{k}:{v}" for k,v in self.args.items())
        return f"{self.id}\t{args}"


class Sentence:
    def __init__(self, text:str):
        self.text = text
        self.annotations = []
        self.offset = None

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return f"Sentence({repr(self.text)})"

    def all_annotations(self):
        result = []

        for ann in self.annotations:
            text = ann.as_text()

            if text:
                result.append(text)

        return result


class SentenceList:
    def __init__(self, sentences:typing.List[Sentence]):
        self.sentences = sentences

        entities = 1
        offset = 0

        for s in sentences:
            s.offset = offset

            for ann in s.annotations:
                ann.set_id(entities)
                entities += 1

                if isinstance(ann, EntityAnnotation):
                    start, end = ann.local_offsets
                    ann.global_offsets = (start + offset, end + offset)

            offset += len(s)

        for s in sentences:
            for ann in s.annotations:
                ann.fix_references()


    def dump(self, fname):
        with open(fname, 'w') as fd:
            for sentence in self.sentences:
                for ann in sentence.annotations:
                    fd.write(f"{ann}\n")

        with open(fname[:-4] + '.txt', 'w') as fd:
            for sentence in self.sentences:
                fd.write(sentence.text)


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

    def empty_sentences(self):
        empty = []

        for s in self.sentences:
            if not s.annotations:
                empty.append(s)

        return empty

    def empty_annotations(self):
        empty = []

        for a in self.annotations.values():
            if not a.sentence:
                empty.append(a)

        return empty

    def all_annotations(self):
        things = set()

        for ann in self.annotations.values():
            t = ann.as_text()

            if t:
                things.add(t)

        return things


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


def training_annotations(dir):
    annotations = set()

    for fname in os.listdir(dir):
        if fname.endswith('.ann'):
            annotations.update(parse_ann(os.path.join(dir, fname)).all_annotations())

    return annotations


def split_test_dev(training, dev, output):
    all_sentences = []

    for fname in os.listdir(dev):
        if fname.endswith('.ann'):
            all_sentences.extend(parse_ann(os.path.join(dev, fname)).sentences)

    training = training_annotations(training)

    for sentence in all_sentences:
        in_training = 0
        out_training = 0

        annotations = sentence.all_annotations()

        for ann in annotations:
            if ann in training:
                in_training += 1
            else:
                out_training += 1

        sentence.balance = in_training - out_training

    all_sentences.sort(key=lambda s: s.balance)

    global_balance = 0
    test_set = []

    for i in range(300):
        if global_balance < 0:
            s = all_sentences.pop(-1)
        else:
            s = all_sentences.pop(0)

        test_set.append(s)
        global_balance += s.balance

    total_annotations = 0
    in_annotations = 0

    for s in test_set:
        for ann in s.all_annotations():
            total_annotations += 1
            if ann in training:
                in_annotations += 1

    print("Training coverage: %.2f" % (in_annotations / total_annotations))

    r = random.Random(42)

    r.shuffle(test_set)
    r.shuffle(all_sentences)

    scenario1 = SentenceList(test_set[:100])
    scenario2 = SentenceList(test_set[100:200])
    scenario3 = SentenceList(test_set[200:])
    develop = SentenceList(all_sentences)

    develop.dump(os.path.join(output, 'develop.ann'))
    scenario1.dump(os.path.join(output, 'scenario1.ann'))
    scenario2.dump(os.path.join(output, 'scenario2.ann'))
    scenario3.dump(os.path.join(output, 'scenario3.ann'))


def main():
    fire.Fire()


if __name__ == '__main__':
    main()

