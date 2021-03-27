# -*- coding: utf-8 -*-
import random
from typing import Union, Dict, Any
from jsonschema import ValidationError, validators

from easy_mock import common

SCHEMA_KEYS = tuple(
    "items additionalItems contains additionalProperties propertyNames "
    "if then else allOf anyOf oneOf not".split()
)

DEFAULT_TYPES = tuple(
    "array object string boolean integer null number".split()
)

SCHEMA_OBJECT_KEYS = ("properties", "patternProperties", "dependencies")

JSONType = Union[None, bool, float, str, list, Dict[str, Any]]

Schema = Dict[str, JSONType]

JSONSchemaValidator = Union[
    validators.Draft4Validator,
    validators.Draft6Validator,
    validators.Draft7Validator,
]


def process_int(**kwargs):
    maximun = kwargs.get("maximun") or 99999
    minimun = kwargs.get("minimun") or 0
    exclusiveMinimum = 1 if kwargs.get("exclusiveMinimum") else 0
    exclusiveMaximum = 1 if kwargs.get("exclusiveMaximum") else 0

    result = random.randint(int(minimun) + exclusiveMinimum, int(maximun) - exclusiveMaximum)
    result = result * kwargs.get("multipleOf") if kwargs.get("multipleOf") else result

    return result


def process_str(**kwargs):
    maxLength = kwargs.get("maxLength") or 99
    minLength = kwargs.get("minLength") or 0
    result = common.gen_random_string(random.randint(int(minLength), int(maxLength)))
    return "".join(result)


# def process_list(**kwargs):


def process(schema: Schema) -> Dict:
    """Generate test data according to the schema
    """
    res = {}

    def schema2data(value):
        type_ = value.get("type")
        if type_ and type_ not in DEFAULT_TYPES:
            raise ValueError(f"The schema type must be in {DEFAULT_TYPES}.")

        if value.get("oneOf") or value.get("anyOf"):
            type_ = random.choice(value.get("oneOf") or value.get("anyOf"))

            if type_.get("type") == "null":
                return None

            value.update(type_)
            value.pop("oneOf", None)
            value.pop("anyOf", None)
            return resolve_all_refs(value)

        elif type_ == "array":
            array_data = []
            for item in value.get("items"):
                item_type_ = item.get("type")
                if item_type_ == "object":
                    array_data.append(resolve_all_refs(item))
                else:
                    array_data.append(schema2data(item))

            return array_data

        elif type_ == "object":
            return resolve_all_refs(value)

        elif type_ == "boolean":
            return random.choice([True, False])

        elif type_ == "integer" or type_ == "number":
            return process_int(**value)

        elif type_ == "string":
            return process_str(**value)

        else:
            raise ValidationError("Incorrect schema syntax.")

    for k, v in schema.items():
        res[k] = schema2data(v)

    return res


def resolve_all_refs(schema: Schema) -> Dict:
    """Parse schema and process through process method
    """
    res = {}
    for key in SCHEMA_KEYS:
        val = schema.get(key, False)
        if isinstance(val, list):
            schema[key] = [
                resolve_all_refs(v) if isinstance(v, dict) else v
                for v in val
            ]
        elif isinstance(val, dict):
            schema[key] = resolve_all_refs(val)

    for key in SCHEMA_OBJECT_KEYS:
        if key in schema:
            res = process(schema[key])

    if schema.get("properties") and schema.get("required"):
        difference_set = set(schema.get("properties").keys()) - set(schema.get("required"))
        for ds in difference_set:
            if ds.startswith(common.gen_random_string(1)):
                del res[ds]

    return res
