import json
import os
import argparse

import requests
from requests.auth import HTTPBasicAuth


class BitBucketException(Exception):
    pass


class BitBucket:
    def __init__(self, user_name, password, team):
        self.base_url = 'https://api.bitbucket.org/2.0'
        self.team = team
        self.auth = HTTPBasicAuth(user_name, password)

    def get_last_commit_author(self, repo_name, branch_name):
        commit_hash = self._get_branch_info(repo_name, branch_name)['target']['hash']
        return self._get_commit_info(repo_name, commit_hash)['author']['raw']

    def start_custom_pipeline(self, repo_name, build_branch, pipeline_name, variables):
        data = {
            'target': {
                "type": "pipeline_ref_target",
                "ref_type": "branch",
                "ref_name": build_branch,
                "selector": {
                    "type": "custom",
                    "pattern": pipeline_name
                }
            },
        }
        if variables:
            data.update({'variables': variables})
        print(data)
        url = '{}/repositories/{}/{}/pipelines/'.format(self.base_url, self.team, repo_name)
        req = requests.post(url, auth=self.auth, json=data)
        print(req)
        print(req.text)

    def _get_branch_info(self, repo_name, branch_name):
        url = '{}/repositories/{}/{}/refs/branches/{}'.format(
            self.base_url, self.team,
            repo_name, branch_name
        )
        req = requests.get(url, auth=self.auth)
        return req.json()

    def _get_commit_info(self, repo_name, commit_hash):
        url = '{}/repositories/{}/{}/commit/{}'.format(
            self.base_url, self.team,
            repo_name, commit_hash
        )
        req = requests.get(url, auth=self.auth)
        return req.json()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, required=True)
    parser.add_argument("--branch", type=str, default="master")
    parser.add_argument("--pipeline", type=str, required=True)
    parser.add_argument("--pipe-vars", type=str)
    return parser.parse_args()


def main():
    bb = BitBucket(os.getenv('BB_CLIENT'), os.getenv('BB_TOKEN'), 'neurohive')
    args = parse_args()
    pipe_vars = None
    if args.pipe_vars:
        pipe_vars = json.loads(args.pipe_vars)
    bb.start_custom_pipeline(args.repo, args.branch, args.pipeline, pipe_vars)


if __name__ == '__main__':
    main()
