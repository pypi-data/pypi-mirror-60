import click

from boiler import cli
from boiler.commands.utils import exit_with, handle_request_error
from boiler.definitions import all_activity_codes


@click.group(name='activity', short_help='utils')
@click.pass_obj
def activity(ctx):
    pass


@activity.command(name='list-types', help='list known activities')
def list_activities():
    for activity_type in all_activity_codes.values():
        click.echo(activity_type.value)


@activity.command(name='list', help='list activities for video')
@click.option('--video-id', required=True)
@click.pass_obj
def list_video_activities(ctx, video_id):
    r = ctx['session'].get(f'video/{video_id}/activities')
    exit_with(handle_request_error(r))


cli.add_command(activity)
