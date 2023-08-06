# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hadrosaur']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hadrosaur',
    'version': '0.0.3',
    'description': '[WIP] Manage a large amount of computed resources, such as files, imports, etc.',
    'long_description': '# hadrosaur — computed resource management\n\n![logo](docs/logo.jpg)\n\nDo you want to compute thousands of resources (files, metadata, database imports, etc) in parallel, but have a hard time tracking completion status, errors, logs, and other runtime data? That\'s what this is for.\n\n> **Work in progress**\n\n## Quick usage tutorial\n\n### Install\n\n```sh\npip install hadrosaur\n```\n\n### Define a resource collection\n\nImport the lib and initialize a project using a base directory. Files, metadata, and logs will all get stored under this directory.\n\n```py\nfrom hadrosaur import Project\n\nproj = Project(\'./base_directory\')\n```\n\nDefine a collection using a decorator around a function. The collection should have a unique name and must take these params:\n\n* `ident` — an identifier (unique across the collection) for each computed resource\n* `args` — a dictionary of optional arguments\n* `subdir` — the path of a directory in which you can store files for this resource\n\n```py\n@proj.resource(\'collection_name\')\ndef compute_resource(ident, args, subdir):\n  # Run some things...\n  # Maybe save stuff into subdir... \n  time.sleep(1)\n  # Return metadata for the resource, such as run results, filepaths, etc.\n  return {\'ts\': time.time()}\n```\n\n### Fetch a resource\n\nUse the `proj.fetch(collection_name, ident, args)` method to compute and cache resources in a collection.\n\n* If the resource has not yet been computed, the function will be run\n* If the resource was already computed in the past, then the saved results will get returned instantly\n* If an error is thrown in the function, logs will be saved and the status will be updated\n* If the function is backgrounded, then fetching the resource will show a "pending" status\n\n```py\n>> proj.fetch(\'collection_name\', \'uniq_ident123\', optional_args)\n{\n  \'result\': {\'some\': \'metadata\'},\n  \'status\': {\'completed\': True, \'pending\': False, \'error\': False},\n  \'_paths\': {\n    \'base\': \'base_directory/collection_name/uniq_ident123\',\n    \'error\': \'base_directory/collection_name/uniq_ident123/error.log\',\n    \'stdout\': \'base_directory/collection_name/uniq_ident123/stdout.log\',\n    \'stderr\': \'base_directory/collection_name/uniq_ident123/stderr.log\',\n    \'status\': \'base_directory/collection_name/uniq_ident123/status.json\',\n    \'result\': \'base_directory/collection_name/uniq_ident123/result.json\',\n    \'storage\': \'base_directory/collection_name/uniq_ident123/storage/\'\n  }\n}\n```\n\nDescriptions of each of the returned fields:\n\n* `\'result\'`: any JSON-serializable data returned by the resource\'s function\n* `\'status\'`: whether the resource has been computed already ("completed"), is currently being computed ("pending"), or threw a Python error while running the function ("error")\n* `\'paths\'`: All the various filesystem paths associated with your resource\n  * `\'base\'`: The base directory that holds all data for the resource\n  * `\'error\'`: A Python stacktrace of any error that occured while running the resource\'s function\n  * `\'stdout`\': A line-by-line log file of stdout produced by the resource\'s function (any `print()` calls)\n  * `\'stderr`\': A line-by-line log of stderr messages printed by the resource\'s function (any `sys.stderr.write` calls)\n  * `\'status\'`: a JSON object of status keys for the resource ("completed", "pending", "error")\n  * `\'result\'`: Any JSON serializable data returned by the resource\'s function\n  * `\'storage\'`: Additional storage for any files written by the resource\'s function \n',
    'author': 'Jay R Bolton',
    'author_email': 'jayrbolton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jayrbolton/hadrosaur',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
