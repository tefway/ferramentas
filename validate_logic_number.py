import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def handle_data(data):
    '''
    Processa os dados recebidos pelo JSON e trata inconsistências.

    Args:
        data (dict): Dados recebidos pela requisição JSON contendo "adquirente", "logico" e "codigo".

    Returns:
        tuple: (adquirence_lower, logic_number, code) se todos os dados forem válidos.
        Response: Resposta JSON com mensagem de erro e código de status HTTP, se houver erro nos dados.
    '''
    adquirence = data.get("adquirente")
    logic_number = data.get("logico")
    code = data.get("codigo")
    
    if not adquirence:
        return jsonify({"Error": "invalid adquirence"}), 400
    elif not logic_number:
        return jsonify({"Error": "invalid logic number"}), 400
    elif not code:
        return jsonify({"Error": "invalid code number"}), 400
    
    adquirence_lower = adquirence.lower()
    valid_adquirences = {"bin", "getnetlac", "safra", "sipag", "stone", "vero", "adiq", "bigcard", "biz", 
                         "brasil card", "cabal", "cardse", "carto", "comprocard", "convcard", "credishop", 
                         "ctf frota", "fitcard", "globalpayments", "marketpay", "mettacard", "orgcard", 
                         "portalcard", "rede", "resomaq", "softnex", "telenet", "valecard", "valeshop", "cielo"}
    
    if adquirence_lower in valid_adquirences:
        return adquirence_lower, logic_number, code
    else:
        return jsonify({"Error": "unsupported adquirence type"}), 400


def process_data(adquirence, logic_number):
    """
    Processa o número lógico baseado no tipo de adquirente.

    Args:
        adquirence (str): O tipo de adquirente, representado por uma string.
        logic_number (str): O número lógico que precisa ser processado.

    Returns:
        str: O número lógico processado. 
        Se o adquirente for um dos seguintes: "bin", "fitcard", "getnetlac", "policard", "safra", "sipag", "siscred", "softnex", ou "valeshop", 
        o número lógico será preenchido com zeros à esquerda até ter 15 dígitos. Caso contrário, o número lógico será retornado como está.
    """
    match adquirence:
        case "bin" | "fitcard" | "getnetlac" | "policard" | "safra" | "sipag" | "siscred" | "softnex" | "valeshop":
            return logic_number.zfill(15)
        case _: 
            return logic_number


@app.route('/validate-logic-number', methods=['POST'])
def validate_logic_number():
    """
    Valida o número lógico e o código baseado no tipo de adquirente recebido via requisição HTTP POST.

    A função extrai dados JSON da requisição recebida, processa o número lógico com base no tipo de adquirente,
    e valida os campos de acordo com as regras específicas para cada tipo de adquirente.

    Requisição esperada:
        - JSON com as chaves "adquirente", "logico" e "codigo".

    Returns:
        Response: Um objeto de resposta Flask contendo:
            - JSON com a mensagem de sucesso ou erro.
            - Código de status HTTP:
                - 200 para sucesso.
                - 400 para erros de validação ou tipos de adquirente não suportados.
    """
    data = request.json
    
    result = handle_data(data)
    if isinstance(result, tuple):
        adquirence, logic_number, code = result
    else:
        return result

    logic_number = process_data(adquirence, logic_number)
    
    match adquirence:
        case "adiq" | "bigcard" | "biz" | "brasil card" | "cabal" | "cardse" | "carto" | "comprocard" | "convcard" | "credishop" | "ctf frota" | "fitcard" | "globalpayments" | "marketpay" | "mettacard" | "orgcard" | "portalcard" | "rede" | "resomaq" | "softnex" | "telenet" | "valecard" | "valeshop":
            if re.match(r"^\d{15}$", logic_number):
                return jsonify({"Success": f"{adquirence} processed with logic number {logic_number}"}), 200

        case "bin" | "getnetlac" | "safra" | "sipag":
            if re.match(r"^\d{15}$", logic_number) and re.match(r"^TF[a-zA-Z0-9]{8}$", code):
                return jsonify({"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}), 200

        case "cielo":
            if re.match(r"^4\d{8}$", logic_number):
                return jsonify({"Success": f"{adquirence} processed with logic number {logic_number}"}), 200
            else:
                return jsonify({"Error": "Logic number does not match the param"}), 400

        case "stone":
            if re.match(r"^[a-zA-Z0-9]{32}$", logic_number) and re.match(r"^\d{9}$", code):
                return jsonify({"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}), 200

        case "vero" | "josias":
            return jsonify({"Info": f"{adquirence} is not yet supported"}), 200

        case _:
            return jsonify({"Error": "Unsupported adquirence type"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=10000)
