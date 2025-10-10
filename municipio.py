"""
Lê CSVs de população criados com `populacao_estimada.py` e gera arquivo final com cadastro de municípios

A planilha final conterá todos os códigos de município que já apareceram nas tabelas de população.
"""
import csv
import datetime
from collections import defaultdict
from pathlib import Path


output_path = Path("data") / "output"
output_filename = output_path / "municipio.csv"

codigos = defaultdict(list)
colunas = ("uf", "codigo_uf", "municipio")
for filename in output_path.glob("populacao-*.csv"):
    ano, data = filename.name.replace("populacao-", "").replace(".csv", "").split("_")
    ano = int(ano)
    data = datetime.datetime.fromisoformat(data).date()
    print(f"Processando {filename}")
    with filename.open(encoding="utf-8") as fobj:
        for row in csv.DictReader(fobj):
            codigos[row["codigo_municipio"]].append(
                tuple([row["codigo_municipio"], ano, data] + [row[col] for col in colunas])
            )

print(f"Criando {output_filename}")
with output_filename.open(mode="w") as fobj:
    writer = None
    for codigo, valores in codigos.items():
        valores.sort()
        _codigo, _ano, data, uf, codigo_uf, nome = valores[-1]
        codigo6 = str(codigo)[:6]
        if len(str(codigo)) != 7:
            print(f"WARN: código {repr(codigo)} com tamanho inesperado.")
        row = {
            "codigo": codigo,
            "codigo6": codigo6,
            "nome": nome,
            "uf": uf,
            "codigo_uf": codigo_uf,
            "ultima_aparicao": data,
        }
        if writer is None:
            writer = csv.DictWriter(fobj, fieldnames=list(row.keys()))
            writer.writeheader()
        writer.writerow(row)
