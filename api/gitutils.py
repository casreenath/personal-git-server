import git
from flask import escape, jsonify, abort
import logging
import json
import os
import subprocess
from fsutils import FSActions

REPO_MASTER = os.getenv('REPO_MASTER')
CLONE_MASTER = os.getenv('CLONE_MASTER')
GIT_DIR="/var/www/git"


def test_call(requests):
    response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
    return jsonify(response)

def get_path_dirname(path):
    path = path.rstrip('/')
    dirname = path.split('/')[-1]
    return dirname

def sync_to_ib(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        auth_token = rec_dict['auth_token']
        dest_dir_path = rec_dict['dest_dir_path']
        repo_name = get_path_dirname(dest_dir_path)
        repos = os.listdir(f"{CLONE_MASTER}")
        if repo_name not in repos:
            raise Exception(f'Could not find the repo: {repo_name}')
        source_path = f"{CLONE_MASTER}/{repo_name}"
        fsa = FSActions(auth_token)
        fsa.push_to_ib(source_path, dest_dir_path)
        response['msg'] = "Sync to IB successful"
    except Exception as errmsg:
        logging.error(f"Error syncing to IB: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to sync to IB: {errmsg}'
        }
    return jsonify(response)

def sync_to_git(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        auth_token = rec_dict['auth_token']
        source_dir_path = rec_dict['source_dir_path']
        repo_name = get_path_dirname(source_dir_path)
        repos = os.listdir(f"{CLONE_MASTER}")
        if repo_name not in repos:
            raise Exception(f'Could not find the repo: {repo_name}')
        destination_path = f"{CLONE_MASTER}/{repo_name}"
        fsa = FSActions(auth_token)
        fsa.copy_folder(source_dir_path, destination_path)
        response['msg'] = "Sync to Git successful"
    except Exception as errmsg:
        logging.error(f"Error syncing to git: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to sync to git: {errmsg}'
        }
    return jsonify(response)

def create_repo(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        repo_name = str(rec_dict['repo_name'])
        result = subprocess.run(['mkrepo', f'{repo_name}'], stdout=subprocess.PIPE)
        if ' created in ' not in str(result.stdout):
            raise Exception(f"Error creating get repo: {result.stdout}")
        git_repos = os.listdir(GIT_DIR)
        if f'{repo_name}.git' in git_repos:
            response['msg'] = f"Successfully created repo: {repo_name}"
        else:
            raise Exception("Could not create repo")
    except Exception as errmsg:
        logging.error(f"Error creating repo: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to create repo: {errmsg}'
        }
    return jsonify(response)

# Load a repo

def load_repo(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        repo_name = str(rec_dict['repo_name'])
        new_repo = git.Repo(repo_name)
        response['msg'] = f"{repo_name} repo loaded"
    except Exception as errmsg:
        logging.error(f"Error loading repo: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to load repo: {errmsg}'
        }
    return jsonify(response)

def create_directory(dir_path):
    try:
        os.mkdir(dir_path)
        return True, None
    except Exception as errmsg:
        return None, str(errmsg)

def check_master_exists(repo_name):
    try:
        git_repos = os.listdir(GIT_DIR)
        if f"{repo_name}.git" in git_repos:
            return True, None
        return False, None
    except Exception as errmsg:
        return None, str(errmsg)  

def check_repo_exists(repo_name, is_clone=False):
    try:
        if not is_clone:
            path = f"{REPO_MASTER}"
        else:
            path = f"{CLONE_MASTER}"
        logging.info(f"Checking if {repo_name} exists in {path}")
        repos = os.listdir(path)
        logging.info(f"repos available: {repos}")
        if repo_name in repos:
            return True, None
        return False, None
    except Exception as errmsg:
        return None, str(errmsg)

# clone a repo

def clone_repo(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        repo_name = str(rec_dict['repo_name'])
        destination_path = str(rec_dict['destination_path'])
        clone_name = get_path_dirname(destination_path)
        # Check if specified repo exisits
        master_exists, err = check_master_exists(repo_name)
        if err:
            raise Exception(f"Error when checking for repo: {err}")
        if not master_exists:
            raise Exception(f"{repo_name} does not exist")

        # create folder in git service clones directory
        _, err = create_directory(f'{CLONE_MASTER}/{clone_name}')
        if err:
            raise Exception(f"Error creating directory : {err}")
        # Clone repo to clone directory
        git.Repo.clone_from(f"{GIT_DIR}/{repo_name}", f"{CLONE_MASTER}/{clone_name}")
        # TODO Need a funtion to copy folder and contents to filesystem
        # Copy files to filesystem
        response['msg'] = f"{clone_name} created"
    except Exception as errmsg:
        logging.error(f"Error cloning repo: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to clone repo: {errmsg}'
        }
    return jsonify(response)

def find_repo(repo_name):
    try:
        repo_exists, err = check_repo_exists(repo_name)
        if err: 
            raise Exception(f"Error in checking repos: {err}")
        if repo_exists:
            logging.info(f"Found in {REPO_MASTER}")
            return git.Repo(f'{REPO_MASTER}/{repo_name}'), None
        clone_exists, err = check_repo_exists(repo_name, True)
        if err: 
            raise Exception(f"Error in checking clones: {err}")
        if clone_exists:
            logging.info(f"Found in {CLONE_MASTER}")
            return git.Repo(f"{CLONE_MASTER}/{repo_name}"), None
        else:
            raise Exception(f'Repo {repo_name} not found')
    except Exception as errmsg:
        return None, str(errmsg)

# Commit code to repo
def commit_push(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        repo_name = str(rec_dict['repo_name'])
        commit_files = rec_dict['commit_files'] # list of files to be committed
        commit_message = str(rec_dict['commit_message'])
        # Copy files to clone
        # TODO commit and push should only work for clones
        target_repo, err = find_repo(repo_name)
        if err:
            raise Exception(f"Error finding the repo: {err}")
        logging.info("Found the repo object")
        target_repo.index.add(commit_files)
        if not target_repo.is_dirty():
            response['msg'] = f"Nothing to commit"
            return jsonify(response)
        target_repo.index.commit(commit_message)
        push_info = target_repo.remotes.origin.push()
        response['msg'] = f"{push_info[0].summary}"
    except Exception as errmsg:
        logging.error(f"Error in commit and push repo: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to commit and push repo: {errmsg}'
        }
    return jsonify(response)

# pull code
def pull(request):
    try:
        response = {
            'status': 'OK',
            'msg': '',
            'errmsg': ''
        }
        rec_dict = json.loads(request.data)
        repo_name = str(rec_dict['repo_name'])
        target_repo, err = find_repo(repo_name)
        if err:
            raise Exception(f"Error finding the repo: {err}")
        pull_info = target_repo.remotes.origin.pull()
        response['msg'] = f"{pull_info[0].note}"
    except Exception as errmsg:
        logging.error(f"Error in pull repo: {errmsg}")
        response = {
            'status': 'ERROR',
            'msg': '',
            'errmsg': f'Failed to pull repo: {errmsg}'
        }
    return jsonify(response)