import sys

if not sys.argv[0].endswith('kts'):
    from kts.api import *
    from kts.core.init import init
    init()
