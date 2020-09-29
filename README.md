# Censo IBGE

Programas de captura de dados do Censo IBGE e informações
relacionadas/relevantes sobre municípios brasileiros.

Os programas serão adicionados aos poucos; no momento temos:

- População estimada por município (para várias datas)
- Perfil do município (segundo Mais Médicos)


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


### População Estimada

População por município estimada pelo IBGE, disponível em diversas datas. Veja
o schema em `schema/populacao-estimada.csv`.


### Perfil dos Municípios

- 1: Grupos III e IV do PAB
- 2: Grupo II do PAB
- 3: Capitais e regiões metropolitanas
- 4: Grupo I do PAB
- 5: G100
- 6: Áreas vulneráveis
- 7: Extrema Pobreza

> Nota 1: [PAB = Piso de Atenção
> Básica](https://bvsms.saude.gov.br/bvs/publicacoes/sus_az_garantindo_saude_municipios_3ed_p2.pdf),
> recursos financeiros federais destinados à viabilização de ações de atenção
> básica à saúde nos municípios.

> Nota 2:
> [G100](https://www2.camara.leg.br/atividade-legislativa/comissoes/comissoes-temporarias/especiais/55a-legislatura/reforma-tributaria/documentos/audiencias-e-eventos/apresentacao-prefeito-elias-gomes)
> = 100 municípios com mais 80 mil habitantes com as menores receitas per
> capita na média dos três últimos anos e os maiores índices de vulnerabilidade
> socioeconômica (educação, saúde e pobreza).


## Instalando

Testado em Python 3.8.2 (pode ser que funcione em outras versões).

```shell
pip install -r requirements.txt
```

## Rodando

```shell
python populacao_estimada.py
python perfil_municipio_maismedicos.py
```
