import click

@click.command()
def vms():
	"""
     welcome message
	 for more information visit http:/github.com/imyashkale
	"""
	click.echo('Vision Management CLI by Yash')

@click.command()
def hello():
	click.command(mkdir,yash)

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def pythonrocks(count):
	for i in range(count):
		click.echo('Python rocks!!!!!')