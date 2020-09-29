import argparse
from pathlib import Path

import rows


def pdf_to_csv(input_filename, output_filename):
    total_pages = rows.plugins.pdf.number_of_pages(input_filename)
    pdf = rows.plugins.pdf.PyMuPDFBackend(input_filename)
    result = []
    for page_number in range(1, total_pages + 1):
        page = list(next(pdf.objects(page_numbers=(page_number,))))
        data = list(rows.plugins.utils.ipartition(page, 4))
        header = [obj.text for obj in data[0]]
        for row in data[1:]:
            row = dict(zip(header, [obj.text for obj in row]))
            row["codigo_ibge"] = row.pop("IBGE")
            row["perfil"] = row.pop("Perfil Município")
            result.append(row)
    table = rows.import_from_dicts(result)
    rows.export_to_csv(table, output_filename)


if __name__ == "__main__":
    DATA_PATH = Path(__file__).parent / "data"
    DOWNLOAD_PATH = DATA_PATH / "download"
    OUTPUT_PATH = DATA_PATH / "output"
    original_url = "http://maismedicos.gov.br/images/PDF/Perfis-de-todos-os-municipios-15Maio2019.pdf"
    mirror_url = "https://data.brasil.io/mirror/maismedicos/Perfis-de-todos-os-municipios-15Maio2019.pdf"
    for path in (DOWNLOAD_PATH, OUTPUT_PATH):
        if not path.exists():
            path.mkdir(parents=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--use-mirror", action="store_true")
    args = parser.parse_args()
    url = original_url if not args.use_mirror else mirror_url

    input_filename = DOWNLOAD_PATH / Path(url).name
    output_filename = OUTPUT_PATH / "perfil-municipio.csv"
    rows.utils.download_file(url, input_filename, progress=True)
    pdf_to_csv(input_filename, output_filename)
