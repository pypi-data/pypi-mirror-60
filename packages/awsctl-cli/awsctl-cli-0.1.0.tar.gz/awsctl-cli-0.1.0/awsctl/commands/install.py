import click

@click.group("install")
def install_group():
    pass

@install_group.command("ssm")
def install_ssm():
    click.echo("Installing SSM...")
    pass

@install_group.command("cloudwatch")
def install_cloudwatch():
    click.echo("Installing Cloudwatch...")
    pass
