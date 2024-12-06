# API de Consulta de Documentos

API RESTful em PHP para consulta de documentos no banco de dados SQL Server.

## Requisitos

- PHP 7.4 ou superior
- Extensão PDO_SQLSRV do PHP
- SQL Server

## Endpoints

### GET /api.php

Retorna os documentos paginados do banco de dados.

#### Parâmetros de Query

- `page` (opcional): Número da página (padrão: 1)
- `limit` (opcional): Quantidade de registros por página (padrão: 100)
- `data_inicial` (opcional): Filtro de data inicial (formato: YYYY-MM-DD)
- `data_final` (opcional): Filtro de data final (formato: YYYY-MM-DD)
- `tipdoc` (opcional): Tipo de documento (CON, NFS, ORT)

#### Exemplo de Uso

```
GET /api.php?page=1&limit=10&data_inicial=2023-01-01&data_final=2023-12-31&tipdoc=CON
```

#### Resposta

```json
{
    "status": "success",
    "data": [...],
    "pagination": {
        "page": 1,
        "limit": 10,
        "total": 100,
        "total_pages": 10
    }
}
```

## Configuração

As configurações de conexão com o banco de dados estão no arquivo `config/database.php`.

## Integração com PowerBI

Para conectar esta API ao PowerBI:

1. No PowerBI Desktop, clique em "Obter Dados"
2. Selecione "Web"
3. Insira a URL da API (exemplo: http://seu-servidor/api/api.php)
4. O PowerBI irá automaticamente reconhecer o JSON retornado

## Integração com Sistemas Web

A API suporta CORS e pode ser consumida por qualquer aplicação web usando fetch ou axios:

```javascript
fetch('http://mtpc-147/api/api.php?page=1&limit=10')
    .then(response => response.json())
    .then(data => console.log(data));
```
