import os
import re
import sys

BASE_FILE_PATH = f"{os.path.dirname(__file__)}/docker-compose-base.yaml"

# Matches a comment in a YAML with a specific tag
COMMENT_REGEX = r"[ \t]*#[ \t]*{}[ \t]*"
# Matches the start of the replication section, with a number in a group named id
START_TAG = COMMENT_REGEX.format(r"replicate-start[ \t]+(?P<id>\d+)")
# Matches the end of the replication section
END_TAG = COMMENT_REGEX.format("replicate-end")
# Matches the start and end tags, with the content in a group with that name
REGEX_REPLICATE = rf".*{START_TAG}\n(?P<content>(?:.|\n)*?){END_TAG}\n?"
# Matches a variable (index_var group) to replace with the replication index within
# a line (content group)
REGEX_INDEX = COMMENT_REGEX.format(r"(?P<index_var>.*)[ \t]*=[ \t]*index") + \
    r"[ \t]*\n(?P<content>.*)"
# Matches a variable (times_var group) to replace with the amount of times to replicate
# an id (id group) within a line (content group)
REGEX_TIMES = COMMENT_REGEX.format(r"(?P<times_var>.*)[ \t]*=[ \t]*times[ \t]+(?P<id>\d+)") + \
    r"[ \t]*\n(?P<content>.*)"

def replace_index(match: re.Match, index: int):
    content = match.group("content")
    index_var = match.group("index_var")
    return content.replace(index_var, f"{index}")

def replace_times(match: re.Match, times: dict[int, int]):
    content = match.group("content")
    times_var = match.group("times_var")
    id = match.group("id")
    return content.replace(times_var, f"{times[int(id)]}")

def replicate(match: re.Match, times: dict[int, int]):
    content = match.group("content")
    id = int(match.group("id"))
    if id not in times:
        print(f"ID {id} not provided, not replicating")
    result = ""
    for i in range(1, times.get(id, 1)+1):
        result += re.sub(REGEX_INDEX, lambda match: replace_index(match, i), content)
    return result

def main():
    args = sys.argv[1:]
    if len(args) <= 1 or any(not x.isnumeric() for x in args[1:]):
        print("Invalid arguments. Usage: ")
        print("python3 generate.py [write path] [times to replicate id 1] [times to replicate id 2] ...")

    write_to, *times = args
    times_per_id = {x+1:int(y) for x, y in enumerate(times)}

    # f.read() and f.write() are guaranteed to read and write the whole file
    # using the with clause
    # https://docs.python.org/3/tutorial/inputoutput.html#methods-of-file-objects

    with open(BASE_FILE_PATH, "r") as f:
        base = f.read()


    times_replaced = re.sub(REGEX_TIMES, lambda match: replace_times(match, times_per_id), base)
    replicated = re.sub(REGEX_REPLICATE, lambda match: replicate(match, times_per_id), times_replaced)
    with open(write_to, "w") as f:
        f.write(replicated)
    

main()