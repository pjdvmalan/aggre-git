"""
Sample repo branches script.

Explore getting details of a branch object within a repo.

PyGithub docs
 - Branches:
    https://pygithub.readthedocs.io/en/latest/github_objects/Branch.html
 - Commits:
    https://pygithub.readthedocs.io/en/latest/github_objects/Commit.html
 - Files:
    https://pygithub.readthedocs.io/en/latest/github_objects/File.html
"""
import string
import time

from lib.connection import CONN


def display_commit(commit):
    """
    Print details and stats for a commit.
    """
    print("COMMIT")
    print(commit.sha)
    print(commit.url)
    if commit.author:
        # This was observed in a case where the commit in the Github site
        # has an author who wrote the patch but there is no link to his profile
        # so perhaps he was deleted. So author can be None.
        print(commit.author.login)
    else:
        print("NO AUTHOR")
    print(commit.last_modified)
    print(commit.commit.message.replace("\n", "\t"))
    print(f"{commit.stats.total} | +{commit.stats.additions} | -{commit.stats.deletions})")
    print()


def display_file(file_):
    """
    Print details and stats for a file on a commit.
    """
    print("FILE")
    print(file_.filename)
    print(file_.blob_url)
    print(file_.last_modified)
    print(file_.status)
    print(f"{file_.changes} | +{file_.additions} | -{file_.deletions}")
    print()


def traverse_commits_detailed(commit):
    """
    Display details, stats and files for a given commit and all its parents.

    Include the names of files in the commit and details of the first file.
    Allow for the fact that there could be zero files such in the initial
    commit.

    Then use recursive logic to get all the commits in the chain, starting
    with the commit's parents.
    """
    display_commit(commit)

    if commit.files:
        print([file_.filename for file_ in commit.files])
        print()
        display_file(commit.files[0])
    else:
        print("No files on commit")

    time.sleep(1)

    # For a merge there could be multiple parents.
    # When storing objects rather than just printing, consider using
    # `yield` to avoid doing a return on the first only.
    for parent in commit.parents:
        traverse_commits_detailed(parent)


def traverse_commits_short(commit, depth=1, parent_index=0):
    """
    Display summarized data for commits in a chain.

    Display attributes recursively for a commit and its parents.
    """
    depth_display = f"depth {depth:3}"
    parent_symbol = f"path {string.ascii_uppercase[parent_index]}"
    elements = (commit.sha, depth_display, parent_symbol, commit.commit.message.replace("\n", "\t"))
    print(" | ".join(elements))

    for i, parent in enumerate(commit.parents):
        traverse_commits_short(parent, depth+1, i+parent_index)


def main():
    repo = CONN.get_repo("MichaelCurrin/aggre-git")
    branches = list(repo.get_branches())
    branch = branches[0]
    print(f"Branch: {branch.name}")

    head_commit = branch.commit
    traverse_commits_short(head_commit)


if __name__ == '__main__':
    main()