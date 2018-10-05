import logging
import click

LOG = logging.getLogger(__name__)


@click.command('institutes', short_help='Display institutes')
@click.pass_context
def institutes(context):
    """Show all institutes in the database"""
    LOG.info("Running scout view institutes")
    adapter = context.obj['adapter']

    institute_objs = [ins_obj for ins_obj in adapter.institutes()]
    if len(institute_objs) == 0:
        click.echo("No institutes found")
        return

    header = ''
    for key in institute_objs[0].keys():
        header = header + "{0}\t".format(key)

    click.echo(header)

    for institute_obj in institute_objs:

        row = ''
        for value in institute_obj.values():
            row = row + "{0}\t".format(value)

        click.echo(row)
