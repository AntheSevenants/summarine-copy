import git
import argparse
import os.path
import re
from tqdm.auto import tqdm
from shutil import copytree, copyfile

parser = argparse.ArgumentParser(
    description='summarine-copy - Copy from my personal notes to the public notes repository')
parser.add_argument('source', type=str,
                    help='Path to the source repository')
parser.add_argument('destination', type=str,
                    help='Path to the destination repository')
parser.add_argument('course_name', type=str,
                    help='Path to the internal course name')
args = parser.parse_args()

print("Initialising remote repository")
source = git.Repo(args.source)

print("Pulling from remote")
source.remotes[0].pull()

print("Initialising destination repository")
destination = git.Repo(args.destination)

print("Pulling from remote")
destination.remotes[0].pull()

full_source_path = f"{args.source}/{args.course_name}/"
print("Asserting source path exists")
assert os.path.exists(full_source_path)

print("Iterating over files")
source_files = os.listdir(full_source_path)
public_files = []
public_resources = set()
for source_file in source_files:
    if source_file == ".resources":
        continue

    full_dir = f"{full_source_path}/{source_file}"
    if not os.path.isdir(full_dir):
        continue

    full_path = f"{full_dir}/content.md"
    with open(full_path, "rt") as reader:
        content = reader.read()
        if "$public=true$" in content:
            public_files.append(source_file)
        else:
            continue
            
        # Resource scraping
        pattern = "img\$(.{4})"
        results = re.findall(pattern, content)
        public_resources.update(results)

print(f"Found {len(public_files)} public files")

for public_file in tqdm(public_files, desc="Copying public files to destination repository"):
    source_dir =  f"{full_source_path}/{public_file}"
    dest_dir = (f"{args.destination}/{public_file}")
    copytree(source_dir, dest_dir, dirs_exist_ok=True)

print(f"Found {len(public_resources)} public resources")

# In case resources directory does not exist
os.makedirs(f"{args.destination}/.resources", exist_ok=True)

for public_resource in tqdm(public_resources, desc="Copying public files to destination repository"):
    source_file =  f"{full_source_path}/.resources/{public_resource}"
    dest_file = (f"{args.destination}/.resources/{public_resource}")
    copyfile(source_file, dest_file)

print("Done")