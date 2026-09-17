import logging
from collections.abc import Callable
from enum import EnumType

from pygrister.api import GristApi

logger = logging.getLogger(__name__)

def not_in_grist(fieldname) -> str:
    return fieldname + " is not in GRIST"

class GristService():
    def __init__(self, doc_id, doc_team_site, doc_self_hosted_server=None):

        config = {
            'GRIST_DOC_ID': doc_id,
            'GRIST_TEAM_SITE': doc_team_site
        }
        if doc_self_hosted_server:
            config['GRIST_SELF_MANAGED'] = "Y"
            config['GRIST_SELF_MANAGED_HOME'] = doc_self_hosted_server

        self.grist = GristApi(config=config)

    def get_grist_data(self, table, config_enum: EnumType, should_be_exported: Callable[[dict], bool]) -> \
    list[dict]:

        # fetch all the rows
        status, raw_data = self.grist.list_records(table)

        grist_data: list[dict] = []
        for record in raw_data:
            if should_be_exported(record):
                record_data = {'id': record["id"]}
                for enum_item in config_enum:
                    if enum_item.value in record:
                        record_data[enum_item.name] = record[enum_item.value]
                    else:
                        record_data[enum_item.name] = not_in_grist(enum_item.name)
                grist_data.append(record_data)
        return grist_data

    def get_table_records(self, table) -> list[dict]:
        """Toutes les lignes d'une table (ex : table de blocs répétables)."""
        status, records = self.grist.list_records(table)
        if status != 200:
            raise RuntimeError(f"Lecture de la table Grist '{table}' impossible : HTTP {status}")
        return records

    def update_grist_data(self, table, data):
        status, response = self.grist.update_records(table, data)
        if status != 200 :
            logger.error(f"Failed to update data: HTTP {status}")

    def upload_attachments(
        self,
        filepath: str,
    ) -> str:
        status, attachment_ids = self.grist.upload_attachments([filepath])

        #return "mock_upload_id"

        if status != 200 or not attachment_ids:
            logger.error(f"Failed to upload attachment: HTTP {status}")
            print("error")

        attachment_id = attachment_ids[0]  # Récupérer le premier ID
        logger.info(
            f"Successfully uploaded file, attachment ID: {attachment_id}"
        )
        print(f"Successfully uploaded file, attachment ID: {attachment_id}"
)

        return attachment_id
