import os

from multiauth.multiauth import Multiauth

for file in os.listdir('examples'):
    if file.endswith('.json'):
        mh = Multiauth.from_file(os.path.join('examples', file))
        print(os.path.join('examples', file))  # noqa: T201
