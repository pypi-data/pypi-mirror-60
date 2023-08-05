import os
import sys
import time
from .spinner_progress import SpinnerProgress
from git import Repo, Git, GitCommandError
from .constants import repository as constants


class Repository:

    def __init__(self):
        self.repo_dir = constants['repo_dir']

    def repo_already_exists(self):
        return os.path.isdir('./{}'.format(self.repo_dir))

    def ask_use_existent_repo(self):
        res = input(constants['use_existent_repository'])
        return True if res == "y" else False

    def exit(self):
        print(constants['delete_repository'])
        sys.exit(0)

    def make_clone(self):
        progress = SpinnerProgress(constants['clonning_repository'])
        try:
            progress.start()
            Git(".").clone(constants['repository_url'])
            cloned_repo = Repo(self.repo_dir)
            cloned_repo.git.checkout(constants['current_branch'])
            time.sleep(2)
            progress.finish()
        except GitCommandError:
            progress.finish()
            print(constants['cant_clone'])
            sys.exit(0)

    def clone(self):
        if self.repo_already_exists():
            use_existent_repo = self.ask_use_existent_repo()
            if use_existent_repo:
                return
            else:
                self.exit()

        self.make_clone()
