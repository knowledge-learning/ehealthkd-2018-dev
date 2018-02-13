# coding: utf8

import os
import sys
import shutil


def main():
    brat_path = "../data/TASS-2018/"
    output_path = "../gold/"

    for dirpath, _, filenames in os.walk(brat_path):
        for fname in filenames:
            if fname.endswith('.ann') and fname != "readme.ann" and not fname.startswith("_"):
                text_name = fname[:-4] + ".txt"

                # Copy the text
                with open(os.path.join(output_path, "input_" + text_name), "w", encoding="utf8") as fwrite:
                    with open(os.path.join(dirpath, text_name), "r", encoding="utf8") as fread:
                        fwrite.write(fread.read())

                # Prepare the output files
                output_A = open(os.path.join(output_path, "output_A_" + text_name), "w", encoding="utf8")
                output_B = open(os.path.join(output_path, "output_B_" + text_name), "w", encoding="utf8")
                output_C = open(os.path.join(output_path, "output_C_" + text_name), "w", encoding="utf8")

                events = []
                mapping = {}

                # Read the annotations
                with open(os.path.join(dirpath, fname), "r", encoding="utf8") as fp:
                    for line in fp:
                        annotation = line.strip().split()

                        if annotation[0].startswith("T"):
                            # It's a type annotation, we have to fill A and B
                            idx = annotation[0][1:]
                            label, start, end, = annotation[1:4]
                            output_A.write("%s\t%s\t%s\n" % (idx, start, end))
                            output_B.write("%s\t%s\n" % (idx, label))

                        if annotation[0].startswith("R"):
                            # It's a relation annotation, we have to fill C
                            label, arg1, arg2 = annotation[1:4]

                            if arg1.startswith("Arg2:"):
                                arg1, arg2 = arg2, arg1

                            arg1 = arg1[6:]
                            arg2 = arg2[6:]

                            output_C.write("%s\t%s\t%s\n" % (label, arg1, arg2))

                        if annotation[0].startswith("E"):
                            # It's an event annotation, we have to fill C
                            label, idx = annotation[1].split(":")

                            # Since events can link to other events, we have
                            # to collect them all before writing them out to build the mapping
                            mapping[annotation[0]] = idx
                            events.append(annotation)

                written = set()

                # Now it's time to process those events
                for annotation in events:
                    label, idx = annotation[1].split(":")
                    idx = idx[1:]

                    subj = None
                    targ = None

                    if label == "Action":
                        components = annotation[2:]

                        for c in components:
                            if c.startswith("Subject:"):
                                subj = c
                            else:
                                targ = c

                    if subj:
                        subj = subj[8:]
                        while subj.startswith("E"):
                            subj = mapping[subj]
                        subj = subj[1:]

                    if targ:
                        targ = targ[7:]
                        while targ.startswith("E"):
                            targ = mapping[targ]
                        targ = targ[1:]

                    if subj:
                        rel = "subject\t%s\t%s\n" % (idx, subj)

                        if rel not in written:
                            output_C.write(rel)
                            written.add(rel)
                    if targ:
                        rel = "target\t%s\t%s\n" % (idx, targ)

                        if rel not in written:
                            output_C.write("target\t%s\t%s\n" % (idx, targ))
                            written.add(rel)
                    # if label == "Reflexive-Action":
                    #     output_C.write("Reflexive-Action\t%s\t%s\n" % (idx, subj))
                    # if label == "Passive-Action":
                    #     output_C.write("Passive-Action\t%s\t%s\n" % (idx, targ))

                output_A.close()
                output_B.close()
                output_C.close()


    # Move the example files to their respective folders
    example_gold = "../training/example/gold/"
    example_dev = "../training/example/dev/"

    for prefix in "input_ output_A_ output_B_ output_C_".split():
        shutil.move(os.path.join(output_path, prefix + "example.txt"),
                    os.path.join(example_gold, prefix + "example.txt"))
        shutil.move(os.path.join(output_path, prefix + "example.errors.txt"),
                    os.path.join(example_dev, prefix + "example.txt"))

    # trial_gold = "../trial/"

    # for prefix in "input_ output_A_ output_B_ output_C_".split():
    #     shutil.move(os.path.join(output_path, prefix + "trial.txt"),
    #                 os.path.join(trial_gold, prefix + "trial.txt"))

    os.remove(os.path.join(example_dev, "input_example.txt"))


if __name__ == '__main__':
    main()
