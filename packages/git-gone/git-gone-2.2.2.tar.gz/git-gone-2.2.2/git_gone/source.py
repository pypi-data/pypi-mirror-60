import pathlib


SCRIPT_SHEBANG = "#!/usr/bin/env bash"
SCRIPT_BODY = """# Create tracker file if it doesn't exist
if ! [[ -r $file ]]; then
	touch $file;
fi;

track_changed_git_repos()
{
	if git -C "$PWD" rev-parse; then
		echo $PWD >> $file;
	fi;
}

chpwd() {
	(track_changed_git_repos >/dev/null 2>&1 &)
}


leave() {
  git-gone synchronise --yes && echo "Shutting down in $1 seconds" && sleep "$1" && shutdown now
}

begone() {
  git-gone synchronise --yes && shutdown now
}"""
SCRIPT_TEMPLATE = """{shebang}

{file_source}

{body}"""


def configure(parser):
    parser.add_argument("--file", "-f", type=pathlib.Path, default=pathlib.Path.home() / ".modified")


def main(args):
    print(SCRIPT_TEMPLATE.format(shebang=SCRIPT_SHEBANG, file_source=f'file="{args.file}";', body=SCRIPT_BODY))
