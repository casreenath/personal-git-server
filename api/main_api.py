import logging
import os
import requests
from flask import Flask, request, jsonify
import gitutils as _git_utils


app = Flask(__name__)

@app.route('/create_repo', methods=['POST'])
def create_repo():
    return _git_utils.create_repo(request)

@app.route('/clone_repo', methods=['POST'])
def clone_repo():
    return _git_utils.clone_repo(request)

@app.route('/commit_push', methods=['POST'])
def commit_push():
    return _git_utils.commit_push(request)

@app.route('/pull', methods=['POST'])
def pull():
    return _git_utils.pull(request)

@app.route('/test_call', methods=['POST'])
def test_call():
    return _git_utils.test_call(request)

@app.route('/sync_to_git', methods=['POST'])
def sync_to_git():
    return _git_utils.sync_to_git(request)

@app.route('/sync_to_ib', methods=['POST'])
def sync_to_ib():
    return _git_utils.sync_to_ib(request)


if __name__ == "__main__":
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(debug=True, host=host, port=port)