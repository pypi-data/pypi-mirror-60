# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mutable_merkle']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mutable-merkle',
    'version': '0.1.1',
    'description': 'A Merkle tree supporting append, update, remove operations.',
    'long_description': '# Mutable Merkle\n[![image](https://img.shields.io/pypi/v/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)\n[![image](https://img.shields.io/pypi/l/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)\n[![image](https://img.shields.io/pypi/pyversions/mutable_merkle.svg)](https://pypi.org/project/mutable_merkle/)\n![style](https://github.com/EdgyEdgemond/mutable_merkle/workflows/style/badge.svg)\n![tests](https://github.com/EdgyEdgemond/mutable_merkle/workflows/tests/badge.svg)\n[![codecov](https://codecov.io/gh/EdgyEdgemond/mutable_merkle/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/mutable_merkle)\n\n``mutable_merkle`` provides a merkle tree with append, update and remove leaf functionality. This \nis intended to support solutions that are not just append only.\n\n```python\n  m1 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"e", b"f"], hash_type="sha256")\n  m2 = mutable_merkle.tree.MerkleTree.new([b"a", b"b", b"c", b"d", b"e", b"f"], hash_type="sha256")\n  m3 = mutable_merkle.tree.MerkleTree(hash_type="sha256")\n\n  m2.remove_leaf(3)\n  for value in [b"a", b"b", b"c", b"e", b"f"]:\n      m3.add_leaf(value)\n\n  assert m1.root == m2.root\n  assert m1.root == m3.root\n```\n\n## Serialization\n\nAlong with update and remove leaf functionality, ``mutable_merkle`` has been designed\naround being serializable as well. This supports storage of the merkle tree as well\nas transmission of the proofs.\n\n\n```python\n  mt = mutable_merkle.tree.MerkleTree.new(\n      [b"a", b"b", b"c", b"d", b"e", b"f", b"g", b"h", b"i", b"j"],\n      hash_type=hash_type,\n  )\n\n  payload = mt.marshal()\n\n  mt_reload = mutable_merkle.tree.MerkleTree.unmarshal(payload)\n\n  assert mt == mt_reload\n```\n',
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'url': 'https://github.com/EdgyEdgemond/mutable_merkle/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
