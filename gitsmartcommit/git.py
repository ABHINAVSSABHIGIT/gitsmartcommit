# Modified main.py
import os
import sys
import re
import subprocess
import argparse
if sys.version_info >= (3, 7):
    from .generate_commit_message import generate_commit_message, _pick_tag
else:
    from generate_commit_message import generate_commit_message, _pick_tag


def check_git_repo(path: str) -> bool:
    try:
        subprocess.check_output(
            ['git', '-C', path, 'rev-parse', '--is-inside-work-tree'],
            stderr=subprocess.STDOUT
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("Error: git is not installed or not in PATH.")
        sys.exit(1)


def git_branch(path: str) -> str:
    try:
        branch = subprocess.check_output(
            ['git', '-C', path, 'branch', '--show-current'],
            stderr=subprocess.STDOUT
        )
        return branch.decode('utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not get branch name — {e}")
        return ""


def git_diff(path: str) -> str:
    """
    Get the diff to analyze.
    Priority: staged changes first, fall back to unstaged if nothing is staged.
    """
    try:
        # Staged changes (git add has been run)
        staged = subprocess.check_output(
            ['git', '-C', path, 'diff', '--cached'],
            stderr=subprocess.STDOUT
        ).decode('utf-8', errors='replace')

        if staged.strip():
            return staged

        # Nothing staged — try unstaged
        unstaged = subprocess.check_output(
            ['git', '-C', path, 'diff'],
            stderr=subprocess.STDOUT
        ).decode('utf-8', errors='replace')

        if unstaged.strip():
            print("Note: No staged changes found. Analyzing unstaged changes instead.")
            print("      Run 'git add <files>' to stage changes before committing.\n")
            return unstaged

        return ""

    except subprocess.CalledProcessError as e:
        print(f"Error: Could not read git diff — {e}")
        sys.exit(1)


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Generate a commit message from your git diff."
        )
        parser.add_argument(
            '--path', '-p',
            default=os.getcwd(),
            help="Path to the git repository (default: current directory)"
        )
        parser.add_argument(
            '--branch', '-b',
            default='',
            help="Override the branch name shown in the commit message"
        )
        args = parser.parse_args()

        path   = os.path.abspath(args.path)
        branch = args.branch

        # Validate path
        if not os.path.isdir(path):
            print(f"Error: Path does not exist: {path}")
            sys.exit(1)

        # Check it's a git repo
        if not check_git_repo(path):
            print(f"Error: Not a git repository: {path}")
            sys.exit(1)

        # Get branch
        current_branch = branch or git_branch(path)

        # Get diff
        diff = git_diff(path)

        if not diff.strip():
            print("Nothing to commit — no staged or unstaged changes found.")
            sys.exit(0)

        # Generate the message — this prints the display and returns the subject
        result = generate_commit_message(diff, current_branch)

        if result:
            subject = result.get("subject", "").strip()
            display = result.get("display", "")
            files = result.get("_files", [])

            # Show preview UI
            print(display)

            # -------- INDUSTRY STYLE BODY --------
            # Compute tag_counts to determine primary_tag
            from collections import defaultdict
            tag_counts = defaultdict(int)
            for r in files:
                tag_counts[r["tag"]] += 1
            primary_tag = _pick_tag(tag_counts)  # Assuming _pick_tag is defined in generate_commit_message.py, import if needed

            # Map to Conventional Commits type
            tag_map = {
                "[ADD]": "feat",
                "[FIX]": "fix",
                "[UPDATE]": "chore",
                "[REFACTOR]": "refactor",
                "[STYLE]": "style",
                "[DOCS]": "docs",
                "[CONFIG]": "chore",
                "[TEST]": "test",
                "[RENAME]": "refactor",
                "[REMOVE]": "chore",
                "[CHORE]": "chore",
            }
            conv_type = tag_map.get(primary_tag, "chore")

            # Clean subject for description
            branch_part = f"[{current_branch}]" if current_branch else ""
            lead_summary = subject.replace(primary_tag, "").replace(branch_part, "").strip()
            clean_desc = re.sub(r"\[\w+\]", "", lead_summary).strip()
            verb = clean_desc.split(" ", 1)[0].lower() if clean_desc else ""
            rest = clean_desc.split(" ", 1)[1] if " " in clean_desc else ""
            description = f"{verb} {rest}".replace(" (+7 more)", "").strip()

            # Special case for initial large add
            verbs = set(r["summary"].split(" ", 1)[0] for r in files if " " in r["summary"])
            if len(files) > 3 and len(verbs) == 1 and "Add" in verbs:
                description = "initial project files and structure"

            # Add scope if branch not main
            scope = f"({current_branch})" if current_branch and current_branch != "main" else ""
            industry_subject = f"{conv_type}{scope}: {description}"

            # Build body
            body_lines = []
            for r in files:
                summary = r["summary"]
                clean_summary = re.sub(r"\[\w+\]", "", summary).strip()
                body_lines.append("- " + clean_summary)

            # Adjust for common verb
            if len(verbs) == 1:
                common_verb = list(verbs)[0]
                body_lines = ["- " + r["summary"].replace(common_verb + " ", "", 1).strip() for r in files]
                intro = common_verb + " the following:"
            else:
                intro = "Apply the following changes:"

            # Special intro paragraph for large adds
            body = intro + "\n" + "\n".join(body_lines)
            if len(files) > 3 and len(verbs) == 1 and "Add" in verbs:
                project_intro = "Introduce core components for the gitsmartcommit tool, including configuration, documentation, and Python modules for commit generation."
                body = project_intro + "\n\n" + body

            # -------- FINAL COMMAND --------
            import shlex

            if industry_subject:
                print("\n  To commit, run:")

                if body:
                    print(
                        f'  git commit -m {shlex.quote(industry_subject)} -m {shlex.quote(body)}\n'
                    )
                else:
                    print(
                        f'  git commit -m {shlex.quote(industry_subject)}\n'
                    )

    except Exception as e:
        print(f"\n  [ERROR] An unexpected error occurred: {e}")
        print("  Please check your git installation, ensure you are in a git repository, and try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()