<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

include_once './config/database.php';

// Instancia a conexão com o banco
$database = new Database();
$conn = $database->getConnection();

// Pega os parâmetros da URL
$page = isset($_GET['page']) ? (int)$_GET['page'] : 10;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 100;
$data_inicial = isset($_GET['data_inicial']) ? $_GET['data_inicial'] : null;
$data_final = isset($_GET['data_final']) ? $_GET['data_final'] : null;
$tipdoc = isset($_GET['tipdoc']) ? $_GET['tipdoc'] : null;

// Calcula o offset
$offset = ($page -1 ) * $limit;

try {
    // Monta a query sem CTEs
    $query = "
        SELECT 
            DC.EMPRESA, 
            DC.FILIAL, 
            DC.TIPDOC, 
            DC.NUMDOC, 
            DC.NUMDOC_ORI, 
            DC.DATEMI AS DATA_EMISSAO, 
            DC.DATVEN_ATUAL AS DATA_VENCIMENTO, 
            DC.DATPAG AS DATA_PAGAMENTO, 
            DC.CLIENTE, 
            K.TIPDIS,
            DC.VALTOT AS VALOR_TOTAL, 
            CONVERT(VARCHAR(7), DC.DATEMI, 111) AS MES,
            CONCAT(DC.FILIAL, DC.TIPDOC, DC.NUMDOC) AS CHAVE,
            DC.VALDES AS VALOR_DESCONTO, 
            DC.VALPAG AS VALOR_PAGAMENTO,
            K.DESCRICAO AS DISTRIBUICAO_TIPO, 
            NF.DISTRIBUICAO_OPERACAO,
            CNH.DISTRIBUICAO AS DISTRIBUICAO_CONHECIMENTO, 
            CNH.TIPO_CTE,
            L.CADGER_FREAUT_GRP
        FROM [TAB DOC CR] AS DC
        LEFT JOIN (
            SELECT 
                A.EMPRESA, 
                A.FILIAL, 
                A.TIPDOC, 
                A.NUMDOC AS NUMDOC_REAL,
                A.TIPDIS,
                B.DESCRICAO AS DISTRIBUICAO, 
                C.TIPCON_D AS TIPO_CTE
            FROM [TAB DE CONHECIMENTO] A
            LEFT JOIN [TAB TIPO DISTRIBUICAO] B ON A.TIPDIS = B.TIPDIS
            LEFT JOIN [TAB TIPCON] C ON A.TIPOCTRC = C.TIPCON
            WHERE A.SubistituidoAnulado = 0 
            AND A.CANCELADO = 0 
            AND A.TIPDOC IN ('CON', 'NFS', 'ORT')
        ) CNH ON DC.EMPRESA = CNH.EMPRESA 
            AND DC.FILIAL = CNH.FILIAL 
            AND DC.NUMDOC = CNH.NUMDOC_REAL
        LEFT JOIN (
            SELECT 
                A.EMPRESA, 
                A.FILIAL, 
                A.TIPDOC, 
                A.NUMDOC AS NUMDOC_REAL,
                B.CTRE_DES AS DISTRIBUICAO_OPERACAO
            FROM [TAB NF] A
            LEFT JOIN [TAB CTRE] B ON A.CTRE = B.CTRE
            WHERE A.CANCELADO = 0 
            AND A.FLAG_PREV = 0 
            AND A.TIPDOC IN ('CON', 'NFS', 'ORT')
        ) NF ON DC.EMPRESA = NF.EMPRESA 
            AND DC.FILIAL = NF.FILIAL 
            AND DC.NUMDOC = NF.NUMDOC_REAL
        LEFT JOIN [TAB TIPO DISTRIBUICAO] K ON CNH.TIPDIS = K.TIPDIS
        LEFT JOIN [TAB DE DESTINATARIO] L ON DC.CLIENTE = L.DESTINATARIO
        WHERE DC.TIPDOC IN ('CON', 'NFS', 'ORT')
    ";

    // Adiciona filtros condicionais
    if ($data_inicial) {
        $query .= " AND DC.DATEMI >= '" . $data_inicial . "'";
    }
    if ($data_final) {
        $query .= " AND DC.DATEMI <= '" . $data_final . "'";
    }
    if ($tipdoc) {
        $query .= " AND DC.TIPDOC = '" . $tipdoc . "'";
    }

    // Adiciona ordenação e paginação
    $query .= " ORDER BY DC.DATEMI DESC OFFSET " . $offset . " ROWS FETCH NEXT " . $limit . " ROWS ONLY";

    // Executa a query
    $result = odbc_exec($conn, $query);
    if (!$result) {
        error_log("Erro na execução da query: " . odbc_errormsg());
        throw new Exception("Erro na consulta: " . odbc_errormsg());
    }

    // Busca os resultados
    $results = array();
    while ($row = odbc_fetch_array($result)) {
        $results[] = array_map('utf8_encode', $row);
    }

    // Verifica se temos resultados
    if (empty($results)) {
        $response = array(
            "status" => "success",
            "message" => "Nenhum resultado encontrado",
            "data" => array(),
            "pagination" => array(
                "page" => $page,
                "limit" => $limit,
                "total" => 0,
                "total_pages" => 0
            )
        );
    } else {
        // Busca o total de registros (sem paginação)
        $countQuery = "SELECT COUNT(*) as total FROM [TAB DOC CR] DC WHERE DC.TIPDOC IN ('CON', 'NFS', 'ORT')";
        if ($data_inicial) {
            $countQuery .= " AND DC.DATEMI >= '" . $data_inicial . "'";
        }
        if ($data_final) {
            $countQuery .= " AND DC.DATEMI <= '" . $data_final . "'";
        }
        if ($tipdoc) {
            $countQuery .= " AND DC.TIPDOC = '" . $tipdoc . "'";
        }

        $countResult = odbc_exec($conn, $countQuery);
        if (!$countResult) {
            throw new Exception("Erro na contagem: " . odbc_errormsg());
        }

        odbc_fetch_row($countResult);
        $totalCount = odbc_result($countResult, "total");

        $response = array(
            "status" => "success",
            "data" => $results,
            "pagination" => array(
                "page" => $page,
                "limit" => $limit,
                "total" => $totalCount,
                "total_pages" => ceil($totalCount / $limit)
            )
        );
    }

    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($response);

} catch(Exception $e) {
    http_response_code(500);
    echo json_encode(array(
        "status" => "error",
        "message" => "Database Error: " . $e->getMessage()
    ), JSON_UNESCAPED_UNICODE);
}

// Fecha a conexão
odbc_close($conn);
?>
