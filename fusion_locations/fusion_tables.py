"""Google server to server authentication through API Key and json credentials."""
import logging
import os

from apiclient.discovery import build
from django.conf import settings
from googleapiclient import errors
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

LOG = logging.getLogger(__name__)

# google credential extraction file paths
API_APPLICATION_JSON_FILE_PATH = os.path.join(settings.BASE_DIR, "google_api_application.json")
API_SERVICE_ACCOUNT_ZIP_FILE_PATH = os.path.join(settings.BASE_DIR, "google_service_account.zip")

# add some marginal protection to google credentials being placed on github
if not os.path.exists(API_APPLICATION_JSON_FILE_PATH):
    # try unzipping creds
    import zipfile

    zip_ref = zipfile.ZipFile(API_SERVICE_ACCOUNT_ZIP_FILE_PATH, 'r')
    zip_ref.extractall(settings.BASE_DIR)
    zip_ref.close()


# google services
def get_fusion_table_service():
    scopes = ["https://www.googleapis.com/auth/fusiontables"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        API_APPLICATION_JSON_FILE_PATH, scopes=scopes)

    http_auth = credentials.authorize(Http())
    return build('fusiontables', 'v2', http=http_auth)


def get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        API_APPLICATION_JSON_FILE_PATH, scopes=scopes)

    http_auth = credentials.authorize(Http())
    return build('drive', 'v3', http=http_auth)


# fusion table (google drive document) read permissions
def set_item_to_public_readable(fusion_table_id):
    """
    https://stackoverflow.com/questions/37092163/permissions-and-the-fusion-table-api
    """
    drive_service = get_drive_service()
    new_permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    try:
        return drive_service.permissions().create(
            fileId=fusion_table_id, body=new_permission).execute()
    except errors.HttpError as error:
        LOG.error('An error occurred: %s' % error)


# FUSION TABLE functions
# google map table definition
def get_table_columns():
    columns = [
        {'name': 'Location', 'type': 'LOCATION'},
        {'name': 'Address', 'type': 'STRING'},
    ]
    return columns


def create_fusion_table():
    from .models import GoogleFusionTable

    columns_dict = get_table_columns()
    fusion_table_service = get_fusion_table_service()
    request = fusion_table_service.table().insert(
        body={
            "name": "Google Maps Locations",
            "isExportable": True,
            "columns": columns_dict
        })
    try:
        response = request.execute()
        fusion_table, created = GoogleFusionTable.objects.get_or_create(table_id=response["tableId"])
        set_item_to_public_readable(response["tableId"])
        return fusion_table
    except Exception as e:
        LOG.error("create_fusion_table exception: %s" % e.message)


def add_fusion_table_row(google_map_location):
    """ try to add fusion table row """
    from .models import GoogleFusionTable

    # get or create fusion table
    google_fusion_table = GoogleFusionTable.objects.get_fusion_table()

    if google_fusion_table:
        table_id = google_fusion_table.table_id
        columns_dict = get_table_columns()
        columns = [column['name'] for column in columns_dict]
        fusion_table_service = get_fusion_table_service()

        # construct values
        values = u"'{lat} {lng}', '{address}'".format(
            lat=google_map_location.lat,
            lng=google_map_location.lng,
            address=google_map_location.address)

        # construct the fusion table query
        sql_query = u"INSERT INTO {table_id} ({columns}) VALUES ({values})".format(
            table_id=table_id,
            columns=", ".join(columns),
            values=values
        )
        request = fusion_table_service.query().sql(sql=sql_query)
        return request.execute()


def clear_fusion_table():
    """ clear all fusion table rows """
    from .models import GoogleFusionTable

    # get or create fusion table
    google_fusion_table = GoogleFusionTable.objects.get_fusion_table()
    if google_fusion_table:
        table_id = google_fusion_table.table_id
        fusion_table_service = get_fusion_table_service()

        # construct the fusion table query
        sql_query = u"DELETE FROM {table_id}".format(table_id=table_id)
        request = fusion_table_service.query().sql(sql=sql_query)
        return request.execute()
