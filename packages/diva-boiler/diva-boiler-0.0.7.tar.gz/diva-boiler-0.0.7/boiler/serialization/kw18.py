"""
KW18 is a csv-type format consisting of 3 files.
A row schema for each file is defined below.
[?] indicates an un-used row field.

file.txt: contains activity information.
[?] [1:ACTIVITY_TYPE_CODE] [2:ACTIVITY_ID] [?] [4:BEGIN]
[?] [6:END] [?] [?] [?] [?] [?] [12:N_PARTICIPANTS]
[ACTOR1_ID] [ACTOR2_ID] ...
[?] [ACTOR1_BEIGN] [?] [ACTOR1_END] [?] [ACTOR2_BEIGN] [?] [ACTOR2_END] ...

file.kw18: contains geometry information
[0:actor_id] [1:actor_track_length] [2:frame]
[?] [?] [?] [?] [?] [?] [9:top_left_x] [10:top_left_y] [11:bottom_right_x] [12:bottom_right_y]

file.kw18.types: contains actor type information
[0:ACTOR_ID] [1:ACTOR_TYPE]

file.kw18.regions: contains keyframe information
[0:actor_id] [1:frame] [2:is_keyframe] [?] ...
"""
import csv
from typing import Dict, IO, List, Tuple

from boiler.definitions import ActivityType, all_activity_codes
from boiler.models import Activity, Actor, Box, Detection


ActivityMapType = Dict[int, Activity]
ActorMapType = Dict[int, Actor]

COMMENT_CHAR = '#'


def row_is_comment(row):
    return row[0][0] == COMMENT_CHAR


def _set_keyframes_from_regions(geom_actor: Actor, regions_actor: Actor):
    """
    given an actor from a regions file and one from a geom
    file where both have **sorted** detection lists, set the
    keyframe value of the geom detections.
    """
    i: int = 0
    temp_detection_count = len(regions_actor.detections)
    for detection in geom_actor.detections:
        while i < temp_detection_count:
            temp_detection = regions_actor.detections[i]
            if temp_detection.frame >= detection.frame:
                break
            i += 1
        if detection.frame == temp_detection.frame:
            detection.keyframe = temp_detection.keyframe


def _deserialize_actor(row, n_participants, i, activity_begin, activity_end, actor_map):

    actor_id = int(row[13 + i])
    if n_participants == 1:
        actor_begin = activity_begin
        actor_end = activity_end
    elif n_participants > 1:
        actor_start_i = 13 + n_participants + (i * 4)
        actor_begin = int(row[actor_start_i + 1])
        actor_end = int(row[actor_start_i + 3])

    actor = Actor()
    if actor_id in actor_map:
        actor = actor_map[actor_id]
    actor.begin = actor_begin
    actor.end = actor_end
    actor.clip_id = actor_id
    actor_map[actor_id] = actor
    return actor


def deserialize_activities(
    file: IO[str], activity_map: ActivityMapType, actor_map: ActorMapType,
):
    reader = csv.reader(file, delimiter=' ')
    for i, row in enumerate(reader):
        try:
            if row_is_comment(row):
                continue
            activity_type_code = int(row[1])
            activity_id = int(row[2])
            activity_begin = int(row[4])
            activity_end = int(row[6])
            n_participants = int(row[12])
            activity_type = all_activity_codes[activity_type_code]
            activity = Activity(
                activity_type=activity_type.value,
                begin=activity_begin,
                end=activity_end,
                clip_id=activity_id,
                actors=[
                    _deserialize_actor(
                        row, n_participants, i, activity_begin, activity_end, actor_map
                    )
                    for i in range(n_participants)
                ],
            )
            activity_map[activity_id] = activity
        except (IndexError, ValueError) as err:
            raise ValueError(f'activity parse failed on line {i}:') from err


def deserialize_geom(file: IO[str], actor_map: ActorMapType):
    reader = csv.reader(file, delimiter=' ')
    for i, row in enumerate(reader):
        try:
            if row_is_comment(row):
                continue
            actor_id = int(row[0])
            frame = int(row[2])
            boxlist = [int(c) for c in row[9:13]]
            box = Box(left=boxlist[0], top=boxlist[1], right=boxlist[2], bottom=boxlist[3])
            detection = Detection(frame=frame, box=box, keyframe=True)
            if actor_id in actor_map:
                actor_map[actor_id].detections.append(detection)
            else:
                actor_map[actor_id] = Actor(clip_id=actor_id, detections=[detection])
        except (IndexError, ValueError) as err:
            raise ValueError(f'geometry parse filed on line {i}:') from err
    for actor in actor_map.values():
        actor.sort_detections()


