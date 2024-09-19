import re
import logging
import asyncio
import traceback
from typing import List
from urllib.parse import urlparse

logger = logging.getLogger('weberist.generic.utils')

async def cancel_task(task: asyncio.Task):
    if not task.done():
        task_name = task.get_name()
        try:
            task.cancel()
            logger.debug("Cancelling task %s", task_name)
            await asyncio.sleep(0.1)
        except asyncio.CancelledError as err:
            logger.debug("Cancelling task %s failed: ", err)

async def gather_and_handle(tasks: List[asyncio.Task],
                            results: List = None,
                            raise_error: bool = True):
    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_EXCEPTION
    )
    task_name = ''
    if results is None:
        results = []
    if done:
        for task in done:
            err = task.exception()
            if err:
                task_name = task.get_name()
                logger.error(
                    'Task %s failed. ERROR: %s. Traceback: %s',
                    task_name,
                    err,
                    traceback.format_exc()
                )
                await cancel_task(task)
                if raise_error:
                    for task_ in tasks:
                        await cancel_task(task_)
                    raise err
                results.append(None)
                continue
            results.append(task.result())
    if pending:
        return await gather_and_handle(pending, results, raise_error)
    return results


def run_async(coro, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    except RuntimeError:
        try:
            return asyncio.run(coro(*args, **kwargs))
        except RuntimeError:
            try:
                import nest_asyncio  # pylint --disable=import-outside-toplevel
                nest_asyncio.apply()
                return asyncio.run(coro(*args, **kwargs))
            except (ImportError, ModuleNotFoundError) as err:
                logger.error(err)
                logger.warning("Install nest_asyncio to run nested async.")
                raise err

def extract_base_url(text: str) -> str:
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, text)

    if not urls:
        return None

    parsed_url = urlparse(urls[0])
    base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    
    return base_url