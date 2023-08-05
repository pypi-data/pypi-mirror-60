# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_component']

package_data = \
{'': ['*']}

install_requires = \
['django>=1.11']

setup_kwargs = {
    'name': 'django-component',
    'version': '0.1.1',
    'description': 'Django template tags to create composable components',
    'long_description': 'django_component\n#################\n\nThe readme is outaded and will be updated only for the first release. Until then refer to the tests\n\n**Better components for Django templates.**\nInspired by javascript front-end frameworks like Svelte, React, etc\n\nSupports Python **3.6+** and Django **1.11**, **2.0+**, and **3.0+**\n\n\nDescribe your components in templatetags/mycomponents.py\n\n.. code-block:: python\n\n    from django_component import Library, Component\n\n    register = Library()\n\n    @register.component\n    class Card(Component):\n        template = "mycomponents/card.html"\n        css = ["mycomponents/card.css"]\n        js = ["mycomponents/card.js"]\n    \n        def context(title, author=\'Me\'):\n            # By default all arguments are passed to the context,\n            # But you can do some context processing if needed\n            return {\n                \'short_title\': title[:20],\n                \'author\': author\n            }\n\nCreate it\'s template in template/mycomponents/card.html\n\n.. code-block:: html\n\n    <section class="card">\n        <header>{{ slots.header }}</header>\n        <h1>{{ short_title }}</h1>\n        <div class="content">{{ children }}</div>\n        <footer>\n            Written by {{ author }}\n            {{ slots.footer }}\n        </footer>\n    </section>\n\nUse it in template/homepage.html\n\n.. code-block:: html\n\n    {% load mycomponents %}\n    \n    {% components.use_components_media %}\n    {% components.css %}\n\n    {% Card title="My card\'s title" %}\n        <div>\n            This will be accessible as the `children` variable.\n            It\'s just django template, {{ variable }} !\n        </div>\n\n        {% slot header %}\n            This <img src="foo.jpg" />\n            will be in the header of the card\n        {% endslot %}\n\n        {% slot footer %}\n            This <span class="bar">slots</span> \n            will be in the footer of the card\n        {% endslot %}\n    {% end_Card %}\n\n    {% components.js %}\n\nWhy django_component?\n======================\n\n``django_component`` make it easy to create reusable template components. Django already has some features to address this, but they all come with some limitations. ``django_component`` unify what\'s great from all of these features (``block``, ``includes``, ``inclusion_tag``) under an unique api. In addition ``django_component`` address one of my greatest frustration with reusable components in django: **tracking css and js dependencies** for each component and **automatically** include them when necessary.\n\n``django_component`` api is influenced by javascript frameworks like Svelte, Vue, React, etc\n\n\nInstallation\n============\n\n.. code-block:: sh\n\n    pip install git+https://gitlab.com/Mojeer/django_component.git#egg=django_component\n\nThen add ``django_component`` to your INSTALLED_APPS:\n\n.. code-block:: python\n\n    INSTALLED_APPS = [\n        ...,\n        "django_component",\n        ...\n    ]\n\nUsage\n=====\n\nThe example at the begining of the readme describe most of the api of ``django_component``. Bellow is a detailed explanation.\n\nCreate your component\'s class\n-----------------------------\n\nA component is describe by it\'s class. This is where you define it\'s name, template, css, js, and context processor.\nIt\'s then registered similarly to how you register classic django tags, by instanciating Library, and then calling it\'s ``component`` method.\n\n.. code-block:: python\n\n    from django_component import Library, Component\n\n    register = Library()\n\n    @register.component\n    class MyComponent(Component):\n        template = \'components/my_component.html\'\n        css = [\'components/my_component.css\']\n        js = [\'components/my_component.js\']\n\n        def context(foo=5):\n            return {\'foo2\': foo * 2}\n\nBecause django_component.Library inherit from django.template.Library you can also register regular tags with it.\n\n\nUse it in your templates\n------------------------\n\nThe opening tag of a component is the same as it\'s class name, the closing tag is the same prefixed by ``end_``\n\nIf your component contains css or js you will need to use ``{% components.use_components_media %}`` before using your components. You can put it in your ``base.html`` template once and then forget about it.\n\nTODO\nFor more examples look into tests/templatetags/test_components.py\n',
    'author': 'Jérôme Bon',
    'author_email': 'bon.jerome@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/Mojeer/django_components',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
