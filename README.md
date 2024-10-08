# Weberist

Weberist is a powerful web automation and scraping framework built on top of Selenium. It provides a flexible and easy-to-use interface for managing web drivers, handling browser profiles, and executing automated tasks in a variety of browsers, including Chrome and Firefox. This README will guide you through the installation, configuration, and usage of Weberist, including examples of how to use ChromeDriver and FirefoxDriver.

## Table of Contents

- [Weberist](#weberist)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Using ChromeDriver](#using-chromedriver)
    - [Using FirefoxDriver](#using-firefoxdriver)
    - [Running Docker Tasks](#running-docker-tasks)
  - [Modules](#modules)
    - [Data Management](#data-management)
    - [Driver Management](#driver-management)
    - [Docker Management](#docker-management)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- Support for multiple browsers (Chrome, Firefox, etc.)
- Easy management of browser profiles and local storage
- Integration with Docker for running headless browser instances
- Customizable user agents and window sizes
- Robust error handling and logging
- Stealthiness: out of the box stealth chrome driver. It passes tests like:
  * [https://fingerprintjs.github.io/BotD/main/](https://fingerprintjs.github.io/BotD/main/)
  * [https://pixelscan.net/](https://pixelscan.net/)
  * [https://deviceandbrowserinfo.com/are_you_a_bot](https://deviceandbrowserinfo.com/are_you_a_bot)

## Installation

To install Weberist, you can clone the repository and install the required dependencies using pip:

```bash
git clone https://github.com/yourusername/weberist.git
cd weberist
pip install -r requirements.txt
```

Or install via pip:

```bash
pip install weberist
```
Make sure you have Docker installed and running if you plan to use the Docker features.

## Configuration

Weberist uses a configuration file located in the `config.py` module. You can customize various settings such as the root directory, data directory, and browser versions.

## Usage

### Using ChromeDriver

To use ChromeDriver, you can create an instance of `ChromeDriver` and perform various actions like navigating to a URL, clicking elements, and sending keys.

```python
from weberist.drivers import ChromeDriver

with ChromeDriver() as driver:
    driver.goto("https://example.com")
    element = driver.select("some-element-id")
    driver.click(element)
```

### Using FirefoxDriver

Similarly, you can instantiate a Firefox driver using the `BaseDriver` class.

```python
from weberist.drivers import BaseDriver

with BaseDriver(browser='firefox') as driver:
    driver.goto("https://example.com")
    element = driver.select("some-element-id")
    driver.click(element)
```

### Running Docker Tasks

Weberist allows you to run browser instances in Docker containers using Selenoid. You can use the `run_selenoid_driver_task` function to execute tasks in a Dockerized environment.

```python
from weberist.docker import run_selenoid_driver_task

def my_driver_task(driver):
    driver.goto("https://example.com")
    # Perform more actions...

result = run_selenoid_driver_task(my_driver_task, dockercompose_name='docker-compose.yml')
```

## Modules

### Data Management

The `data.py` module provides classes for managing user agents, window sizes, and profile storage. You can customize the data used for your web automation tasks.

### Driver Management

The `drivers.py` module contains the `BaseDriver` class and specific driver implementations like `ChromeDriver`. It handles the instantiation and management of web drivers.

### Docker Management

The `docker.py` module provides functions for creating Docker images, managing Docker containers, and running browser instances in a Dockerized environment.

## Contributing

We welcome contributions to Weberist! If you have suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
