import logging
import shutil
import binascii
from pathlib import Path

logger = logging.getLogger("weberist.base.stealth")


def hex_dump_to_bytes(hex_dump: str) -> bytes:
    # Convert a hex dump to bytes
    hex_str = "".join(hex_dump.split())
    return binascii.unhexlify(hex_str)


def remove_cdc(chromedriver_path: str):

    chromedriver_path = Path(chromedriver_path)

    # Create a backup of the original ChromeDriver
    backup_path = chromedriver_path.with_suffix(".bak")
    modified_path = chromedriver_path.with_name(chromedriver_path.name + ".modified")
    shutil.copy(chromedriver_path, backup_path)

    with chromedriver_path.open("rb") as binary_file:
        binary_content = binary_file.read()

    # Create a hex dump of the binary content
    hex_dump = binascii.hexlify(binary_content).decode("ascii")
    logger.info("Found %d occurrences of '$cdc_' and %d occurrences of 'webdriver'", hex_dump.count('246364635f'), hex_dump.count('777562647276657265'))

    # Replace occurrences of '$cdc_' with 'xymu' in the hex dump
    hex_dump = hex_dump.replace("246364635f", "7879646d75")
    # Replace occurrences of 'webdriver' with 'xyzabc'
    hex_dump = hex_dump.replace("777562647276657265", "78797a616263")

    # Convert the modified hex dump back to binary
    modified_binary_content = hex_dump_to_bytes(hex_dump)
    try:
        # Convert the modified hex dump back to binary
        modified_binary_content = hex_dump_to_bytes(hex_dump)

        with modified_path.open("wb") as binary_file:
            binary_file.write(modified_binary_content)

        # Replace the original file with the modified file
        shutil.move(modified_path, chromedriver_path)

        chromedriver_path.chmod(0o755)
        logger.info("Modified ChromeDriver at %s", chromedriver_path)

        with chromedriver_path.open("rb") as binary_file:
            binary_content = binary_file.read()
        hex_dump = binascii.hexlify(binary_content).decode("ascii")
        logger.info("Found %d occurrences of '$cdc_' and %d occurrences of 'webdriver'", hex_dump.count('246364635f'), hex_dump.count('777562647276657265'))

    except Exception as e:
        logger.error("An error occurred while modifying ChromeDriver: %s", e)
        # Clean up the modified file if something goes wrong
        if modified_path.exists():
            modified_path.unlink()
