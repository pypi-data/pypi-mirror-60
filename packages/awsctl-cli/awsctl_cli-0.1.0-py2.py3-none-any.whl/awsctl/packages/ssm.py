from awsctl.packages.common import PackageCommand, PackageInstaller
from awsctl.utils.operating_system import OSDistrubtion

def get_ssm_installer():
    installer = PackageInstaller([
        PackageCommand(
            ["yum", "install", "-y", "https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm"],
            [OSDistrubtion.AMAZON, OSDistrubtion.CENTOS, OSDistrubtion.REDHAT]
        ),
        PackageCommand(
            ["systemctl", "enable", "amazon-ssm-agent"],
            [OSDistrubtion.AMAZON, OSDistrubtion.CENTOS, OSDistrubtion.REDHAT]
        ),
        PackageCommand(
            ["systemctl", "start", "amazon-ssm-agent"],
            [OSDistrubtion.AMAZON, OSDistrubtion.CENTOS, OSDistrubtion.REDHAT]
        )
    ])

    return installer
