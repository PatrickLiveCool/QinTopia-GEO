#!/usr/bin/env python3
"""Keep one pending release at a time, including across paginated API responses."""
import json
import os
import subprocess


def pending_drafts(pages):
    return [item['tag_name'] for page in pages for item in page if item['draft']]


def main():
    pages = json.loads(subprocess.check_output([
        'gh', 'api', '--paginate', '--slurp',
        f"repos/{os.environ['GITHUB_REPOSITORY']}/releases?per_page=100",
    ]))
    drafts = pending_drafts(pages)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
        out.write('pending=' + str(bool(drafts)).lower() + '\n')
    if drafts:
        message = 'Waiting for existing draft release(s): ' + ', '.join(drafts)
        print(message)
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
            out.write(message + '\nNo new version PR created.\n')


if __name__ == '__main__':
    main()