def deserialize_regions(file: IO[str], actor_map: ActorMapType):
    reader = csv.reader(file, delimiter=' ')
    # build a temporary actor map from the detections in regions file
    temp_actor_map: ActorMapType = {}
    for i, row in enumerate(reader):
        try:
            if row_is_comment(row):
                continue
            actor_id = int(row[0])
            frame = int(row[1])
            keyframe = bool(int(row[2]))
            detection = Detection(frame=frame, keyframe=keyframe)
            if actor_id in temp_actor_map:
                temp_actor_map[actor_id].detections.append(detection)
            else:
                temp_actor_map[actor_id] = Actor(clip_id=actor_id, detections=[detection])
        except (IndexError, ValueError) as err:
            raise ValueError(f'regions parse failed on line {i}:') from err

    for actor in temp_actor_map.values():
        actor.sort_detections()

    for actor_id, actor in actor_map.items():
        if actor_id in temp_actor_map and len(temp_actor_map[actor_id].detections) > 0:
            _set_keyframes_from_regions(actor, temp_actor_map[actor_id])


def deserialize_types(file: IO[str], actor_map: ActorMapType):
    reader = csv.reader(file, delimiter=' ')
    for i, row in enumerate(reader):
        try:
            if row_is_comment(row):
                continue
            actor_id = int(row[0])
            actor_type: str = row[1]

            if actor_id in actor_map:
                actor_map[actor_id].actor_type = actor_type
            else:
                actor_map[actor_id] = Actor(clip_id=actor_id, actor_type=actor_type)
        except (IndexError, ValueError) as err:
            raise ValueError(f'types parse failed on line {i}:') from err


def deserialize_from_files(
    types_file: IO[str] = None,
    txt_file: IO[str] = None,
    kw18_file: IO[str] = None,
    regions_file: IO[str] = None,
    prune: bool = False,
) -> Tuple[ActivityMapType, ActorMapType]:

    actor_map: ActorMapType = {}
    activity_map: ActivityMapType = {}

    if types_file:
        deserialize_types(types_file, actor_map)
    if txt_file:
        deserialize_activities(txt_file, activity_map, actor_map)
    if kw18_file:
        deserialize_geom(kw18_file, actor_map)
    if regions_file:
        deserialize_regions(regions_file, actor_map)

    if prune:
        for activity in activity_map.values():
            activity.prune()
    return activity_map, actor_map


def find_activity_code(activity_name: str):
    target_activity = ActivityType(activity_name)
    for code, activity in all_activity_codes.items():
        if activity == target_activity:
            return code
    raise ValueError(f'no numerical code exists for {target_activity}')


def serialize_types(actor_list: List[Actor]):
    for actor in actor_list:
        row = [actor.clip_id, actor.actor_type]
        yield ' '.join([str(d) for d in row]) + '\n'


def serialize_activities(activity_list: List[Activity], filler_char):
    for activity in activity_list:
        row = [
            filler_char,
            find_activity_code(activity.activity_type),
            activity.clip_id,
            filler_char,
            activity.begin,
            filler_char,
            activity.end,
            filler_char,
            filler_char,
            filler_char,
            filler_char,
            filler_char,
            len(activity.actors),
        ]
        for actor in activity.actors:
            row.append(actor.clip_id)
        if len(activity.actors) > 1:
            for actor in activity.actors:
                row += [filler_char, actor.begin, filler_char, actor.end]
        yield ' '.join([str(d) for d in row]) + '\n'


def serialize_geom(actor_list: List[Actor], filler_char, keyframes_only=False):
    for actor in actor_list:
        for detection in actor.detections:
            if not keyframes_only or detection.keyframe:
                row = [
                    actor.clip_id,
                    actor.end - actor.begin,
                    detection.frame,
                    filler_char,
                    filler_char,
                    filler_char,
                    filler_char,
                    filler_char,
                    filler_char,
                ]
                row += detection.box.as_array()
                yield ' '.join([str(d) for d in row]) + '\n'


def serialize_to_files(
    output_basename: str,
    activity_list: List[Activity],
    actor_list: List[Actor],
    keyframes_only=False,
    filler_char='0',
):
    with open(output_basename + '.txt', 'w', encoding='utf-8') as yamlfile:
        for line in serialize_activities(activity_list, filler_char):
            yamlfile.write(line)
    with open(output_basename + '.kw18.types', 'w', encoding='utf-8') as yamlfile:
        for line in serialize_types(actor_list):
            yamlfile.write(line)
    with open(output_basename + '.kw18', 'w', encoding='utf-8') as yamlfile:
        for line in serialize_geom(actor_list, filler_char, keyframes_only=keyframes_only):
            yamlfile.write(line)
