import pathlib
import traceback

from plumbum import cmd, local, ProcessExecutionError, TF

MODIFIED_PATH = pathlib.Path.home() / ".modified"
MODIFIED_PATH.touch()

DEFAULT_COMMIT_ALL_CHANGES_MESSAGE = f"{__package__}: Commit any changes"
GIT_GONE_BRANCH_NAME = "git-gone"
GIT_GONE_STASH_MESSAGE = "git-gone stash commit"


def has_unpushed_commits() -> int:
    """Determine if there are any unpushed commits for the cwd.

    :return:
    """
    return cmd.git("log", "@{u}..", "-q")


def count_modified_files() -> int:
    """Determine how many uncommitted changes there are in the cwd.

    :return:
    """
    return int((cmd.git["status", "--porcelain", "--untracked-files=no"] | cmd.wc["-l"])())


def get_current_branch() -> str:
    return cmd.git("rev-parse", "--abbrev-ref", "HEAD").strip()


def get_branch_remote(branch: str) -> str:
    return cmd.git("config", "--local", f"branch.{branch}.remote").strip()


def yes_no_response(query: str, default_response: bool = True) -> bool:
    """Prompt user with a yes / no response for a given query string.

    :param query: query string
    :param default_response: default return value if user input invalid
    :return:
    """
    default_string = "Y/n" if default_response else "y/N"

    response = input(f"{query} [{default_string}] ").lower().strip()
    if response in ("y", "yes"):
        return True
    elif response in ("n", "no"):
        return False
    return default_response


def configure(parser):
    parser.add_argument("--yes", "-y", action='store_true')


def synchronise_local_changes(interactive: bool = False):
    """Synchronise local changes (if any) with remote, in special branch.
    If any errors occur during this process, we restore save the stash and print a detailed message.
    
    :param interactive: whether to request user confirmation
    :return: 
    """
    branch_name = get_current_branch()
    remote_name = get_branch_remote(branch_name)

    # Use `git stash create` to avoid creating a stash entry unless required
    stash_commit = cmd.git("stash", "create").strip()

    try:
        cmd.git("checkout", "-fB", GIT_GONE_BRANCH_NAME)
        cmd.git("reset", "--hard", branch_name)

        if stash_commit:
            cmd.git("stash", "apply", "--index", stash_commit)

            if not interactive:
                message = DEFAULT_COMMIT_ALL_CHANGES_MESSAGE
            else:
                message = input(
                    "Enter commit message (leave blank for default): "
                ) or DEFAULT_COMMIT_ALL_CHANGES_MESSAGE

            cmd.git("commit", "-am", message)

        cmd.git("push", "-u", remote_name, GIT_GONE_BRANCH_NAME, "--force")
        cmd.git("checkout", branch_name)

        if stash_commit:
            cmd.git("stash", "apply", "--index", stash_commit)

    except Exception:
        # Try and return to branch and apply stash to recover, else fail and save commit
        if (cmd.git["checkout", "-f", branch_name] & TF) and (cmd.git["stash", "apply", "--index", stash_commit] & TF):
            print("Unable to cleanly perform synchronisation. Working state was recovered, but unable to synchronise.")
        else:
            cmd.git("stash", "store", stash_commit, "--message", GIT_GONE_STASH_MESSAGE)
            print(
                "Unable to cleanly perform synchronisation, and couldn't manually recover. "
                "Please check status of repository, and use `git reset --hard && git stash apply --index` "
                f"on {branch_name} ")
        raise


def main(args):
    paths = {pth for pth in (pathlib.Path(p) for p in MODIFIED_PATH.read_text().splitlines()) if
             pth.exists() and not (pth / ".git-gone-ignore").exists()}
    handled_paths = set()

    try:
        for path in paths:
            with local.cwd(path):
                git_root_dir = cmd.git("rev-parse", "--show-toplevel").strip()
                if git_root_dir in handled_paths:
                    continue

                try:
                    if has_unpushed_commits() or count_modified_files():
                        if args.yes or yes_no_response(
                                f"{git_root_dir} has local changes which do not exist "
                                f"on the remote, do you want to push them?"
                        ):
                            synchronise_local_changes(interactive=not args.yes)

                except ProcessExecutionError:
                    traceback.print_exc()
                    continue

                handled_paths.add(git_root_dir)
    finally:
        # Clear modified file in case of errors
        MODIFIED_PATH.write_text('\n'.join(str(p) for p in (paths - handled_paths)))
