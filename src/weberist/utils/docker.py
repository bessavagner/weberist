import os
import json
import time
import signal
import logging
import subprocess
import threading
from pathlib import Path
from typing import Callable

import docker

from weberist import ChromeDriver
from weberist.base.config import (
    DOCKER_DIR,
    CHROME_IMAGE,
    DOCKER_NETWORK,
    CHROME_VERSIONS,
    DOCKER_COMPOSE,
    CONTAINER_SELENOID,
    CONTAINER_SELENOID_UI,
)
from weberist.generic.types import WebDriver


SELENOID_STARTED_CUE = "[INIT] [Listening on :4444]"
is_selenoid_up = False

logger = logging.getLogger('standard')

def create_network(name: str = None):
    if name is None:
        name = DOCKER_NETWORK
    client = docker.from_env()
    for network in client.networks.list():
        if name == network.name:
            logger.warning("Network '%s' already existis.", name)
            return network
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
        name = DOCKER_COMPOSE
    if network_name is None:
        network_name = DOCKER_NETWORK
    
    create_chrome_dockerfile(dockerfile_name, chrome_version)
    create_browsers_json(chrome_version, target_path)

    template_compose = DOCKER_DIR / "docker-compose-selenoid.yml"
    with open(template_compose, 'r', encoding='utf-8') as docker_compose_file:
        
        dockerfile_content = docker_compose_file.read().format(
            network=network_name,
            container_selenoid=CONTAINER_SELENOID,
            container_selenoid_ui=CONTAINER_SELENOID_UI,
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

def run_docker_compose(path: str = None, build: bool = False):
    # Start the Docker Compose process
    command = ["docker", "compose", "up", "--build"]
    if path is not None:
        command = command[:2] + ["-f", str(path)] + command[2:]
    if not build:
        command.pop()
    print(" ".join(command))
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
                print(f"stdout: {line}", end='')
            else:
                print(f"stderr: {line}", end='')
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
            logger.info("🕒 Waiting selenoid...")


def run_selenoid_driver_task(driver_task: Callable,
                             *args,
                             dockerfile_name: str = None,
                             dockercompose_name: str = None,
                             network_name: str = None,
                             chrome_version: str = CHROME_VERSIONS[-1],
                             target_path: str | Path = None,
                             **kwargs):
    
    global is_selenoid_up
    is_selenoid_up = False
    
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'selenoid' in container.name:
            is_selenoid_up = True
            break

    process = None
    path = None
    if not is_selenoid_up:
        create_compose = True
        if target_path is None:
            target_path = DOCKER_DIR
        if dockercompose_name is None:
            dockercompose_name = DOCKER_COMPOSE
        for item in target_path.glob("*"):
            if dockercompose_name == item.name:
                create_compose = False
                break
        if create_compose:
            setup_selenoid_chrome(
                dockerfile_name,
                dockercompose_name,
                network_name,
                chrome_version,
                target_path
            )
    
        create_network_ = True
        if network_name is None:
            network_name = DOCKER_NETWORK
        for network in client.networks.list():
            if network_name == network.name:
                create_network_ = False
                break
        if create_network_:
            create_network(network_name)
        
        build = True
        for container in client.containers.list(all=True):
            if CONTAINER_SELENOID == container.name:
                build = False
                break
        path = Path(target_path) / dockercompose_name
        (
            process, stdout_thread, stderr_thread, clean_up
        ) = run_docker_compose(path, build)
        wait_selenoid()

    try:
        driver = ChromeDriver(remote=True)
        result = driver_task(driver, *args, **kwargs)
        return result
    finally:
        if process:
            stop_docker_compose(process, path)
            clean_up()
            stdout_thread.join()
            stderr_thread.join()
