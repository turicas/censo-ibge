from itertools import groupby

from rows.plugins.plugin_pdf import PyMuPDFBackend


def parse_file(filename):
    doc = PyMuPDFBackend(filename)
    started = False
    objs = []
    for page_number, page in enumerate(doc.text_objects(), start=1):
        for obj in page:
            if not started and obj.text == "POPULAÇÃO":
                started = True
                continue
            if started and obj.text.startswith("Fonte: IBGE"):
                break
            if started:
                objs.append((page_number, obj))

    header = "state,state_ibge_code,city_ibge_code,city,estimated_population".split(",")
    sort = lambda obj: (obj[0], obj[1].y0, obj[1].x0)
    objs.sort(key=sort)
    for key, group in groupby(objs, key=lambda obj: (obj[0], obj[1].y0)):
        group = sorted(group, key=sort)
        data = [obj.text.strip() for page, obj in group if obj.text.strip()]
        assert len(data) == 5
        row = dict(zip(header, data))
        row["state_ibge_code"] = int(row["state_ibge_code"])
        row["estimated_population"] = int(row["estimated_population"].replace(".", ""))
        yield row


if __name__ == "__main__":
    import argparse


    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_filename")  # Exemplo: TO_POP2022.pdf
    args = parser.parse_args()

    for row in parse_file(args.pdf_filename):
        print(row)
