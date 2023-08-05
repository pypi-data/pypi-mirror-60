import os
def list_package_data(root):
    """
    Include project template as package data
    """
    paths = []
    for base, dirs, files in os.walk(root, topdown=True):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        paths.extend([
            os.path.join(base, name) for name in files
            if name not in ('.git', 'package-lock.json')
        ])
    return paths
list_package_data('django_project_npm')
