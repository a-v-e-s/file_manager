"""
coroutine for sorting files
"""


import os
import pickle
from tempfile import TemporaryDirectory
from shutil import copy2
import subprocess
# jank to avoid deprecation warnings:
from setuptools import distutils; from distutils.dir_util import copy_tree

import PIL

import utils


def sorting_coroutine(full_dirs, filter_dirs, filter_filetypes, notifier):
    """ File sorting coroutine """

    # get all pickles of filehashes:
    pickles = dict()
    pickles_changed = False # used later
    for dir_ in utils.MANAGED:
        try:
            pickles[dir_] = utils.load_pickle(dir_)
        except FileNotFoundError:
            pickles[dir_] = utils.generate_pickle(dir_)

    
    # create a temporary directory,
    with TemporaryDirectory() as tdir:
        
        # then move all the stuff to it for sorting:
        for dir_ in full_dirs:
            copy_tree(dir_, tdir)
        #
        for dir_ in filter_dirs:
            
            for filetype in filter_filetypes:
                p = subprocess.Popen(
                    ['find', dir_, '-type', 'f', '-iname', f'*{filetype}'],
                    stdout=subprocess.PIPE
                )
                
                for file_ in str(p.stdout.read()).split('\\n'):
                    try:
                        copy2(file_.lstrip("b'"), tdir)
                    except FileNotFoundError:
                        pass

        # the main loop!
        for root, _, fns in os.walk(tdir):
            #
            for fn in fns:
                #
                filepath = os.path.join(root, fn)
                filehash = utils.get_hash(filepath)
                
                # display the file for the user:
                displaying = False
                if fn[-3:] in {'jpg', 'png', 'bmp', 'gif', 'peg', 'ebp'}:
                    try:
                        utils.display_img(filepath)
                        displaying = True
                    except PIL.UnidentifiedImageError:
                        subprocess.Popen(['xdg-open', filepath], stdout=subprocess.PIPE)
                #
                else:
                    p = subprocess.Popen(['xdg-open', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    err = p.stderr.read()
                    if err:
                        notifier.config(text=f'xdg-open failed with {filepath}:\n{err}.')
                        print(f'xdg-open failed with {filepath}:\n{err}.')
                        print('\nContinuing...')
                        continue

                # Wait patiently here for destination directory
                destination = (yield)
                if displaying: utils.close_display()

                if destination is None:
                    continue
                
                # do we track files in this files destination?
                if (predestination := '/'+'/'.join(destination.split('/')[1:4])) in utils.MANAGED:

                    # does it already exist?
                    if filehash in pickles[predestination]:
                        notifier.config(text=f'{fn} found in {destination}:\n\t{pickles[predestination][filehash]}')
                        print(f'{fn} found in {destination}:\n\t{pickles[predestination][filehash]}')
                        print('Continuing...')
                        continue

                    # if not, track it:
                    else:
                        copy2(filepath, destination)
                        pickles[predestination][filehash] = os.path.join(destination, fn)
                        if not pickles_changed: # they've changed now!
                            pickles_changed = [predestination]
                        elif predestination not in pickles_changed:
                            pickles_changed.append(predestination)

                # just stick it in there.
                else: copy2(filepath, destination)

        # update our pickles:
        if pickles_changed:
            for pkl in pickles_changed:
                with open(os.path.join(pkl, 'file_db.pkl'), 'rb') as file:
                    pickle.dump(pickles[pkl], file)
    
    raise GeneratorExit('Done!')


if __name__ == '__main__':
    pass