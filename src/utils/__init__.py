# src/utils/__init__.py

# This file makes the 'utils' directory a Python package.

# You can optionally import utility modules from this package here
# to make them directly available when someone imports 'src.utils'.

# Import the utility modules
# This allows you to import them like:
# from src.utils import sys_utils
# from src.utils import image_utils

from . import sys_utils
from . import image_utils

# If you had specific functions or classes you wanted to expose directly
# under the 'src.utils' namespace (less common for general utility packages),
# you could do that here:
# from .sys_utils import check_and_install_libraries
# from .image_utils import create_circular_image

# For this project's structure, importing the modules themselves is standard
# and clear. An empty __init__.py would also technically work to make it a package.