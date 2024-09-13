import logging
import asyncio

logger = logging.getLogger('weberist.generic.utils')


def run_async(coro, *args, **kwargs):
    task = None
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro(*args, **kwargs))
    except RuntimeError:
        task = coro(*args, **kwargs)
    try:
        asyncio.run(task)
    except RuntimeError:
        try:
            # NOTE: this allows running in jupyter without using 'await'
            import nest_asyncio  # pylint --disable=import-outside-toplevel
            nest_asyncio.apply()
            asyncio.run(task)
        except (ImportError, ModuleNotFoundError) as err:
            logger.error(err)
            logger.warning("Must install nest_asyncio for running in Jupyter")
            raise err
    return task.result()