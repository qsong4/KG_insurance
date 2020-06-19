import os, sys
cur_dir = os.path.dirname(__file__)


def pre(infile, infile2, outfile):
    type_map = {}
    with open(infile2, "r") as fr:
        for line in fr:
            content = line.strip().split("\t")
            ins = content[0]
            _type = content[1]
            if ins in type_map:
                type_map[ins].append(_type)
            else:
                type_map[ins] = [_type]

    with open(infile, "r") as fr, open(outfile, "w") as fw:
        for line in fr:
            content = line.strip().split("\t")
            content = content[:-1]
            ins = content[0]
            if ins in type_map:
                content.append("|".join(type_map[ins]))
            else:
                content.append("0")
            fw.write("\t".join(content) + "\n")


if __name__ == '__main__':
    pre("./insurance_label.csv", "./rel_type.csv", "./insurance_feature.csv")
