# Censo IBGE

Nesse repositório ficarão os programas de captura de dados do Censo IBGE.
O único programa funcional atualmente é o que baixa dados de estimativa da
população.


## Licença

A licença do código é [LGPL3](https://www.gnu.org/licenses/lgpl-3.0.en.html) e
dos dados convertidos [Creative Commons Attribution
ShareAlike](https://creativecommons.org/licenses/by-sa/4.0/). Caso utilize os
dados, **cite a fonte original e quem tratou os dados**, como: **Fonte: IBGE,
dados tratados por Álvaro Justen/[Brasil.IO](https://brasil.io/)**. Caso
compartilhe os dados, **utilize a mesma licença**.


## Dados

Se esse programa e/ou os dados resultantes foram úteis a você ou à sua empresa,
considere [fazer uma doação ao projeto Brasil.IO](https://brasil.io/doe), que é
mantido voluntariamente.


## Instalando

Testado em Python 3.8.2 (pode ser que funcione em outras versões).

```shell
pip install -r requirements.txt
```

## Rodando

```shell
python populacao_estimada.py
```
