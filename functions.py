import boto3
import datetime
import os
import uuid

from constants import (
    CUSTOMER_KEY,
    FAMILY_ITEM_ID_KEY,
    FAMILY_ITEM_KEY,
    FONT_ITEM_KEY,
    NAME_KEY,
    STYLE_KEY,
    WEIGHT_KEY
)


def convert_form(request):
    result = {}
    for key in request.form:
        if key == CUSTOMER_KEY:
            result[key] = request.form[key]
            continue

        index = key[-1]
        if index in result:
            result[index][key[:-1]] = request.form.get(key)
        else:
            result[index] = { key[:-1] : request.form.get(key)}
    return result


def get_all_ddb_items(table):
    response = table.scan()
    data = response.get('Items')
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response.get('LastEvaluatedKey'))
        data.extend(response.get('Items'))
    return data


def font_in_families(name, families):
    for family in families:
        if name == family.get(NAME_KEY):
            return family.get('id')
    return None


def font_in_fonts(family_id, form, fonts):
    for font in fonts:
        if font.get(FAMILY_ITEM_ID_KEY) != family_id:
            continue
        if (
            font.get(STYLE_KEY) == form.get(STYLE_KEY)
            and font.get(WEIGHT_KEY) == form.get(WEIGHT_KEY)
        ):
            return True
    return False


def save_family_to_ddb(table, form, customer_id):
    id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat("Z")
    item = {
        'id': id,
        'drnId': str(uuid.uuid4()),
        'name': form[NAME_KEY],
        'customerId': customer_id,
        '__typename': FAMILY_ITEM_KEY,
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    response = table.put_item(Item=item)
    return id


def save_font_to_ddb(table, form, family_id, customer_id, file):
    filename = os.path.basename(file.filename).replace(" ", "_")
    timestamp = datetime.datetime.now().isoformat("Z")
    item = {
        'id': str(uuid.uuid4()),
        'drnId': str(uuid.uuid4()),
        'familyItemID': family_id,
        'storageKey': f'{customer_id}/fonts/{filename}' ,
        'style': form[STYLE_KEY],
        'weight': form[WEIGHT_KEY],
        '__typename': FONT_ITEM_KEY,
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    response = table.put_item(Item=item)
    return id


def upload_file(font_file, customer_id):
    s3 = boto3.client('s3')
    filename = os.path.basename(font_file.filename).replace(" ", "_")
    object_name = f'public/{customer_id}/{filename}'
    
    response = s3.upload_fileobj(
        font_file,
        os.environ.get('BUCKET_NAME'),
        object_name
    )
    
    return str(response)


