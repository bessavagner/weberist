import os
import json
import time
import signal
import asyncio
import asyncio
import logging
import tarfile
import threading
import tarfile
import threading
import subprocess
from io import BytesIO
from io import BytesIO
from shutil import copyfile
from pathlib import Path
from typing import Callable, List, Dict

import docker

from weberist import ChromeDriver
from weberist.base.config import (
    DATA_DIR,
    DOCKER_DIR,
    DOCKER_FILE_BROWSER,
    LOCALSTORAGE,
    BROWSER_IMAGE,
    LOCALSTORAGE,
    BROWSER_IMAGE,
    CHROME_IMAGE,
    DOCKER_NETWORK,
    CHROME_VERSIONS,
    FIREFOX_VERSIONS,
    DOCKER_COMPOSE,
    CONTAINER_SELENOID,
    CONTAINER_SELENOID_UI,
    BROWSER_DICT,
)
from weberist.generic.types import TypeBrowser
from weberist.generic.utils import run_async, gather_and_handle


SELENOID_STARTED_CUE = "[INIT] [Listening on :4444]"
is_selenoid_up = False

logger = logging.getLogger('standard')
client_logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)
client_logger.setLevel(logging.DEBUG)


def create_network(name: str = None, client: docker.DockerClient = None):

    if name is None:
        name = DOCKER_NETWORK
    if client is None:
        client = docker.from_env()
    for network in client.networks.list():
        if name == network.name:
            client_logger.warning("Network '%s' already exists.", name)
            return network
    return client.networks.create(name)

def create_dockerfile(name: str = None,
                      browser: str = None,
                      version: str = None,
                      target_path: str | Path = None):
    
    target_path = target_path or DATA_DIR
    if not isinstance(target_path, Path):
        target_path = Path(target_path)

    with open(DOCKER_FILE_BROWSER, 'r', encoding='utf-8') as dockerfile_chrome:
        localstorage = target_path / 'localstorage'
        localstorage.mkdir(parents=True, exist_ok=True)
        entrypoint = target_path / f'{browser}-entrypoint.sh'
        copyfile(DOCKER_DIR / f'{browser}-entrypoint.sh', entrypoint)
        dockerfile_content = dockerfile_chrome.read().format(
            version=version,
            browser=browser,
            localstorage='./localstorage',
            entrypoint=f'./{browser}-entrypoint.sh'
        )

        name = name or 'Dockerfile'
        with open(target_path / name, 'w', encoding='utf-8') as dockerfile:
            dockerfile.write(dockerfile_content)
    
def create_chrome_dockerfile(name: str = None,
                             chrome_version: str = None,
                             target_path: str | Path = None):

    chrome_version = chrome_version or CHROME_VERSIONS[-1]
    create_dockerfile(name, 'chrome', chrome_version, target_path)

def create_firefox_dockerfile(name: str = None,
                              firefox_version: str = None,
                              target_path: str | Path = None):

    firefox_version = firefox_version or FIREFOX_VERSIONS[-1]
    create_dockerfile(name, 'firefox', firefox_version, target_path)
                        
def create_browser_image(browser: str,
                         version: int,
                         client: docker.DockerClient = None,
                         target_path: str | Path = None):

    image, log = None, None
    create = True
    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    tag = BROWSER_IMAGE.format(
        browser=browser, version=version
    )
    # tag = f"{tag}:latest"
    for image_ in client.images.list():
        if image_ and len(image_.tags) > 0:
            if tag == image_.tags[0]:
                create = False
                image = image_
                break
    if create:
        client_logger.info("Creating image '%s'", tag)
        
        name = f"Dockerfile-{browser}-{version}"
        create_dockerfile(
            name=name,
            browser=browser,
            version=version,
            target_path=target_path
        )
        dockerfile_obj = BytesIO()
        with tarfile.open(fileobj=dockerfile_obj, mode='w') as tar:
            for file_path in target_path.rglob('*'):
                arcname = file_path.relative_to(target_path)
                tar.add(file_path, arcname=arcname)
        dockerfile_obj.seek(0)
        
        image, log = client.images.build(
            fileobj=dockerfile_obj,
            dockerfile=name,
            custom_context=True,
            tag=tag,
            rm=True,
            nocache=True,
            quiet=False,
        )
        
        client_logger.info("Image '%s' crated!", tag)
    
    return image, log
                        
async def create_browser_image_async(browser: str,
                                     version: int,
                                     client: docker.DockerClient = None,
                                     target_path: str | Path = None):
    return await asyncio.to_thread(
        create_browser_image,
        browser,
        version,
        client,
        target_path,
    )

def create_browsers_images(browsers: Dict[str, TypeBrowser],
                           client: docker.DockerClient = None,
                           target_path: str | Path = None):

    data = {
        "images": [],
        "logs": []
    }

    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    for browser, info in browsers.items():
        for version in info['versions']:
            image, log = create_browser_image(
                browser, version, client, target_path
            )
            data['images'].append(image)
            data['logs'].append(log)
    return data

