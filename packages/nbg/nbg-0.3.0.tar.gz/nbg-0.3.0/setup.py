# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nbg', 'nbg.auth', 'nbg.base']

package_data = \
{'': ['*'], 'nbg.auth': ['certs/*']}

install_requires = \
['requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'nbg',
    'version': '0.3.0',
    'description': 'Official Python SDK for NBG APIs',
    'long_description': '# NBG Python SDK\n\nPython wrapper with unified developer experience for the APIs of the National Bank of Greece.\n\n## Requirements\n\n- Python 3.6 or newer\n\n## Installation\n\n```shell\npipenv install nbg\n```\n\n## API clients\n\nThe National Bank of Greece provides a set of multiple APIs. To use each one of these APIs, you should pick the corresponding client from the `nbg` package.\n\n### Accounts Information PSD2 API\n\n```python\nfrom datetime import datetime\n\nimport nbg\n\n\n# Step 1 - Set up client and authentication\nclient = nbg.AccountInformationPSD2Client(\n    client_id="your_client_id",\n    client_secret="your_client_secret",\n    production=False,\n)\nclient.set_access_token("access_token_of_your_user")  # Also sets default `user_id`\n\n# Step 2 - Set up a sandbox, when in development\nclient.create_sandbox("sandbox_id")\nclient.set_sandbox("sandbox_id")\n\n# Step 3 - Start working with the Account information API\n\n## Account resource\nclient.accounts()\nclient.account_beneficiaries(iban="GR7701100800000008000133077")\nclient.account_details(account="08000133077")\nclient.account_transactions(\n    account="08000133077",\n    date_from=datetime(2019, 7, 1),\n    date_to=datetime(2019, 8, 1),\n)\n\n## Foreign Currency Account resource\nclient.foreign_currency_accounts()\nclient.foreign_currency_account_beneficiaries(\n    account="08000133077",\n)\nclient.foreign_currency_account_details(\n    account="08000133077",\n)\nclient.foreign_currency_account_transactions(\n    account="08000133077",\n    date_from=datetime(2019, 7, 1),\n    date_to=datetime(2019, 8, 1),\n)\n\n## Scheduled Payments resource\nclient.scheduled_payments(\n    account="08000133077",\n    date_from=datetime(2019, 7, 1),\n    date_to=datetime(2019, 8, 1),\n)\n\n## Standing Orders resource\nclient.standing_orders(\n    account="08000133077",\n    date_from=datetime(2019, 7, 1),\n    date_to=datetime(2019, 8, 1),\n)\n\n## Sandbox resource\nclient.create_sandbox("unique_sandbox_id")\nsandbox_data = client.export_sandbox("unique_sandbox_id")\nclient.import_sandbox("another_unique_sandbox_id", sandbox_data)\nclient.delete_sandbox("unique_sandbox_id")\n\n## User resource\nclient.current_user()\n```\n',
    'author': 'Paris Kasidiaris',
    'author_email': 'paris@sourcelair.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
