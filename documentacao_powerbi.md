# Documentação da API para Power BI

## Endpoint da API
```
http://[seu-servidor]/api/api.php
```

## Parâmetros de Consulta
| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| page | número | Página atual (padrão: 10) | ?page=1 |
| limit | número | Quantidade de registros por página (padrão: 100) | ?limit=50 |
| data_inicial | data | Data inicial para filtro (formato: YYYY-MM-DD) | ?data_inicial=2024-01-01 |
| data_final | data | Data final para filtro (formato: YYYY-MM-DD) | ?data_final=2024-01-31 |
| tipdoc | texto | Tipo de documento (CON, NFS, ORT) | ?tipdoc=CON |

## Como Consumir no Power BI

### Passo 1: Obter Dados
1. Abra o Power BI Desktop
2. Clique em "Obter Dados"
3. Selecione "Web"
4. Cole a URL da API com os parâmetros desejados

### Passo 2: Configurar a URL
Exemplo de URL completa:
```
http://[seu-servidor]/api/api.php?page=1&limit=100&data_inicial=2024-01-01&data_final=2024-01-31
```

### Passo 3: Transformar os Dados
1. O Power BI irá receber um JSON com a seguinte estrutura:
```json
{
    "status": "success",
    "data": [
        {
            "EMPRESA": "...",
            "FILIAL": "...",
            "TIPDOC": "...",
            "NUMDOC": "...",
            "NUMDOC_ORI": "...",
            "DATA_EMISSAO": "...",
            "DATA_VENCIMENTO": "...",
            "DATA_PAGAMENTO": "...",
            "CLIENTE": "...",
            "TIPDIS": "...",
            "VALOR_TOTAL": "...",
            "MES": "...",
            "CHAVE": "...",
            "VALOR_DESCONTO": "...",
            "VALOR_PAGAMENTO": "...",
            "DISTRIBUICAO_TIPO": "...",
            "DISTRIBUICAO_OPERACAO": "...",
            "DISTRIBUICAO_CONHECIMENTO": "...",
            "TIPO_CTE": "...",
            "CADGER_FREAUT_GRP": "..."
        }
    ],
    "pagination": {
        "page": 1,
        "limit": 100,
        "total": 1000,
        "total_pages": 10
    }
}
```

2. No Editor do Power Query:
   - Expanda a coluna "data" para obter todos os campos
   - Converta os campos de data para o tipo Data
   - Converta os campos numéricos para o tipo Número Decimal
   - Remova colunas desnecessárias se houver

### Passo 4: Dicas de Uso
1. **Paginação**: Para obter todos os dados, você pode:
   - Usar um número alto no parâmetro 'limit'
   - Ou criar uma função para fazer múltiplas chamadas e combinar os resultados

2. **Atualização**: 
   - Configure a atualização automática no Power BI Service
   - Recomendado usar filtros de data para otimizar o carregamento

3. **Tipos de Documentos**:
   - CON: Conhecimento
   - NFS: Nota Fiscal de Serviço
   - ORT: Outros

## Exemplo de Função M (Power Query)
```m
let
    Fonte = Json.Document(Web.Contents("http://[seu-servidor]/api/api.php", 
        [
            Query=[
                page="1",
                limit="100",
                data_inicial="2024-01-01",
                data_final="2024-01-31"
            ]
        ]
    )),
    dados = Fonte[data],
    #"Expandir Colunas" = Table.ExpandRecordColumn(
        dados, 
        "Column1", 
        {"EMPRESA", "FILIAL", "TIPDOC", "NUMDOC", "DATA_EMISSAO", "VALOR_TOTAL"},
        {"EMPRESA", "FILIAL", "TIPDOC", "NUMDOC", "DATA_EMISSAO", "VALOR_TOTAL"}
    )
in
    #"Expandir Colunas"
```

## Suporte
Para suporte ou dúvidas adicionais, entre em contato com a equipe de TI.
