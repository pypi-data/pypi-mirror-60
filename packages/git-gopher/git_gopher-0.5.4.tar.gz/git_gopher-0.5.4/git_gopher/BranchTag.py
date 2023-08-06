from git_gopher.CommandInterface import CommandInterface
from git_gopher.NoTagsException import NoTagsException
from git_gopher.HistoryCommandRunner import HistoryCommandRunner
from git_gopher.GitDataGetter import GitDataGetter

class BranchTag(CommandInterface):
    def __init__(self, hist_command_runner: HistoryCommandRunner, git_data_getter: GitDataGetter):
        self._hist_command_runner = hist_command_runner
        self._git_data_getter = git_data_getter

    def run(self):
        try:
            from_tag = self._git_data_getter.get_tag_name(preview='echo "git checkout -b [new_branch_name] {2}"')
        except NoTagsException:
            print("No tags exist for this repository")
            return

        if from_tag:
            new_branch_name = self._git_data_getter.get_branch_name_from_input()
            return self._hist_command_runner.run(['git', 'checkout', '-b', new_branch_name, from_tag])
