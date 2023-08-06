from .base_ingestor import BaseIngestor

class CsvIngestor(BaseIngestor):
    def __init__(self, log, srcfile, jira, issue_types, fields, project, issue_default_fields):
        self._log = log
        self._srcfile = srcfile
        super().__init__(project, issue_types, fields, issue_default_fields, jira, log)

    fid = 'csv_field'

    def ingest(self):
        for row in self._srcfile:
            self._log.info('Ingesting row: {}'.format(row['Plugin ID']))
            row['Description'] = row['Description'].replace("\n", " ")
            self._process_open_vuln(row, self.fid)