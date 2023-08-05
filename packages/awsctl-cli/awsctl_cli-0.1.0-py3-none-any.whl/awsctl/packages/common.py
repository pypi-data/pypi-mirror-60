import subprocess
import click
from typing import List
from awsctl.utils.operating_system import OSDistrubtion, get_os_distribution

class PackageCommand(object):
    def __init__(self, args: List[str], distrubtions: List[OSDistrubtion]):
        self.args = args
        self.distrubtions = distrubtions

    def execute(self):
        command = " ".join(self.args)

        click.echo(click.style(command, fg="grey"))

        return subprocess.run(self.args)

    def is_applicable(self, distribution):
        return distribution in self.distrubtions

class PackageInstaller(object):

    def __init__(self, commands: List[PackageCommand]):
        self.commands = commands

    def install(self):
        distribution = get_os_distribution()

        click.echo(click.style("Operating System: {}".format(distribution), fg="pink", bold=True))

        click.echo(click.style("[INSTALL]", fg="green", bold=True))

        for command in self.commands:
            if command.is_applicable(distribution):
                result = command.execute()

                if result.returncode != 0:
                    click.echo(click.style("[ERROR]", fg="red", bold=True))
                    click.echo(click.style(result.stderr, fg="grey"))
                else:
                    raise click.Abort("install command returned an error code.")


