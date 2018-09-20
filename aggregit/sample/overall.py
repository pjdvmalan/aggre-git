"""
Overall sample report.

This script is not easy to maintain or extend but it used as a demo of
how stats can be aggregated down to a commit level for a specific user.

Iterates through configured repos and the PRs within it. Count the commits
which the configured users contributed to the PR.

https://developer.github.com/v3/git/commits/

https://stackoverflow.com/questions/18750808/difference-between-author-and-committer-in-git
The commit.author is who wrote the patch.
The commit.committer is a project maintainer and who merged the patch on behalf
of the author.
"""
from etc import config
import lib
from lib.connection import CONN

# TODO: Refactor to do counts for each user with one pass through the repos.
login = config.USERNAMES[0]

for repo_name in config.REPO_PATHS:
    repo = CONN.get_repo(repo_name)

    print("######## REPO ########")
    print(repo.full_name)
    print(repo.name)
    print(repo.description)

    u_prs = 0
    u_commits = 0
    u_additions = 0
    u_deletions = 0

    # Note that .totalCount gives an error so can't be used to count PRs
    # in a repo.

    # Only activity in PRs is counted, not direct commits to a branch.
    for pr in repo.get_pulls():
        pr_author = pr.user

        if pr.user.login == login:
            u_prs += 1
            print("### PR ###")
            print(f"ID: {pr.number}")
            print(f"Title: {pr.title}")

            print(f"Author: @{pr_author.login}")
            print(f"Commits: {pr.commits}")
            print()

            print("--- Commits ---")
            if pr.commits:
                for commit in pr.get_commits():
                    # Sometimes author can be None. Perhaps if the user is
                    # inactive or it was left off the of config file.
                    if commit.author and commit.author.login == login:
                        u_commits += 1

                        date = lib.parse_datetime(
                            commit.stats.last_modified
                        ).date()
                        commit_data = dict(
                            SHA=commit.sha,
                            last_modified=str(date),
                            additions=commit.stats.additions,
                            deletions=commit.stats.deletions,
                            total=commit.stats.total
                        )
                        print(commit_data)

                        comments = list(commit.get_comments())
                        print(f"Comments: {len(comments)}")

                        for file_ in commit.files:
                            print(file_.filename)
                            print(f"  Changes: {file_.changes}")
                            print(f"  Additions: {file_.additions}")
                            print(f"  Deletions: {file_.deletions}")
                            print(f"  Status: {file_.status}")

                            print(f"  Raw URL: {file_.raw_url}")
                            print(f"  Blob URL: {file_.blob_url}")
                            # See also file_.patch for the diff.

                            u_additions += file_.additions
                            u_deletions += file_.deletions
                            print()
                    else:
                        print(pr.title)
                        print(f"Expected: {login}")
                        print(commit)

                print()
        print()
print()

print(f"Totals for {login} for configured repos")
data = {
   'prs': u_prs,
   'commits': u_commits,
   'additions': u_additions,
   'deletions': u_deletions,
}
print(data)
