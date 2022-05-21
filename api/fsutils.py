import requests
import json
import os

api_root = 'https://www.instabase.com/api/v1/drives/'

class FSActions:

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def copy_folder(self,folder_path, destination_path):
        # os.mkdir(destination_path+"/"+folder_path.split('/')[-1])
        resp = self.list_dir(folder_path)
        self.download_files_from_dir(resp, destination_path)

    def read_file(self,filepath):
        api_args = dict(
            type='file',
            get_content=True,
            range=''
        )

        headers = {
            'Authorization': 'Bearer {0}'.format(self.auth_token),
            'Instabase-API-Args': json.dumps(api_args)
        }
        url = api_root + filepath

        r = requests.get(url, headers=headers)

        # resp = json.loads(r.headers['Instabase-API-Resp'])
        data = r.content
        return data

    def download_files_from_dir(self,response, dir):
        for item in response['nodes']:
            if item['type'] == 'folder':
                resp = self.list_dir(item['full_path'])
                os.mkdir(dir + '/' + item['name'])
                self.download_files_from_dir(resp, dir + '/' + item['name'])
            else:
                data = self.read_file(item['full_path'])
                f = open(dir + '/' + item['name'], "wb")
                f.write(data)
                f.close()

    def list_dir(self,root):
        url = api_root + root

        api_args = dict(
            type='folder',
            get_content=True,
            get_metadata=False,
            start_page_token=''
        )

        headers = {
            'Authorization': 'Bearer {0}'.format(self.auth_token),
            'Instabase-API-Args': json.dumps(api_args)
        }

        resp = requests.get(url, headers=headers).json()
        return resp

    def create_file(self,filename, content):
        url = api_root  + filename
        print(url)

        api_args = dict(
            type='file',
            cursor=0,
            if_exists='overwrite',
            mime_type='pdf'
        )

        headers = {
            'Authorization': 'Bearer {0}'.format(self.auth_token),
            'Instabase-API-Args': json.dumps(api_args)
        }

        data = content
        resp = requests.post(url, data=data, headers=headers).json()
        print(resp)

    def push_to_ib(self,localpath,ib_path):
        for path, subdirs, files in os.walk(localpath):
            for name in files:
                #print(os.path.join(path, name))
                f = open(os.path.join(path, name), "r")
                relative_path = path.replace(localpath, "")
                target_path = ib_path+ '/' +os.path.join(relative_path, name)
                self.create_file(target_path, f.read())
                f.close()
