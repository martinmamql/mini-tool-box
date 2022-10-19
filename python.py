# Module not found
# \__init__.py
# modules/
# fusion

# The following will trigger ModuleNotFoundError: No module named 'fusion'
import modules as modules
import fusion as fusion

# Correction:
from . import fusion
from . import modules

# Set two arguments referring to true and false of the same value
parser.add_argument('--global_pool', action='store_true')
parser.set_defaults(global_pool=False)
parser.add_argument('--cls_token', action='store_false', dest='global_pool',
                    help='Use class token instead of global pool for classification')

# in bash
AGGRE_TYPE="cls_token"
#AGGRE_TYPE="global_pool"

python ... 
--$AGGRE_TYPE
