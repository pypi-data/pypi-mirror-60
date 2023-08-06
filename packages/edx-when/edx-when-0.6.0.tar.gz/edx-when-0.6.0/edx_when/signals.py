"""edx_when signal handlers."""
from __future__ import absolute_import, unicode_literals

import logging

from six import text_type
from xblock.fields import Scope

from .api import FIELDS_TO_EXTRACT, set_dates_for_course

log = logging.getLogger(__name__)


def date_field_values(date_fields, xblock):
    """
    Read field values for the specified date fields from the supplied xblock.
    """
    result = {}
    for field_name in date_fields:
        if field_name not in xblock.fields:
            continue
        field = xblock.fields[field_name]
        if field.scope == Scope.settings and field.is_set_on(xblock):
            try:
                result[field.name] = field.read_from(xblock)
            except TypeError as exception:
                exception_message = "{message}, Block-location:{location}, Field-name:{field_name}".format(
                    message=text_type(exception),
                    location=text_type(xblock.location),
                    field_name=field.name
                )
                raise TypeError(exception_message)
    return result


def extract_dates_from_course(course):
    """
    Extract all dates from the supplied course.
    """
    from xmodule.modulestore.django import modulestore  # pylint: disable=import-error

    log.info('Publishing course dates for %s', course.id)
    if course.self_paced:
        metadata = date_field_values(FIELDS_TO_EXTRACT, course)
        # self-paced courses may accidentally have a course due date
        metadata.pop('due', None)
        date_items = [(course.location, metadata)]
    else:
        date_items = []
        items = modulestore().get_items(course.id)
        log.info('extracting dates from %d items in %s', len(items), course.id)
        for item in items:
            date_items.append((item.location, date_field_values(FIELDS_TO_EXTRACT, item)))
    return date_items


def extract_dates(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Extract dates from blocks when publishing a course.
    """
    from xmodule.modulestore.django import modulestore  # pylint: disable=import-error

    log.info("Extracting dates from %s", course_key)

    course = modulestore().get_course(course_key)

    if not course:
        log.info("No course found for key %s", course_key)
        return

    date_items = extract_dates_from_course(course)

    try:
        set_dates_for_course(course_key, date_items)
    except Exception:  # pylint: disable=broad-except
        log.exception('setting dates for %s', course_key)
