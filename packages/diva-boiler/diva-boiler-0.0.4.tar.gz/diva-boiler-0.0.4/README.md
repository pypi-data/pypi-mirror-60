# boiler

## installation

```bash
# for yaml.CLoader support
apt install libyaml-dev

# install boiler tools
pip3 install -e .

# set token for stumpf
export STUMPF_API_URL="" # defaults to https://stumpf-the-younger.avidannotations.com/api/diva
export X_STUMPF_TOKEN=""

# set tokens for boto3.  currently unused - you can ignore these
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""

boiler --help
```

You should [install jq](https://stedolan.github.io/jq/) for output formatting.

See [boto3 docs](https://pypi.org/project/boto3/) for additional info about AWS config.

## usage

This documentation provides some useful examples, but is not exhaustive.

```bash
# to get up-to-date documentation, use the help option
boiler [noun] --help
boiler [noun] [verb] --help
```

Commands produce json objects as output.  No keys are guaranteed, and different commands produce different keys.

```js
{
  "response": { /* network response body if network request succeeds */ },
  "error": { /* error information if errors were encountered */ },
  "context": { /* error context if available */ },
  "summary": { /* summarization of activity files */ },
}
```

### local data manipulation

boiler has utilities to read, validate, and convert KPF and KW18 data.  Some example commands are below.  These are **offline** operations.

```bash
# show KPF help
boiler kpf load --help

# show kw18 help
boiler kw18 load --help

# validate some kpf
boiler kpf load \
  --geom examples/kpf/geom.yml \
  --activities examples/kpf/activities.yml \
  --types examples/kpf/types.yml \
  --prune \
  --validate \
  | jq

# convert kw18 to kpf
boiler kw18 load \
  --txt /path/to/data.txt \
  --kw18 /path/to/data.kw18 \
  --types /path/to/data.kw18.types \
  --validate \
  --convert kpf directory/output_basename \
  | jq
```

* `--validate` checks activities for integrity errors.  The rules for validation are generally documented as assertion string errors in `boiler/validate.py`
* `--prune` runs keyframe correction to validate that no frames marked as keyframes match perfectly with the linear interpolation of their surrounding keyframes.  If `--prune` is specified, `--convert` will omit non-keyframes from the output.
* `--convert` takes 2 arguments: `kpf|kw18` and a path to the output file's base name.  It will overwrite the output file if it
* Note that for `--geom, --activities, --types, --txt, --kw18`, not all of the options have to be specified at every run.  Without all 3, validation will fail, but if you just want to see what's going on in an activity file (for example) without having to specify types or geometry, you'll still get a summary with info limited to that file.

Example data can be found in `examples/kpf/`

### Workflow Step 1: video ingest

Can be done one-off or through a batch CSV file.

```bash
# one-off
boiler video add --help

# minimal add
boiler video add \
  --name 2999-01-01.00-00-00.00-05-00.admin.G999 \
  --local-path somefile.avi \
  --release-batch testing \
  | jq

# bulk using a manifest csv file
boiler video bulk-ingest --help

# display the bulk csv header
boiler video get-bulk-csv-header
```

Notes on ingest behavior:

* Not all fields are required.
* If `gtag`, `location`, etc. are parsable from the video name, they will be.
* You can override any parsed or guessed fields by setting them explicitly.
* One of `local_path` or `s3_path` is required.
  * If `local_path` is set, boiler will upload the video to s3 and attempt transcoding.
  * If `s3_path` is set, boiler will assume transcoding is complete and expect `frame_rate`, `duration`, etc. to be set.

Example bulk ingest files can be found in `examples/`

* Bulk ingest CSV must always contain a header row
* header fields can be in any order
* fields can be omitted according to the rules above.

## Workflow Step 2: vendor activity dispatch

Once a video exists, it can be transitioned to the annotation state.

```bash
boiler vendor dispatch --help

# generate the list of known activity types to file
boiler activity list-types > activity-list.txt

# specify a video, vendor, and list of activities to transition to the annotation stage
boiler vendor dispatch \
  --name kitware \
  --video-name 2999-01-01.00-00-00.00-05-00.admin.G999 \
  --activity-type-list activity-list.txt \
  | jq
```

Example type lists can be found in `examples/`

### Workflow Step 3: vendor activity ingestion

When activities come back from vendors, they should be transitioned to the audit state.

```bash

boiler kpf ingest --help

# specify kpf to ingest and transition
boiler kpf ingest \
  --types examples/kpf/types.yml \
  --geom examples/kpf/min.geom.yml  \
  --activities activity-list.txt \
  --video-name 2999-01-01.00-00-00.00-05-00.admin.G999 \
  --vendor-name kitware \
  --activity-type-list examples/activity-type-list-short.txt \
  | jq
```

## design

design for cli commands follows some simple guidelines:

* commands produce a single JSON document (map or array) as output on stdout in all conditions.
* input data and REST errors cause boiler to exit with status code 1.  error information is JSON on stdout.
* fatal exceptions not related to input data or REST operations should not be caught or handled.
* additional logging and metrics, especially for batch operations, may be printed to stderr.
* any output on stderr has no guaranteed format, though in most cases it should be human-readable lines of text.
* click.argument should not be used.  prefer click.option
* you can confidently pipe any boiler command to `jq`
