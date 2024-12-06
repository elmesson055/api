# Guia Power BI - API

## Configuração Básica

1. No Power BI Desktop:
   - Obter Dados > Web
   - Cole a URL: `http://[seu-servidor]/api/api.php`

2. Parâmetros disponíveis:
   - `?page=1` (página)
   - `&limit=100` (registros por página)
   - `&data_inicial=2024-01-01`
   - `&data_final=2024-01-31`
   - `&tipdoc=CON` (ou NFS, ORT)

3. Exemplo URL completa:
```
http://[seu-servidor]/api/api.php?page=1&limit=100&data_inicial=2024-01-01&data_final=2024-01-31
```

4. No Editor Power Query:
   - Expandir coluna "data"
   - Ajustar tipos de dados (datas e números)
