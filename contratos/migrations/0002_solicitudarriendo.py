from django.db import migrations


class Migration(migrations.Migration):

	# Esta migración quedó como archivo vacío por error en el pasado.
	# La convertimos en una migración vacía (no-op) que mantiene la numeración.
	dependencies = [
		('contratos', '0002_initial'),
	]

	operations = []

