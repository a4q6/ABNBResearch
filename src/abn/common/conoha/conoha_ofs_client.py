from dataclasses import dataclass
import requests
import json
import os
from pathlib import Path
from typing import List, Dict, Collection, Callable, Union, Optional


class ConohaOFSClient:

    def __init__(self, auth):
        """
        
        Args:
            auth (CONOHA): Authentification constants. defined by  
            ```
                @dataclass
                class CONOHA:
                    USERNAME = ""
                    PASSWORD = ""
                    TENANTID = ""
                    TOKENURL = ""
                    OBJECT_STORAGE = 'https://object-storage.tyo2.conoha.io/***'
            ```
        """
        self.auth = auth
        self.token = self.get_token()
        
        
    def get_token(self) -> requests.models.Response:
        """ Get HTTP api token
        
        Returns:
            requests.models.Response: 
        """
        headers = {'Accept': 'application/json'}
        data = '{"auth":{"passwordCredentials":{"username":"%s","password":"%s"},"tenantId":"%s"}}' % (self.auth.USERNAME, self.auth.PASSWORD, self.auth.TENANTID)
        response = requests.post(self.auth.TOKENURL, headers=headers, data=data)
        data = response.json()
        return json.dumps(data["access"]["token"]["id"], indent=4).replace('\"', '')
    
    
    def create_container(self, container: str) -> requests.models.Response:
        """ Create new container(=top-level folder).
        
        Args:
            container (str): container name
        
        Returns:
            requests.models.Response: 
        """
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token}
        response = requests.put(os.path.join(self.auth.OBJECT_STORAGE, container), headers=headers)
        return response
    
    
    def get_object(self, uri: str, outputpath: str = ".", omit_folders: bool = False) -> requests.models.Response:
        """ Download object to local.

        Args:
            uri (str): object uri.
            outputpath (str, optional):  Defaults to ".".
            omit_folders (bool, optional):  use folder path or not. Defaults to False.

        Returns:
            requests.models.Response:
        """
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token}
        # get contents
        response = requests.get(os.path.join(self.auth.OBJECT_STORAGE, uri), headers=headers)
        if response.status_code == 200:
            # write contents
            filepath = Path(outputpath).joinpath(uri) if not omit_folders else Path(outputpath).joinpath(uri.split("/")[-1])
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(4096):  # chunk sizeは任意で指定可能
                    f.write(chunk)
        return response
    
    
    def delete_object(self, uri: str) -> requests.models.Response:
        """ Delete remote object. Can delete blank container as well.
        
        Args:
            uri (str): 
        
        Returns:
            requests.models.Response: 
        """
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token}
        response = requests.delete(os.path.join(self.auth.OBJECT_STORAGE, uri), headers=headers)
        return response
    
    
    def put_object(self, target_file: str, put_path: str) -> requests.models.Response:
        """ Upload local object to remote.
        
        Args:
            target_file (str): local path to target file.
            put_path (str, optional): where to put file.
            
        Returns:
            requests.models.Response:
        """
        assert (not "." in put_path), "argument `put_path` must be a directory, not a file."
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token}
        with open(target_file, 'rb') as f:
            response = requests.put(os.path.join(self.auth.OBJECT_STORAGE, put_path, target_file.split("/")[-1]), headers=headers, data=f)
        return response
    
    
    def list_objects(self, container: str, path: str = "") -> Union[List[Dict], requests.models.Response]:
        """ List objects under `cotainer/path`.
        
        Args:
            container (str): container name
            path (str): 
        
        Returns:
            Union[List[Dict], requests.models.Response]: return object name list.
        """
        assert not "/" in container, "must pass `container` name, not a path"
        headers = {'X-Auth-Token': self.token}
        params = {('format', 'json'), ('prefix', path)}
        response = requests.get(os.path.join(self.auth.OBJECT_STORAGE, container), headers=headers, params=params)
        if response.status_code == 200:
            return eval(response.content.decode())
        else:
            return response
    
    
    def enable_public_access(self, container: str) -> requests.models.Response:
        """ 
        
        Args:
            container (str):
            
        Returns:
            requests.models.Response:
        """
        assert not "/" in container, "must pass `container` name, not a path"
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token, 'X-Container-Read': '.r:*'}
        response = requests.post(os.path.join(self.auth.OBJECT_STORAGE, container), headers=headers)
        return response
    
    
    def disable_public_access(self, container: str) -> requests.models.Response:
        """
        
        Args:
            container (str):
        
        Returns:
            requests.models.Response:
        """
        assert not "/" in container, "must pass `container` name, not a path"
        headers = {'Accept': 'application/json', 'X-Auth-Token': self.token, 'X-Remove-Container-Read': '.r:*'}
        response = requests.post(os.path.join(self.auth.OBJECT_STORAGE, container), headers=headers)
        return response