async def create_browsers_images_async(browsers: Dict[str, TypeBrowser],
                                       client: docker.DockerClient = None,
                                       target_path: str | Path = None,
                                       n_batches: int = 4):

    data = {
        "images": [],
        "logs": []
    }

    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    
    tasks = []
    results = []
    counter = 0
    for browser, info in browsers.items():
        for version in info['versions']:
            tasks.append(
                asyncio.create_task(
                    create_browser_image_async(
                        browser, version, client, target_path
                    ),
                    name=f"{browser}-{version}"
                )
            )
            counter += 1
            if counter == n_batches:
                result = await gather_and_handle(tasks, raise_error=False)
                results.extend(result)
                tasks = []
    if len(tasks) > 0:
        result = await gather_and_handle(tasks, raise_error=False)
        results.extend(result)
    for result in results:
        if result is not None:
            image, log = result
            data['images'].append(image)
            data['logs'].append(log)
    return data

def create_browser_config_dict(browser: str,
                               versions: List[int],
                               default: int = 0,
                               **kwargs):
    browser_config = {}
    images = [f"{browser}_{version}.0" for version in versions]
    browser_config["default"] = images[default]
    browser_config["versions"] = {}
    for image in images:
        browser_config["versions"][image] = BROWSER_DICT
        browser_config["versions"][image]["image"] = f"weberist-{image}"
        for key, value in kwargs.items():
            browser_config["versions"][image][key] = value
    return browser_config

def create_browsers_json(browsers: Dict[str, TypeBrowser],
                         target_path: str | Path = None):
    browsers_json = {}
    for browser, info in browsers.items():
        kwargs = {}
        if 'kwargs' in info:
            kwargs = info['kwargs']
        browsers_json[browser] = create_browser_config_dict(
            browser,
            info['versions'],
            info['default'],
            **kwargs
        )
    target_path = target_path or DATA_DIR
    if not isinstance(target_path, Path):
        target_path = Path(target_path)

    path = target_path / 'browsers.json'
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(browsers_json, json_file, indent=4, ensure_ascii=False)

def create_selenoid_compose(browsers: Dict[str, TypeBrowser],
                            name: str = None,
                            network_name: str = None,
                            client: docker.DockerClient = None,
                            target_path: str | Path = None,):

    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    target = target_path / 'target'
    video = target_path / 'video'
    logs = target_path / 'logs'
    target.mkdir(parents=True, exist_ok=True)
    video.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    
    create_browsers_json(browsers, target_path)
    
    # data = create_browsers_images(browsers, client, target_path)
    data = run_async(
        create_browsers_images_async, browsers, client, target_path
    )
    name = name or DOCKER_COMPOSE
    network_name = network_name or DOCKER_NETWORK

    template_compose = DOCKER_DIR / "docker-compose-selenoid.yml"
    with open(template_compose, 'r', encoding='utf-8') as docker_compose_file:
        content = docker_compose_file.read().format(network=network_name)
        target_name = target_path / name
        with open(target_name, 'w', encoding='utf-8') as compose_file:
            compose_file.write(content)
    
    return data
                                   
def create_selenoid_chrome_compose(name: str = None,
                                   dockerfile_name: str = None,
                                   network_name: str = None,
                                   chrome_version: str = None,
                                   target_path: str | Path = None):

    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    target = target_path / 'target'
    video = target_path / 'video'
    logs = target_path / 'logs'
    target.mkdir(parents=True, exist_ok=True)
    video.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    name = name or DOCKER_COMPOSE
    network_name = network_name or DOCKER_NETWORK

    create_chrome_dockerfile(dockerfile_name, chrome_version, target_path)
    create_browsers_json(chrome_version, target_path)

    template_compose = DOCKER_DIR / "docker-compose-selenoid.yml"
    with open(template_compose, 'r', encoding='utf-8') as docker_compose_file:

        dockerfile_content = docker_compose_file.read().format(
            network=network_name,
            # NOTE: conflict if already created:
            container_selenoid=CONTAINER_SELENOID,
            container_selenoid_ui=CONTAINER_SELENOID_UI,
        )
        target_name = target_path / name
        with open(target_name, 'w', encoding='utf-8') as target:
            target.write(dockerfile_content)
        
                        
def create_chrome_image(chrome_version: str = CHROME_VERSIONS[-1],
                        client: docker.DockerClient = None,
                        target_path: str | Path = None):

    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    image = None
    log = [{}]
    create = True
    name = f"{CHROME_IMAGE.format(version=chrome_version)}:latest"
    for image_ in client.images.list():
        if image_ and len(image_.tags) > 0:
            if name == image_.tags[0]:
                create = False
                image = image_
                break
    if create:
        client_logger.info("Creating chrome image '%s'", name)
        image, log = client.images.build(
            path=str(target_path.absolute()),
            tag=name,
            rm=True,
            nocache=True,
            quiet=False,
        )
        client_logger.info("Chrome image '%s' crated!", name)
    return image, log

