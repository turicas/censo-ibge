from ftplib import FTP
from pathlib import Path
from unicodedata import normalize
from urllib.parse import urlparse

import rows


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


def to_ascii(text):
    return normalize("NFKD", text).encode("ascii", errors="ignore").decode("ascii")


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


def convert_file(input_filename, output_filename):
    table = rows.import_from_xls(
        input_filename,
        sheet_name="Municípios",
        start_row=1,
        force_types={
            "cod_uf": rows.fields.TextField,
            "cod_munic": rows.fields.TextField,
            "populacao_estimada": CustomIntegerField,
        },
    )
    result = []
    for row in table:
        if not row.uf.strip() or "fonte:" in row.uf.strip().lower():
            # End of data
            break
        result.append(
            {
                "state": row.uf,
                "state_ibge_code": row.cod_uf,
                "city_ibge_code": f"{row.cod_uf}{row.cod_munic}",
                "city": row.nome_do_municipio.replace("*", "").strip(),
                "estimated_population": row.populacao_estimada,
            }
        )
    result.sort(key=lambda row: (row["state"], to_ascii(row["city"])))
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

    urls = {
        "2019-09-16": "ftp://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/estimativa_dou_2019.xls",
        "2020-06-22": "ftp://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/estimativa_TCU_2019_20200622.xls",
        "2020-07-20": "ftp://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/POP2019_20072020.xls",
        "2020-08-27": "ftp://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2020/estimativa_dou_2020.xls",
    }
    for date, url in urls.items():
        download_filename = DOWNLOAD_PATH / Path(url).name
        output_filename = OUTPUT_PATH / f"populacao-{date}.csv"

        print(f"Downloading {url} to {download_filename}")
        download_ftp_file(url, download_filename, skip_if_downloaded=True)

        print(f"  Converting to {output_filename}")
        convert_file(download_filename, output_filename)
