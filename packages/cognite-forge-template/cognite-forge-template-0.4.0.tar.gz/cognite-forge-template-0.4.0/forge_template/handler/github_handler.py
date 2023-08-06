from typing import Dict, List, Tuple

import git
import requests

import forge_template.handler.git_utils as git_utils
import forge_template.handler.handler_utils as utils
from forge_template.handler.handler import BaseHandler


class GitHubHandler(BaseHandler):
    def __init__(self, name: str, config: Dict):
        self._principal = config["principal"]
        self._repo_name = config["repo_name"]
        self._is_organization = bool(config["is_organization"])
        api_token = config["token"]
        self._auth_header = {"Authorization": f"token {api_token}"}
        self._api_base_url = "https://api.github.com/"

        self._ssh_url: str = ""
        self._repos_to_add: List[str] = []
        self._remotes_to_rename: List[str] = []
        self._remotes_to_add: List[str] = []

        self._repos_added: List[Tuple[str, str]] = []
        self._remotes_renamed: List[str] = []
        self._remotes_added: List[str] = []
        self._repo = git.Repo()

        super().__init__(name=name, config=config)

    def setup(self) -> None:
        if len(self._repos_to_add) == 1:
            self.__create_repo(self._repo_name, self._principal, self._is_organization)
        git_utils.add_remotes(self._remotes_to_add, self._ssh_url, self._repo, self._remotes_added)
        git_utils.rename_remotes(self._remotes_to_rename, self._repo, self._remotes_renamed)
        git_utils.push_content_to_repo(self._repo, self._repo_name)

    def create_preview(self) -> None:
        if self.__check_if_repo_exists(self._repo_name, self._principal):
            self._repos_to_add.append(self._repo_name)
        git_utils.check_remotes_to_add(self._repo, self._repo_name, self._remotes_to_rename, self._remotes_to_add)

    def print_preview(self) -> None:
        utils.print_resource_to_add(self._repos_to_add, "Repository")
        utils.print_remotes_to_rename(self._remotes_to_rename)
        utils.print_resource_to_add(self._remotes_to_add, "Remote")
        utils.print_files_to_be_added()

    def rollback(self) -> None:
        if len(self._repos_added) == 1:
            self.delete_repo(self._repos_added[0][0], self._principal)
        git_utils.remove_remotes(self._remotes_added, self._repo)
        git_utils.rename_remotes(self._remotes_renamed, self._repo, [])

    def delete_all_resources(self):
        pass

    def __check_if_repo_exists(self, repo_name: str, principal: str) -> bool:
        git_cmd = git.cmd.Git()
        ssh_url = f"git@github.com:{principal}/{repo_name}"
        try:
            git_cmd.ls_remote(ssh_url)
            self._ssh_url = ssh_url
            return True
        except git.exc.GitCommandError:
            return False

    def __create_repo(self, repo_name: str, principal: str, is_organization: bool = True) -> None:
        url = self._api_base_url + (f"orgs/{principal}" if is_organization else "user") + "/repos"
        params = {"name": repo_name}

        response = requests.post(url=url, headers=self._auth_header, json=params)
        if response.status_code == 201:
            self._repos_added = [(repo_name, principal)]
            self._ssh_url = response.json()["ssh_url"]
            utils.print_success_created(repo_name, "Repository")
        else:
            raise RuntimeError(f"Github repository {repo_name} creation failed with status code {response.status_code}")

    def delete_repo(self, repo_name: str, principal: str) -> None:
        url = f"{self._api_base_url}repos/{principal}/{repo_name}"
        response = requests.delete(url, headers=self._auth_header)
        if response.status_code != 204:
            raise RuntimeError(f"Github repository {repo_name} deletion failed with status code {response.status_code}")
        else:
            utils.print_success_deleted(f"{principal}/{repo_name}", "Repository")
