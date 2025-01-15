import json
import os
from dateutil import rrule
import dateutil.relativedelta as relativedelta
import datetime
import zipfile
import tldextract

from google.cloud import bigquery
from google.oauth2 import service_account


class CrUXDownloader:

    GLOBAL_SQL = """SELECT distinct origin, experimental.popularity.rank
        FROM `chrome-ux-report.experimental.global`
        WHERE yyyymm = ?
        GROUP BY origin, experimental.popularity.rank
        ORDER BY experimental.popularity.rank;"""

    COUNTRY_SQL = """SELECT distinct country_code, origin, experimental.popularity.rank
        FROM `chrome-ux-report.experimental.country`
        WHERE yyyymm = ?
        GROUP BY country_code, origin, experimental.popularity.rank
        ORDER BY country_code, experimental.popularity.rank;"""

    def __init__(self, credentials_path=None, credentials_json=None, credentials_env=False):
        if not credentials_path and not credentials_json and not credentials_env:
            raise Exception("No credentials supplied for Google Cloud")
        if credentials_env:
            self._bq_client = bigquery.Client()
        elif credentials_json:
            obj = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(obj)
            self._bq_client = bigquery.Client(credentials=credentials)
        else:
            self._bq_client = bigquery.Client.from_service_account_json(credentials_path)

    def _extract_domain(self, url):
        # Extract domain and suffix using tldextract
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"

    def dump_month_to_csv(self, scope, yyyymm: int, path):
        assert scope in {"global", "country"}
        query = self.GLOBAL_SQL if scope == "global" else self.COUNTRY_SQL
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(None, "INT64", yyyymm),
            ]
        )
        df = self._bq_client.query(query, job_config=job_config).to_dataframe()
        if df.empty:
            return

        # Process URLs to extract domains
        df['domain'] = df['origin'].apply(lambda x: self._extract_domain(x))
        
        # Drop duplicates keeping the highest rank (lowest number)
        df = df.sort_values('rank').drop_duplicates(subset='domain', keep='first')
        
        # Save only domain and rank
        df[['domain', 'rank']].to_csv(path, index=False, header=True)
        return path


class CrUXRepoManager:

    MIN_YYYYMM = datetime.datetime(2021, 2, 1)
    GLOBAL_DIR_NAME = "global"
    COUNTRY_DIR_NAME = "country"
    GLOBAL_FILENAME = "crux-top-10m.csv"

    @classmethod
    def _iter_valid_YYYYMM(cls):
        now = datetime.datetime.now()
        last_month = now + relativedelta.relativedelta(months=-1)
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=cls.MIN_YYYYMM,
                until=last_month):
            yield (dt.year, dt.month)

    def __init__(self, data_directory):
        self._data_directory = data_directory
        self._global_directory = os.path.join(data_directory,
                self.GLOBAL_DIR_NAME)
        self._country_directory = os.path.join(data_directory,
                self.COUNTRY_DIR_NAME)

    def _get_latest_YYYYMM(self):
        now = datetime.datetime.now()
        last_month = now + relativedelta.relativedelta(months=-1)
        return (last_month.year, last_month.month)

    def _make_directories(self):
        if not os.path.exists(self._global_directory):
            os.mkdir(self._global_directory)
        if not os.path.exists(self._country_directory):
            os.mkdir(self._country_directory)

    def _zip(self, filename, delete_original=True):
        zip_filename = os.path.splitext(filename)[0] + ".zip"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, os.path.basename(filename))
        if delete_original:
            os.remove(filename)

    def _clean_existing_files(self, base_filename):
        # Remove any existing CSV and ZIP files
        csv_path = os.path.join(self._global_directory, base_filename)
        zip_path = os.path.splitext(csv_path)[0] + ".zip"
        
        if os.path.exists(csv_path):
            os.remove(csv_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    def download(self, credentials_path=None, credentials_json=None, credentials_env=False):
        downloader = CrUXDownloader(
            credentials_path=credentials_path,
            credentials_json=credentials_json,
            credentials_env=credentials_env,
        )
        self._make_directories()
        
        # Get the latest month's data
        year, month = self._get_latest_YYYYMM()
        yyyymm = int(f"{year}{str(month).zfill(2)}")
        
        # Clean up existing files
        self._clean_existing_files(self.GLOBAL_FILENAME)
        
        # Download global data
        print("Fetching global data for {}".format(yyyymm))
        results_path = os.path.join(self._global_directory, self.GLOBAL_FILENAME)
        if downloader.dump_month_to_csv("global", yyyymm, results_path):
            self._zip(results_path, delete_original=True)  # Ensure we delete the CSV after zipping

        # TODO: Add country-specific data if needed
        # for scope in {"global", "country"}:
        #    data_directory = self._global_directory if scope == "global" else self._country_directory

