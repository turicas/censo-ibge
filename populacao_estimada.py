import unicodedata
from ftplib import FTP
from pathlib import Path
from unicodedata import normalize
from urllib.parse import urljoin, urlparse

import requests
import rows
import xlrd
from lxml.html import document_fromstring, tostring
from tqdm import tqdm


class IbgeScraper:

    def __init__(self):
        self.session = requests.Session()

    def parse_html_table_list(self, url):
        response = self.session.get(url)
        tree = document_fromstring(response.text)
        table = []
        for tr in tree.xpath("//table//tr"):
            data = [
                (
                    " ".join([item.strip() for item in td.xpath(".//text()") if item.strip()]),
                    td.xpath(".//a/@href"),
                )
                for td in tr.xpath(".//td")
            ]
            if not data:
                continue
            if data[0] == ('', []):
                data = data[1:]
            table.append(data)
        header = "url date size _".split()
        for row in table[1:]:
            row = (row[0][1][0], row[1][0].split()[0], row[2][0], row[3][0])
            row = dict(zip(header, row))
            row["url"] = urljoin(url, row["url"])
            yield row

    def list_xls_urls(self, start_year=2000, end_year=2021):
        # TODO: get URLs for other formats (such as .zip)
        anos_censo = (1980, 1991, 2000, 2010, 2022)
        urls = {}
        for ano in range(start_year, end_year + 1):
            urls[ano] = {}
            if ano not in anos_censo:  # Estimativa
                url = f"https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_{ano}/"
                for row in self.parse_html_table_list(url):
                    if not row["url"].endswith(".xls") or Path(row["url"]).name.startswith("serie"):
                        continue
                    urls[ano][row["date"]] = row["url"]
            else:
                url = f"https://ftp.ibge.gov.br/Censos/Censo_Demografico_{ano}/"
                # TODO: implementar o restante
        return urls


class CustomIntegerField(rows.fields.IntegerField):
    @classmethod
    def deserialize(cls, value):
        value = str(value or "").strip()
        if not value:
            return None
        value = value.replace("*", "").replace(".", "")
        if "(" in value:
            value = value.split("(")[0].strip()
        return super().deserialize(value)


def download_ftp_file(url, output_filename, skip_if_downloaded=False):
    if skip_if_downloaded and Path(output_filename).exists():
        return

    parsed = urlparse(url)
    host = parsed.netloc
    path = str(Path(parsed.path).parent)
    filename = str(Path(parsed.path).name)
    server = FTP(host)
    server.login()
    server.cwd(path)
    with open(output_filename, mode="wb") as fobj:
        server.retrbinary(f"RETR {filename}", fobj.write)
    server.quit()
    return filename

def normaliza(texto):
    "Remove acentos, espaços em branco e coloca para minúsculas"
    return normalize("NFKD", texto).encode("ascii", errors="ignore").decode("ascii").strip().lower()


def convert_file(input_filename, output_filename):
    book = xlrd.open_workbook(input_filename, formatting_info=True)
    selected_sheet = None
    sheet_names = book.sheet_names()
    for sheet_name in sheet_names:
        normalized = normaliza(sheet_name)
        if normalized == "municipios":
            selected_sheet = sheet_name
            break
    if selected_sheet is None:
        raise RuntimeError(f"Aba 'Municípios' não encontrada na planilha (existentes: {', '.join(sheet_names)})")
    sheet = book.sheet_by_name(selected_sheet)
    column_uf = sheet.col(0)
    for start_row, cell in enumerate(column_uf):
        if str(cell.value or "").strip() == "UF":
            break

    header = [normaliza(cell.value) for cell in sheet.row(start_row)]
    force_types = {
        "cod_uf": rows.fields.TextField,
        "cod_munic": rows.fields.TextField,
    }
    tem_populacao_estimada = "populacao estimada" in header
    if tem_populacao_estimada:
        force_types["populacao_estimada"] = CustomIntegerField
    else:  # Censo 2022 não tem população estimada
        force_types["populacao"] = CustomIntegerField

    table = rows.import_from_xls(
        input_filename,
        sheet_name=selected_sheet,
        start_row=start_row,
        force_types=force_types,
    )
    result = []
    for row in table:
        if not row.uf.strip() or "fonte:" in row.uf.strip().lower():
            # End of data
            break
        result.append(
            {
                "uf": row.uf,
                "codigo_uf": row.cod_uf,
                "codigo_municipio": f"{row.cod_uf}{row.cod_munic}",
                "municipio": row.nome_do_municipio.replace("*", "").strip(),
                "populacao": row.populacao_estimada if tem_populacao_estimada else row.populacao,
            }
        )
    result.sort(key=lambda row: (row["uf"], normaliza(row["municipio"])))
    writer = rows.utils.CsvLazyDictWriter(output_filename)
    for row in result:
        writer.writerow(row)


if __name__ == "__main__":
    DATA_PATH = Path(__file__).parent / "data"
    DOWNLOAD_PATH = DATA_PATH / "download"
    OUTPUT_PATH = DATA_PATH / "output"
    for path in (DOWNLOAD_PATH, OUTPUT_PATH):
        if not path.exists():
            path.mkdir(parents=True)

    # This dict must be updated using `IbgeScraper.list_xls_urls()`
    urls = {
        2012: {
            "2017-06-14": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2012/estimativa_2012_TCU_20170614.xls",
        },
        2013: {
            "2017-06-14": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2013/estimativa_2013_TCU_20170614.xls",
        },
        2014: {
            "2017-06-14": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2014/estimativa_TCU_2014_20170614.xls",
        },
        2015: {
            "2017-06-14": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2015/estimativa_TCU_2015_20170614.xls",
            "2016-08-17": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2015/estimativa_dou_2015_20150915.xls",
        },
        2016: {
            "2017-07-14": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2016/estimativa_TCU_2016_20170614.xls",
        },
        2017: {
            "2022-09-05": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2017/POP2017_20220905.xls",
            "2017-08-30": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2017/estimativa_dou_2017.xls",
        },
        2018: {
            "2022-09-05": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2018/POP2018_20220905.xls",
            "2019-09-10": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2018/estimativa_dou_2018_20181019.xls",
        },
        2019: {
            "2022-09-05": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/POP2019_20220905.xls",
            "2019-09-17": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/estimativa_dou_2019.xls",
        },
        2020: {
            "2022-07-11": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2020/POP2020_20220711.xls",
            "2022-09-05": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2020/POP2020_20220905.xls",
            "2020-08-27": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2020/estimativa_dou_2020.xls",
        },
        2021: {
            "2024-06-24": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/POP2021_20240624.xls",
            "2021-08-27": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2021/estimativa_dou_2021.xls",
        },
        2022: {
            "2023-06-22": "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Previa_da_Populacao/POP2022_Municipios_20230622.xls",
        },
        2024: {
            "2024-11-01": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2024/POP2024_20241101.xls",
            "2024-12-30": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2024/POP2024_20241230.xls",
        },
        2025: {
            "2025-09-01": "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2025/estimativa_dou_2025.xls",
        },
    }
    for year, year_data in urls.items():
        for release_date, url in year_data.items():
            download_filename = DOWNLOAD_PATH / Path(url).name
            output_filename = OUTPUT_PATH / f"populacao-{year}_{release_date}.csv"

            print(f"Downloading {url} to {download_filename}")
            download_ftp_file(url, download_filename, skip_if_downloaded=True)

            print(f"  Converting to {output_filename}")
            convert_file(download_filename, output_filename)
