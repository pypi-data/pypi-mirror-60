from git_gopher.CommandInterface import CommandInterface
from git_gopher.HistoryCommandRunner import HistoryCommandRunner
from git_gopher.GitDataGetter import GitDataGetter

class PushTag(CommandInterface):
    def __init__(self, hist_command_runner: HistoryCommandRunner, git_data_getter: GitDataGetter):
        self._hist_command_runner = hist_command_runner
        self._git_data_getter = git_data_getter

    def run(self):
        preview = 'echo "Select a remote. No action is taken until selecting a tag."'
        remote = self._git_data_getter.get_remote_name(preview=preview)

        if not remote:
            return

        tag = self._git_data_getter.get_local_tag_name(remote, preview='echo "git push -u ' + remote + ' {2}"')

        if tag:
            return self._hist_command_runner.run(['git', 'push', '-u', remote, tag])
