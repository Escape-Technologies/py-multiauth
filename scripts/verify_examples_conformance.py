import os

from multiauth.revamp.multiauth import Multiauth

for file in os.listdir('examples'):
    if file.endswith('.json'):
        mh = Multiauth.from_file(os.path.join('examples', file))
