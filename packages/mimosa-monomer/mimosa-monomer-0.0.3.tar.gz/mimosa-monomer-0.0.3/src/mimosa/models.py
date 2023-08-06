from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

import pytz

from pydantic import BaseModel, StrictStr, StrictInt, validator, ValidationError


# def validate(instance):
#     errors: List[str] = []
#     for field in fields(instance):
#         attr = getattr(instance, field.name)
#         if not isinstance(attr, field.type):
#             errors.append(
#                 f"Field {field.name} is of type {type(attr)}, should be {field.type}"
#             )


class CraftTypes(Enum):
    SCAFFOLDING = 10
    INSULATION = 15
    WATERBLASTING = 20
    SANDBLASTING = 25
    PAINTING = 30
    HOISTWELLS = 40
    MOBILE_EQUIPMENT = 50
    HVAC = 60
    PERMITTING = 90
    HOUSEKEEPING = 99


class TaskTypes(Enum):
    INSTALLATION = 10
    MODIFICATION = 11
    REMOVAL = 12
    INSPECTION = 13
    WATERBLASTING = 20
    SANDBLASTING = 30
    INSULATION = 40
    ABATEMENT = 50
    PAINTING = 60
    REPAIR = 70
    LOCKOUT = 90
    WALKTHROUGH = 91
    PERFORMING_WORK = 92
    HOUSEKEEPING = 99


class TaskStatus(Enum):
    AWAITING_ESTIMATE = 5
    AWAITING_APPROVAL = 8
    AWAITING_SCHEDULE = 10
    SCHEDULED = 20
    AWAITING = 30
    IN_PROGRESS = 40
    ON_HOLD = 50
    COMPLETE = 90


class EventTypes(Enum):
    NEW_USER_APPROVED = 10
    NEW_USER_APPLIED = 11
    CRAFT_RECORD_CREATED = 20
    NEW_TASK_ADDED = 30
    TASK_STATUS_UPDATED = 31
    TASK_REASSIGNED_COMPANY = 32
    TASK_DESCRIPTION_UPDATED = 33
    TASK_WORK_ORDER_UPDATED = 34
    TASK_DETAILS_UPDATED = 36
    UPDATED_TITLE = 40
    UPDATED_DESCRIPTION = 41
    ADDED_PHOTO = 42
    REMOVED_PHOTO = 43
    CHANGED_ASSET = 44
    UPDATED_CRAFT_DETAILS = 45
    CHANGED_LOCATION_ID = 46
    UPDATED_LOCATION_ON_MAP = 47


@dataclass
class SiteKey:
    name: str
    timezone: str
    managingCompanyID: str
    validCraftTypes: List[int]
    validTaskTypes: List[int]
    validTaskStatusCodes: List[int]
    validEventTypes: List[int]
    customizations: Dict[str, Any]


class SiteKeyValidator(BaseModel):
    name: StrictStr
    timezone: StrictStr
    managingCompanyID: StrictStr
    validCraftTypes: List[StrictInt]
    validTaskTypes: List[StrictInt]
    validTaskStatusCodes: List[StrictInt]
    validEventTypes: List[StrictInt]
    customizations: Dict[StrictStr, Any]

    @validator("timezone")
    def timezone_must_be_valid(cls, tz_string: str):
        if tz_string not in pytz.common_timezones:
            raise ValueError(f"Timezone '{tz_string}' is not valid")

    @validator("validCraftTypes")
    def craft_type_must_be_in_list(cls, type_list: List[int]):
        errors: List[str] = []
        for item in type_list:
            if item not in [craft_type.value for craft_type in CraftTypes]:
                errors.append(f"code {item} not found in CraftTypes")
        if len(errors) > 0:
            raise ValueError(f"Validation errors: {errors}")

        return type_list

    @validator("validTaskTypes")
    def task_type_must_be_in_list(cls, type_list: List[int]):
        errors: List[str] = []
        for item in type_list:
            if item not in [task_type.value for task_type in TaskTypes]:
                errors.append(f"code {item} not found in TaskTypes")
        if len(errors) > 0:
            raise ValueError(f"Validation errors: {errors}")

        return type_list

    @validator("validTaskStatusCodes")
    def status_type_must_be_in_list(cls, type_list: List[int]):
        errors: List[str] = []
        for item in type_list:
            if item not in [status_type.value for status_type in TaskStatus]:
                errors.append(f"code {item} not found in TaskStatus")
        if len(errors) > 0:
            raise ValueError(f"Validation errors: {errors}")

        return type_list

    @validator("validEventTypes")
    def event_type_must_be_in_list(cls, type_list: List[int]):
        errors: List[str] = []
        for item in type_list:
            if item not in [event_type.value for event_type in EventTypes]:
                errors.append(f"code {item} not found in EventTypes")
        if len(errors) > 0:
            raise ValueError(f"Validation errors: {errors}")

        return type_list
