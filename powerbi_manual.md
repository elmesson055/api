# Guia Rápido: Consumo da API no Power BI

## URL Base
```
http://[seu-servidor]/api/api.php
```

## Parâmetros
- page: número da página (padrão: 10)
- limit: registros por página (padrão: 100)
- data_inicial: YYYY-MM-DD
- data_final: YYYY-MM-DD
- tipdoc: CON, NFS ou ORT

## No Power BI

1. Obter Dados > Web
2. URL exemplo:
```
http://[seu-servidor]/api/api.php?page=1&limit=100&data_inicial=2024-01-01&data_final=2024-01-31
```

3. Transformar Dados:
   - Expandir coluna "data"
   - Converter datas e números
   - Remover colunas extras

4. Campos Disponíveis:
   - EMPRESA
   - FILIAL
   - TIPDOC
   - NUMDOC
   - DATA_EMISSAO
   - DATA_VENCIMENTO
   - DATA_PAGAMENTO
   - CLIENTE
   - VALOR_TOTAL
   - VALOR_DESCONTO
   - VALOR_PAGAMENTO
   - DISTRIBUICAO_TIPO
   - DISTRIBUICAO_OPERACAO
   - TIPO_CTE

## Código M (Power Query) Básico
```
let
    Fonte = Json.Document(Web.Contents("http://[seu-servidor]/api/api.php",
        [Query=[page="1", limit="100"]])),
    dados = Fonte[data],
    #"Expandir" = Table.ExpandRecordColumn(dados, "Column1", {"EMPRESA", "FILIAL", "TIPDOC", "NUMDOC", "DATA_EMISSAO", "VALOR_TOTAL"})
in
    #"Expandir"
```
