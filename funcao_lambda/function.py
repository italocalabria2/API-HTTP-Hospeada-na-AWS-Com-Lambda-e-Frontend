
import json
import os
import uuid
import datetime
import base64
from decimal import Decimal

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME")
#configurar a variável para:  "TABLE_NAME = os.environ.get("TABLE_NAME")"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

STATUS_VALIDOS = [
    "criado",
    "confirmado",
    "cancelado",
    "entregue"
]


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def agora_iso():
    return datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()


def resposta(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers":
                "Content-Type,Authorization",
            "Access-Control-Allow-Methods":
                "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        },
        "body": json.dumps(
            body,
            cls=DecimalEncoder,
            ensure_ascii=False
        )
    }


def corpo_json(event):

    body = event.get("body")

    if not body:
        return {}

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    return json.loads(
        body,
        parse_float=Decimal
    )


def obter_metodo_e_caminho(event):

    http = (
        event.get("requestContext", {})
        .get("http", {})
    )

    method = (
        http.get("method")
        or event.get("httpMethod")
        or ""
    )

    path = (
        event.get("rawPath")
        or event.get("path")
        or ""
    )

    partes = [
        p for p in path.split("/")
        if p
    ]

    return method.upper(), partes


def validar_pedido(dados):

    campos_obrigatorios = [
        "cliente",
        "email",
        "produto",
        "quantidade",
        "valorUnitario"
    ]

    for campo in campos_obrigatorios:
        if campo not in dados:
            return (
                f"Campo obrigatório ausente: {campo}"
            )

    status = dados.get("status")

    if status and status not in STATUS_VALIDOS:
        return "Status inválido"

    return None


def criar_pedido(event):

    try:
        dados = corpo_json(event)
    except Exception:
        return resposta(
            400,
            {"erro": "JSON inválido"}
        )

    erro = validar_pedido(dados)

    if erro:
        return resposta(
            400,
            {"erro": erro}
        )

    pedido_id = str(uuid.uuid4())

    agora = agora_iso()

    quantidade = Decimal(
        str(dados["quantidade"])
    )

    valor_unitario = Decimal(
        str(dados["valorUnitario"])
    )

    item = {
        "id": pedido_id,
        "cliente": dados["cliente"],
        "email": dados["email"],
        "produto": dados["produto"],
        "quantidade": quantidade,
        "valorUnitario": valor_unitario,
        "valorTotal":
            quantidade * valor_unitario,
        "status":
            dados.get("status", "criado"),
        "criadoEm": agora,
        "atualizadoEm": agora
    }

    table.put_item(Item=item)

    return resposta(
        201,
        {
            "mensagem":
                "Pedido criado com sucesso",
            "pedido": item
        }
    )


def listar_pedidos():

    resultado = table.scan()

    itens = resultado.get(
        "Items",
        []
    )

    return resposta(
        200,
        {
            "total": len(itens),
            "pedidos": itens
        }
    )


def buscar_pedido(pedido_id):

    resultado = table.get_item(
        Key={"id": pedido_id}
    )

    item = resultado.get("Item")

    if not item:
        return resposta(
            404,
            {
                "erro":
                    "Pedido não encontrado"
            }
        )

    return resposta(200, item)


def atualizar_pedido(event, pedido_id):

    resultado = table.get_item(
        Key={"id": pedido_id}
    )

    existente = resultado.get("Item")

    if not existente:
        return resposta(
            404,
            {
                "erro":
                    "Pedido não encontrado"
            }
        )

    try:
        dados = corpo_json(event)
    except Exception:
        return resposta(
            400,
            {"erro": "JSON inválido"}
        )

    erro = validar_pedido(dados)

    if erro:
        return resposta(
            400,
            {"erro": erro}
        )

    quantidade = Decimal(
        str(dados["quantidade"])
    )

    valor_unitario = Decimal(
        str(dados["valorUnitario"])
    )

    item = {
        "id": pedido_id,
        "cliente": dados["cliente"],
        "email": dados["email"],
        "produto": dados["produto"],
        "quantidade": quantidade,
        "valorUnitario": valor_unitario,
        "valorTotal":
            quantidade * valor_unitario,
        "status":
            dados.get(
                "status",
                existente["status"]
            ),
        "criadoEm":
            existente["criadoEm"],
        "atualizadoEm":
            agora_iso()
    }

    table.put_item(Item=item)

    return resposta(
        200,
        {
            "mensagem":
                "Pedido atualizado com sucesso",
            "pedido": item
        }
    )


def atualizar_status(event, pedido_id):

    resultado = table.get_item(
        Key={"id": pedido_id}
    )

    pedido = resultado.get("Item")

    if not pedido:
        return resposta(
            404,
            {
                "erro":
                    "Pedido não encontrado"
            }
        )

    try:
        dados = corpo_json(event)
    except Exception:
        return resposta(
            400,
            {"erro": "JSON inválido"}
        )

    novo_status = dados.get("status")

    if novo_status not in STATUS_VALIDOS:
        return resposta(
            400,
            {"erro": "Status inválido"}
        )

    pedido["status"] = novo_status
    pedido["atualizadoEm"] = agora_iso()

    table.put_item(Item=pedido)

    return resposta(
        200,
        {
            "mensagem":
                "Status atualizado",
            "pedido": pedido
        }
    )


def cancelar_pedido(pedido_id):

    resultado = table.get_item(
        Key={"id": pedido_id}
    )

    pedido = resultado.get("Item")

    if not pedido:
        return resposta(
            404,
            {
                "erro":
                    "Pedido não encontrado"
            }
        )

    pedido["status"] = "cancelado"
    pedido["atualizadoEm"] = agora_iso()

    table.put_item(Item=pedido)

    return resposta(
        200,
        {
            "mensagem":
                "Pedido cancelado",
            "pedido": pedido
        }
    )


def lambda_handler(event, context):

    method, partes = (
        obter_metodo_e_caminho(event)
    )

    print(
        json.dumps(
            event,
            default=str
        )
    )

    if method == "OPTIONS":
        return resposta(
            200,
            {"mensagem": "CORS OK"}
        )

    if (
        len(partes) == 1
        and partes[0] == "pedidos"
    ):

        if method == "POST":
            return criar_pedido(event)

        if method == "GET":
            return listar_pedidos()

    if (
        len(partes) == 2
        and partes[0] == "pedidos"
    ):

        pedido_id = partes[1]

        if method == "GET":
            return buscar_pedido(
                pedido_id
            )

        if method == "PUT":
            return atualizar_pedido(
                event,
                pedido_id
            )

        if method == "DELETE":
            return cancelar_pedido(
                pedido_id
            )

    if (
        len(partes) == 3
        and partes[0] == "pedidos"
        and partes[2] == "status"
    ):

        pedido_id = partes[1]

        if method == "PATCH":
            return atualizar_status(
                event,
                pedido_id
            )

    return resposta(
        404,
        {
            "erro":
                "Rota não encontrada",
            "metodo": method,
            "caminho":
                "/" + "/".join(partes)
        }
    )

