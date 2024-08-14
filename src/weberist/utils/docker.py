import json
from typing import Iterator
from pathlib import Path

import docker

from weberist.base.config import (
    DOCKER_DIR,
    CHROME_IMAGE,
    DOCKER_NETWORK,
    CHROME_VERSIONS,
)


def create_network(name: str = None):
    if name is None:
        name = DOCKER_NETWORK
    client = docker.from_env()
    return client.networks.create(name)

def create_chrome_dockerfile(name: str = None, chrome_version: str = None):

    path = DOCKER_DIR / "Dockerfile-chrome"
    if name is None:
        name = 'Dockerfile'
    if chrome_version is None:
        chrome_version = CHROME_VERSIONS[-1]
    with open(path, 'r', encoding='utf-8') as dockerfile_chrome:
        dockerfile_content = dockerfile_chrome.read().format(
            version=chrome_version,
            localstorage='./data/localstorage',
            entrypoint='./data/chrome-entrypoint.sh'
        )
        path = DOCKER_DIR / name
        with open(path, 'w', encoding='utf-8') as dockerfile:
            dockerfile.write(dockerfile_content)

def create_browsers_json(chrome_version: str = None,
                         target_path: str | Path = '.'):
    
    if chrome_version is None:
        chrome_version = CHROME_VERSIONS[-1]

    browsers_template = DOCKER_DIR / 'browsers'
    browsers_json = target_path / 'browsers.json'
    with open(browsers_template, encoding='utf-8') as json_template:
        browsers = json_template.read().format(version=chrome_version)
        content = json.loads(browsers)
        with open(browsers_json, 'w', encoding='utf-8') as json_file:
            json.dump(content, json_file, indent=4, ensure_ascii=False)

def create_selenoid_chrome_compose(name: str = None,
                                   dockerfile_name: str = None,
                                   network_name: str = None,
                                   chrome_version: str = None,
                                   target_path: str | Path = '.'):
    
    if isinstance(target_path, str):
        target_path = Path(target_path)
    if not target_path.exists():
        target_path.mkdir()
    if not target_path.is_dir():
        raise FileExistsError(f"A file named '{target_path}' exists.")
    target = target_path / 'target'
    video = target_path / 'video'
    logs = target_path / 'logs'
    if not target.exists():
        target.mkdir()
    if not video.exists():
        video.mkdir()
    if not logs.exists():
        logs.mkdir()
    
    if name is None:
        name = 'docker-compose.yml'
    if network_name is None:
        network_name = 'weberist'
    
    create_chrome_dockerfile(dockerfile_name, chrome_version)
    create_browsers_json(chrome_version, target_path)

    template_compose = DOCKER_DIR / "docker-compose-selenoid.yml"
    with open(template_compose, 'r', encoding='utf-8') as docker_compose_file:
        
        dockerfile_content = docker_compose_file.read().format(
            network=network_name
        )
        target_name = target_path / name
        with open(target_name, 'w', encoding='utf-8') as target:
            target.write(dockerfile_content)

def setup_selenoid_chrome(dockerfile_name: str = None,
                          dockercompose_name: str = None,
                          network_name: str = None,
                          chrome_version: str = CHROME_VERSIONS[-1],
                          target_path: str | Path = '.'):
    
    create_chrome_dockerfile(name=dockerfile_name)
    network = create_network(name=network_name)
    create_selenoid_chrome_compose(
        dockercompose_name,
        dockerfile_name,
        network_name,
        chrome_version,
        target_path,
    )
    
    client = docker.from_env()
    image, log = client.images.build(
        path=str(DOCKER_DIR.absolute()),
        tag=f"{CHROME_IMAGE.format(version=chrome_version)}:latest"
    )
    return image, network, log
