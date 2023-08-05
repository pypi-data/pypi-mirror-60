import platform
from enum import Enum

class OSDistrubtion(Enum):
    AMAZON = "amzn"
    CENTOS = "centos"
    DEBIAN = "debian"
    REDHAT = "redhat"
    UBUNTU = "ubuntu"

def get_os_id():
    with open("/etc/os-release") as f:
        info = {}
        for line in f:
            k,v = line.rstrip().split("=")
            info[k] = v.strip('"')
    return info.get('ID')

def get_os_distribution():
    id = get_os_id().lower()

    switcher = {
        "amzn": OSDistrubtion.AMAZON,
        "centos": OSDistrubtion.CENTOS,
        "debian": OSDistrubtion.DEBIAN,
        "redhat": OSDistrubtion.REDHAT,
        "ubuntu": OSDistrubtion.UBUNTU,
    }

    return switcher.get(id)
