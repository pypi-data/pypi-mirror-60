# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['brickschema']

package_data = \
{'': ['*'], 'brickschema': ['ontologies/*']}

install_requires = \
['owlrl>=5.2,<6.0', 'rdflib>=4.2,<5.0', 'sqlalchemy>=1.3,<2.0']

setup_kwargs = {
    'name': 'brickschema',
    'version': '0.0.1',
    'description': 'A library for working with the Brick ontology for buildings (brickschema.org)',
    'long_description': '# Brick Ontology Python package\n\n## Installation\n\nThe `brickschema` package requires Python >= 3.6. It can be installed with `pip`:\n\n```\npip install brickschema\n```\n\n## Haystack Inference\n\nRequires a JSON export of a Haystack model\nFirst, export your Haystack model as JSON; we are using the public reference model `carytown.json`.\nThen you can use this package as follows:\n\n```python\nimport json\nfrom brickschema.inference import HaystackInferenceSession\nhaysess = HaystackInferenceSession("http://project-haystack.org/carytown#")\nmodel = json.load(open(\'carytown.json\'))\nmodel = haysess.infer_model(model)\nprint(len(model))\n\npoints = model.query("""SELECT ?point ?type WHERE {\n    ?point rdf:type/rdfs:subClassOf* brick:Point .\n    ?point rdf:type ?type\n}""")\nprint(points)\n```\n\n## SQL ORM\n\n```python\nfrom brickschema.graph import Graph\nfrom brickschema.namespaces import BRICK\nfrom brickschema.orm import SQLORM, Location, Equipment, Point\n\n# loads in default Brick ontology\ng = Graph(load_brick=True)\n# load in our model\ng.load_file("test.ttl")\n# put the ORM in a SQLite database file called "brick_test.db"\norm = SQLORM(g, connection_string="sqlite:///brick_test.db")\n\n# get the points for each equipment\nfor equip in orm.session.query(Equipment):\n    print(f"Equpiment {equip.name} is a {equip.type} with {len(equip.points)} points")\n    for point in equip.points:\n        print(f"    Point {point.name} has type {point.type}")\n# filter for a given name or type\nhvac_zones = orm.session.query(Location)\\\n                        .filter(Location.type==BRICK.HVAC_Zone)\\\n                        .all()\nprint(f"Model has {len(hvac_zones)} HVAC Zones")\n```\n',
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'url': 'https://brickschema.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
