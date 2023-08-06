import argparse
import sys

parser = argparse.ArgumentParser(prog="trollformatter")
parser.add_argument("--tabsize", help="If file uses tabs, set this as tabsize", type=int)
parser.add_argument("--limit",
                    default=150,
                    help="Ignore lines longer than LIMIT characters when calculating padding.",
                    type=int)
parser.add_argument("file", help="File to format")

args = parser.parse_args()

if args.tabsize == None:
    args.tabsize = 8

f = open(args.file)

longest = max(f,
              key=lambda x: len(x.replace("\t", " "*args.tabsize)) if len(x.replace("\t", " "*args.tabsize)) <= args.limit else 0)

# First, do some preprocessing
f.seek(0)
content = f.read()

if content.find("\t") != -1:
    print("Using tabs for this run.")
    print("WARNING: With tabs, this program's output will not look the same on all systems.")
    print("We highly recommend you convert your file to use spaces instead.")
    cols = len(longest.replace("\t", "        ")) + 2
else:
    cols = len(longest) + 2

f.close()

lines = content.splitlines()
formatted_lines = []

for c, line in enumerate(lines):
    line = line.rstrip()
    if line == "":
        formatted_lines.append(line)
        continue
    elif line[-1] in {"{", ";", "}"}:
        # We found a good one, time to troll hanson
        # Calculate how much we have to pad
        diff = cols - len(line.replace("\t", " "*args.tabsize))
        line = line[:-1] + " " * diff + line[-1]

    if line.strip() == "}":
        # Collapse these
        formatted_lines[-1] += line.strip()
    else:
        formatted_lines.append(line)

print("\n".join(map(lambda x: x.expandtabs(args.tabsize), formatted_lines)))

out_filename = ".".join(args.file.split(".")[:-1]) + "_troll." + args.file.split(".")[-1]

with open(out_filename, "w") as out:
    for line in formatted_lines:
        out.write(line)
        out.write("\n")
