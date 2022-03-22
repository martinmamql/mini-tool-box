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