def setup_selenoid(browsers: Dict[str, TypeBrowser],
                   network_name: str = None,
                   target_path: str | Path = None,
                   client: docker.DockerClient = None):

    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)

    network = create_network(name=network_name, client=client)
    data = create_selenoid_compose(browsers, network_name, target_path)
    
    data['network'] = network
    
    return data

def setup_selenoid_chrome(dockerfile_name: str = None,
                          dockercompose_name: str = None,
                          network_name: str = None,
                          chrome_version: str = CHROME_VERSIONS[-1],
                          target_path: str | Path = None,
                          client: docker.DockerClient = None):

    client = client or docker.from_env()
    target_path = target_path or DATA_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)

    network = create_network(name=network_name, client=client)

    create_selenoid_chrome_compose(
        dockercompose_name,
        dockerfile_name,
        network_name,
        chrome_version,
        target_path,
    )

    image, log = create_chrome_image(chrome_version, client)

    return image, network, log

def run_docker_compose(path: str = None, build: bool = False):
    # Start the Docker Compose process
    command = ["docker", "compose", "up", "--build"]
    if path is not None:
        command = command[:2] + ["-f", str(path)] + command[2:]
    if not build:
        command.pop()
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # Use text mode for easier handling of strings
        bufsize=1,  # Line buffering
        universal_newlines=True  # Ensure newlines are handled properly
    )

    # Define a function to print output in real-time
    def print_output(pipe, stream):
        for line in iter(pipe.readline, ''):
            if stream == 'stdout':
                client_logger.info("stdout: %s", line)
            else:
                client_logger.info("stderr: %s", line)
            if SELENOID_STARTED_CUE in line:
                global is_selenoid_up
                is_selenoid_up = True
        pipe.close()

    # Start threads to handle stdout and stderr
    stdout_thread = threading.Thread(target=print_output, args=(process.stdout, 'stdout'))
    stderr_thread = threading.Thread(target=print_output, args=(process.stderr, 'stderr'))

    stdout_thread.start()
    stderr_thread.start()

    # Handle process termination and cleanup
    def cleanup():
        if process.poll() is None:  # Check if process is still running
            os.kill(process.pid, signal.SIGTERM)  # Send termination signal
            process.wait()  # Wait for the process to terminate

    return process, stdout_thread, stderr_thread, cleanup

def stop_docker_compose(process, path: str = None):
    # Stop the Docker Compose process
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()

    # Optionally, you can shut down the containers cleanly
    command = ["docker", "compose", "down"]
    if path is not None:
        command = command[:2] + ["-f", str(path)] + command[2:]
    subprocess.run(command, check=True)

def wait_selenoid(quiet=False):

    global is_selenoid_up

    while not is_selenoid_up:
        time.sleep(1)
        if not quiet:
            client_logger.debug("🕒 Waiting selenoid...")


def run_selenoid_driver_task(driver_task: Callable,
                             *args,
                             dockercompose_name: str = None,
                             network_name: str = None,
                             target_path: str | Path = None,
                             chrome_kwargs: dict = None,
                             **kwargs):

    global is_selenoid_up
    is_selenoid_up = False

    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'selenoid' in container.name:
            is_selenoid_up = True
            break

    dockercompose_name = dockercompose_name or DOCKER_COMPOSE
    target_path = target_path or DATA_DIR  # DOCKER_DIR
    if isinstance(target_path, str):
        target_path = Path(target_path)
    browsers = {
        'chrome': TypeBrowser(versions=[CHROME_VERSIONS[-1]], default=-1)
    }
    setup_selenoid(
        browsers,
        network_name,
        target_path,
        client
    )

    path = None
    process = None
    if not is_selenoid_up:
        client_logger.debug("Selenoid is not up")

        build = True
        path = Path(target_path) / dockercompose_name
        for container in client.containers.list(all=True):
            if CONTAINER_SELENOID == container.name:
                build = False
                break
        (
            process, stdout_thread, stderr_thread, clean_up
        ) = run_docker_compose(path, build)
        wait_selenoid()
    else:
        client_logger.debug("Selenoid is already up")

    try:
        if chrome_kwargs is None:
            chrome_kwargs = {}
        if 'localstorage' not in chrome_kwargs:
            chrome_kwargs['localstorage'] = LOCALSTORAGE
        driver = ChromeDriver(remote=True, **chrome_kwargs)
        result = driver_task(driver, *args, **kwargs)
        return result
    finally:
        if process:
            stop_docker_compose(process, path)
            clean_up()
            stdout_thread.join()
            stderr_thread.join()
