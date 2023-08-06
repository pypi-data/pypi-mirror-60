from pathlib import Path
import sys

import click

from boiler import cli
from boiler.commands.utils import (
    activity_types_from_file,
    exit_with,
    handle_request_error,
    summarize_activities,
)
from boiler.definitions import AnnotationVendors
from boiler.serialization import kw18 as kw18_serialization, serializers, web as web_serialization
from boiler.validate import validate_activities


def _load_kw18(types=None, kw18=None, txt=None, validate=False, prune=False, convert=(None, None)):
    activity_map, actor_map = kw18_serialization.deserialize_from_files(types, txt, kw18)
    if prune:
        [a.prune() for a in activity_map.values()]

    output = {'summary': summarize_activities(activity_map.values())}

    if validate:
        errors = validate_activities(activity_map.values())
        output['error'] = web_serialization.serialize_validation_errors(errors)

    serialization_type = convert[0]
    base_path = convert[1]
    if serialization_type and base_path:
        serializer = serializers.get(serialization_type)
        serializer.serialize_to_files(
            base_path, activity_map.values(), actor_map.values(), keyframes_only=prune
        )
    return output


@click.group(name='kw18', short_help='Ingest and validate kw18')
@click.pass_obj
def kw18(ctx):
    pass


@kw18.command(name='load', help='interact locally with the kw18 format')
@click.option('--types', type=click.File(mode='r'), help='path to .kw18.types file')
@click.option('--kw18', type=click.File(mode='r'), help='path to .kw18 geometry file')
@click.option('--txt', type=click.File(mode='r'), help='path to .txt activity definitions')
@click.option('--validate', is_flag=True, help='run static integrity checks')
@click.option('--prune', is_flag=True, help='prune interpolated detections before validation')
@click.option(
    '--convert',
    nargs=2,
    type=click.Tuple(
        [
            click.Choice(serializers.keys()),
            click.Path(
                exists=False, file_okay=True, dir_okay=False, writable=True, resolve_path=True
            ),
        ]
    ),
    default=(None, None),
    help='convert to another serialization',
)
def load(types, kw18, txt, validate, prune, convert):
    output = _load_kw18(types, kw18, txt, validate, prune, convert)
    exit_with(output)


@kw18.command(name='bulk-validate', short_help='validate all kw18 files in a local directory')
@click.option('--path', type=click.Path(exists=True, file_okay=False), default='.')
@click.option(
    '--prune', is_flag=True, help='prune interpolated detections before validation', default=False
)
def bulk_validate(path, prune):
    errors = {}
    total_count = 0
    valid_count = 0
    all_files = list(Path(path).glob('**/*.kw18'))
    with click.progressbar(
        all_files, label='validating', item_show_func=lambda x: x and x.stem, file=sys.stderr,
    ) as bar:
        for kw18_path in bar:
            total_count += 1
            dir = kw18_path.parent
            base = kw18_path.stem

            try:
                types = (dir / (base + '.kw18.types')).open()
            except FileNotFoundError:
                types = None

            try:
                txt = (dir / (base + '.txt')).open()
            except FileNotFoundError:
                txt = None

            error = _load_kw18(
                kw18=kw18_path.open(), types=types, txt=txt, validate=True, prune=prune
            )['error']
            if len(error) == 0:
                valid_count += 1

            errors[str(kw18_path)] = error

    exit_with({'summary': f'{valid_count} of {total_count} kw18 files are valid', 'errors': errors})


@kw18.command(name='ingest', short_help='push files from the annotation repository')
@click.option(
    '--types', type=click.File(mode='r'), help='path to the "*.types" file', required=True
)
@click.option('--kw18', type=click.File(mode='r'), help='path to the "*.kw18" file', required=True)
@click.option('--txt', type=click.File(mode='r'), help='path to the "*.txt" file', required=True)
@click.option('--video-name', type=click.STRING, help='video name in stumpf', required=True)
@click.option(
    '--vendor-name',
    type=click.Choice([e.value for e in AnnotationVendors]),
    help='vendor name in stumpf',
    required=True,
)
@click.option('--activity-type-list', type=click.File(mode='r'), required=True)
@click.pass_obj
def ingest(ctx, types, kw18, txt, video_name, vendor_name, activity_type_list):
    """Ingest a single clip's annotations from the annotation repository.

    This command takes a set of KW18 annotation files for a single clip and
    sends them to Stumpf.  Stumpf will first detect whether the files have
    changed or not.  If they have not, no further action will be taken.  If
    they have, then Stumpf will:

    \b
    1. Generate a transition to the "annotation" status.
    2. Run server side validation.
    3. If validation fails, return failure information.
    4. If validation succeeds, transion to the "audit" state
       and ingest activities from the KW18 files.
    """
    activity_types = activity_types_from_file(activity_type_list)
    files = {
        'geom': {'file': kw18, 'model': None},
        'types': {'file': types, 'model': None},
        'activities': {'file': txt, 'model': None},
    }

    for f in files.values():
        f['file'].seek(0, 0)  # reset reader position after local deserialization
        payload = {'file': f['file']}
        r = ctx['session'].post('upload', files=payload)
        if r.status_code == 409:
            r.status_code = 201
        resp = handle_request_error(r)
        if r.status_code == 201:
            f['model'] = resp['response']
        else:
            exit_with(resp)

    data = {
        'video_name': video_name,
        'vendor_name': vendor_name,
        'kw18_geom_id': files['geom']['model']['id'],
        'kw18_types_id': files['types']['model']['id'],
        'kw18_activities_id': files['activities']['model']['id'],
        'activity_types': activity_types,
    }
    r = ctx['session'].post('video-pipeline/process-annotation', json=data)
    exit_with(handle_request_error(r))


cli.add_command(kw18)  # type: ignore
