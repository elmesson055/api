from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="API de Dados Logísticos",
    description="API para consulta de dados de documentos, conhecimentos e notas fiscais",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração da conexão com o banco de dados
def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};'
            f'SERVER={os.getenv("DB_SERVER")};'
            f'DATABASE={os.getenv("DB_NAME")};'
            f'UID={os.getenv("DB_USER")};'
            f'PWD={os.getenv("DB_PASSWORD")}'
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {str(e)}")

class DocumentoResponse(BaseModel):
    EMPRESA: Optional[str]
    FILIAL: Optional[str]
    TIPDOC: Optional[str]
    NUMDOC: Optional[str]
    NUMDOC_ORI: Optional[str]
    DATA_EMISSAO: Optional[datetime]
    DATA_VENCIMENTO: Optional[datetime]
    DATA_PAGAMENTO: Optional[datetime]
    CLIENTE: Optional[str]
    TIPDIS: Optional[str]
    VALOR_TOTAL: Optional[float]
    MES: Optional[str]
    CHAVE: Optional[str]
    VALOR_DESCONTO: Optional[float]
    VALOR_PAGAMENTO: Optional[float]
    DISTRIBUICAO_TIPO: Optional[str]
    DISTRIBUICAO_OPERACAO: Optional[str]
    DISTRIBUICAO_CONHECIMENTO: Optional[str]
    TIPO_CTE: Optional[str]
    CADGER_FREAUT_GRP: Optional[str]

@app.get("/documentos/", response_model=list[DocumentoResponse])
async def get_documentos(
    skip: int = Query(0, description="Número de registros para pular (paginação)"),
    limit: int = Query(100, description="Número máximo de registros para retornar"),
    data_inicial: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_final: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    tipdoc: Optional[str] = Query(None, description="Tipo de documento (CON, NFS, ORT)")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base da query
        query = """
        WITH CTE_DOC_CR AS (
            SELECT 
                A.EMPRESA, A.FILIAL, A.TIPDOC, A.NUMDOC, A.NUMDOC_ORI, 
                A.DATEMI, A.DATVEN_ATUAL, A.DATPAG, A.CLIENTE, A.VALTOT,
                CONVERT(VARCHAR(7), A.DATEMI, 111) AS MES,
                CONCAT(A.FILIAL, A.TIPDOC, A.NUMDOC) AS CHAVE,
                A.VALDES, A.VALPAG, A.COMP_TIPDOC, A.COMP_NUMDOC, A.COMP_DATCOM
            FROM [TAB DOC CR] AS A
            WHERE A.TIPDOC IN ('CON', 'NFS', 'ORT')
        ),
        CTE_CONHECIMENTO AS (
            SELECT 
                A.EMPRESA, A.FILIAL, A.TIPDOC, A.NUMDOC AS NUMDOC_REAL, 
                A.NUMDOC_1 AS NUMDOC_INTERNO, A.[DAT-EMI] AS DATA_EMISSAO, 
                A.PAGADOR AS CLIENTE, A.TIPDIS AS TIPDIS, A.[C-TOTAL] AS VALOR,
                B.DESCRICAO AS DISTRIBUICAO, C.TIPCON_D AS TIPO_CTE
            FROM [TAB DE CONHECIMENTO] AS A
            LEFT JOIN [TAB TIPO DISTRIBUICAO] AS B ON A.TIPDIS = B.TIPDIS
            LEFT JOIN [TAB TIPCON] AS C ON A.TIPOCTRC = C.TIPCON
            WHERE A.SubistituidoAnulado = 0 AND A.CANCELADO = 0 
            AND A.TIPDOC IN ('CON', 'NFS', 'ORT')
        ),
        CTE_NF AS (
            SELECT 
                A.EMPRESA, A.FILIAL, A.TIPDOC, A.NUMDOC AS NUMDOC_REAL, 
                A.NUMDOC_1 AS NUMDOC_INTERNO, A.DATEMI AS DATA_EMISSAO, 
                A.CLIENTE, A.CTRE AS TIPDIS, A.TOT_VALBRU AS VALOR,
                B.CTRE_DES AS DISTRIBUICAO_OPERACAO
            FROM [TAB NF] AS A
            LEFT JOIN [TAB CTRE] AS B ON A.CTRE = B.CTRE
            WHERE A.CANCELADO = 0 AND A.FLAG_PREV = 0 
            AND A.TIPDOC IN ('CON', 'NFS', 'ORT')
        )
        SELECT 
            DC.EMPRESA, DC.FILIAL, DC.TIPDOC, DC.NUMDOC, DC.NUMDOC_ORI, 
            DC.DATEMI AS DATA_EMISSAO, DC.DATVEN_ATUAL AS DATA_VENCIMENTO, 
            DC.DATPAG AS DATA_PAGAMENTO, DC.CLIENTE, K.TIPDIS,
            DC.VALTOT AS VALOR_TOTAL, DC.MES, DC.CHAVE,
            DC.VALDES AS VALOR_DESCONTO, DC.VALPAG AS VALOR_PAGAMENTO,
            K.DESCRICAO AS DISTRIBUICAO_TIPO, NF.DISTRIBUICAO_OPERACAO,
            CNH.DISTRIBUICAO AS DISTRIBUICAO_CONHECIMENTO, CNH.TIPO_CTE,
            L.CADGER_FREAUT_GRP
        FROM CTE_DOC_CR AS DC
        LEFT JOIN CTE_CONHECIMENTO AS CNH
            ON DC.EMPRESA = CNH.EMPRESA AND DC.FILIAL = CNH.FILIAL 
            AND DC.NUMDOC = CNH.NUMDOC_REAL
        LEFT JOIN CTE_NF AS NF
            ON DC.EMPRESA = NF.EMPRESA AND DC.FILIAL = NF.FILIAL 
            AND DC.NUMDOC = NF.NUMDOC_REAL
        LEFT JOIN [TAB TIPO DISTRIBUICAO] AS K ON CNH.TIPDIS = K.TIPDIS
        LEFT JOIN [TAB DE DESTINATARIO] AS L ON DC.CLIENTE = L.DESTINATARIO
        WHERE DC.TIPDOC IN ('CON', 'NFS', 'ORT')
        """

        # Adicionar filtros condicionais
        if data_inicial:
            query += f" AND DC.DATEMI >= '{data_inicial}'"
        if data_final:
            query += f" AND DC.DATEMI <= '{data_final}'"
        if tipdoc:
            query += f" AND DC.TIPDOC = '{tipdoc}'"

        # Adicionar ordenação e paginação
        query += f" ORDER BY DC.DATEMI DESC OFFSET {skip} ROWS FETCH NEXT {limit} ROWS ONLY"

        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Converter resultados para dicionário
        columns = [column[0] for column in cursor.description]
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            results.append(result)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
