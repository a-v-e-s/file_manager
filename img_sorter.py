import os
import subprocess
from tempfile import TemporaryDirectory
from shutil import copy2
from PIL import Image
import psutil

# jank to avoid deprecation warnings:
from setuptools import distutils; from distutils.dir_util import copy_tree


def main():
    # get directories that need to be fully sorted:
    ret = None
    full_dirs = []
    while ret != 'Q':
        ret = input('Enter absolute paths to directories that need to be completely sorted, or "Q" to quit:\t')
        if os.path.isdir(ret):
            if ret not in full_dirs:
                full_dirs.append(ret)
            else:
                print(f'{ret} already in full_dirs:\n{full_dirs}\n')
        elif ret != 'Q':
            print(f'{ret} is not a valid directory path.\n')


    # get directories that need particular filetypes sorted:
    ret = None
    find_dirs = {}
    while ret != 'Q':
        ret = input('Enter absolute paths to directories that need specific filetypes to be sorted, or "Q" to quit:\t')
        if os.path.isdir(ret):
            if ret not in find_dirs:
                find_dirs[ret] = []
            else:
                print(f'{ret} already in find_dirs:\n{find_dirs}\n')
        elif ret != 'Q':
            print(f'{ret} is not a valid directory path.\n')


    # get filetypes to find for filtered directories:
    for dir_ in find_dirs:
        ret = None
        while ret != 'Q':
            ret = input(f'Directory {dir_}:\n\tEnter filetype that needs to be found and sorted, or "Q" to quit:\t')
            if ret in find_dirs[dir_]:
                print(f'{ret} already in filetypes:\n{find_dirs[dir_]}\n')
            elif ret != 'Q':
                find_dirs[dir_].append(ret)


    # the business end of the script:
    # create a temporary directory,
    # then move all the stuff to it for sorting:
    with TemporaryDirectory() as tdir:
        for dir_ in full_dirs:
            copy_tree(dir_, tdir)
        for dir_ in find_dirs:
            for filetype in find_dirs[dir_]:
                p = subprocess.Popen(['find', dir_, '-type', 'f', '-iname', f'*{filetype}'], stdout=subprocess.PIPE)
                for file_ in str(p.stdout.read()).split('\\n'):
                    try:
                        copy2(file_.lstrip("b'"), tdir)
                    except FileNotFoundError:
                        pass


        targets = {}
        hashes = {}
        counter = 1

        for root, _, fns in os.walk(tdir): # the main loop!
            for fn in fns:
                filepath = os.path.join(root, fn)
                filehash = get_sha1(filepath)

                # does the file already exist somewhere in a target directory?
                skipping = False
                for num in targets:
                    dir_ = targets[num]
                    if filehash in hashes[dir_]:
                        skipping = True
                        print(f'{filepath} already exists in {dir_}, skipping...')
                if skipping:
                    continue
                
                # open file, print directory menu:
                with Image.open(filepath) as img:
                    img.show()
                #_ = subprocess.Popen(['xdg-open', filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if targets:
                    for num in targets:
                        print(f'{num}): {targets[num]}')
                else:
                    print('No directories chosen so far.')

                # What does the user want to do with it?
                ret = ''
                while not ((ret in targets) or (os.path.isdir(ret) and ret not in targets.values()) or (ret.lower() == 'n')):
                    ret = input('Enter number associated with target directory OR enter new target OR "n" to skip:\n')
                    if (not os.path.isdir(ret)) and (ret not in targets) and (ret.lower() != 'n'):
                        print(f'{ret} is not a valid target number or new directory path!')
                
                # close the image display:
                for ps in psutil.process_iter():
                    if ps.name() == 'display':
                        ps.kill()
                        break

                if ret.lower() == 'n': # skipping!
                    continue

                if ret in targets: # copy file, add hash to hashes dict:
                    if filehash not in hashes[targets[ret]]:
                        copy2(filepath, targets[ret])
                        hashes[targets[ret]].add(filehash)
                    else:
                        print(f'{targets[ret]} already contains {filepath}.')

                elif os.path.isdir(ret): # new destination directory:
                    targets[str(counter)] = ret
                    counter += 1

                    # get all hashes from destination:
                    hashes[ret] = set()
                    print('Generating hashes to prevent duplication....')
                    for file_ in os.listdir(ret):
                        hashes[ret].add(get_sha1(os.path.join(ret, file_)))

                    # copy it if it doesn't already exist:
                    if filehash not in hashes[ret]:
                        copy2(filepath, ret)
                        hashes[ret].add(filehash)
                    else:
                        print(f'{ret} already contains {filepath}')


if __name__ == '__main__':
    main()