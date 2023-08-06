from os import path
from typing import List
from colorama import Fore, Style
from git_gopher.CommandInterface import CommandInterface
from git_gopher.FormatColumns import FormatColumns
from git_gopher.HistoryCommandRunner import HistoryCommandRunner
from git_gopher.GitDataGetter import GitDataGetter
from git_gopher.Fzf import Fzf

class Add(CommandInterface):
    def __init__(self, hist_command_runner: HistoryCommandRunner, git_data_getter: GitDataGetter, fzf: Fzf):
        self._hist_command_runner = hist_command_runner
        self._git_data_getter = git_data_getter
        self._fzf = fzf

    def run(self):
        unstaged_files = self._get_unstaged_files()
        filepaths = self._get_user_selections(unstaged_files)

        if filepaths:
            for filepath in filepaths:
                self._hist_command_runner.run(['git', 'add', filepath])

    def _get_unstaged_files(self) -> List[str]:
        unstaged_files = self._git_data_getter.get_unstaged_files().splitlines()

        # break up path into subdirectories
        # e.g. path/to/file becomes path\nto
        # so we can include directories in the list to add
        for file in unstaged_files:
            for dir in path.dirname(file).split('/'):
                if path.isdir(dir):
                    dir_files = self._git_data_getter.get_unstaged_files_from_dir(dir)
                    # if there's only 1 file under the given directory, we
                    # don't need to subdivide further, as choosing a parent
                    # directory is the same as choosing the file itself

                    if len(dir_files.splitlines()) > 1:
                        unstaged_files.append(dir)
                    else:
                        break

        # list only unique folders as the above subdirs don't consider it
        unstaged_files = list(set(unstaged_files))
        unstaged_files.sort()

        return self._colorize_unstaged_files(unstaged_files)

    def _colorize_unstaged_files(self, unstaged_files) -> List[str]:
        for i in range(len(unstaged_files)):
            file = unstaged_files[i]

            if not self._git_data_getter.get_is_tracked(file):
                file = Fore.RED + file

            if path.isdir(unstaged_files[i]):
                unstaged_files[i] = Fore.BLUE + "dir" + Style.RESET_ALL + " | " + file
            else:
                unstaged_files[i] = Fore.CYAN + "file" + Style.RESET_ALL + " | " + file

        return unstaged_files

    def _get_user_selections(self, unstaged_files) -> List[str]:
        format_columns = FormatColumns()
        preview = "ggo-add-preview {2}"
        filepaths = self._fzf.run(format_columns.set_colors({0: Fore.BLUE}).format('\n'.join(unstaged_files)), preview=preview, preview_window="--preview-window=right", multi="--multi")

        if (filepaths):
            return list(map(lambda line: line.split('\t')[1].strip(), filepaths.splitlines()))
