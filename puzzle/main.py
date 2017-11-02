import box
from ipdb import launch_ipdb_on_exception

def main():
    with launch_ipdb_on_exception():
        b = box.Box()
        box.find(b)


