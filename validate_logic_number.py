import re
import json

class ErrInvalidParam(Exception):
    def __init__(self, value=None, msg=None) -> None:
        if not msg:
            msg = f"Invalid parameter found, please validate.\nValue: {value}"
        super().__init__(msg)

def handle_data(data) -> any:
    '''
    Processa os dados recebidos pelo JSON e trata inconsistências.

    Args:
        data (dict): Dados recebidos pela requisição JSON contendo "adquirente", "logico" e "codigo".

    Returns:
        tuple: (adquirence_lower, logic_number, code) se todos os dados forem válidos.
        str: Mensagem de erro se houver erro nos dados.
    '''
    try:
        adquirence = data.get("adquirente")
        logic_number = data.get("logico")
        code = data.get("codigo")
        
        if not adquirence:
            raise ErrInvalidParam(adquirence, "Authorizer not provided.")
        elif not logic_number:
            raise ErrInvalidParam(logic_number, "Logical number not provided.")
        elif not code:
            raise ErrInvalidParam(code, "Code not provided")

    except ErrInvalidParam as e:
        return str(e)

    adquirence_lower = adquirence.lower()
    valid_adquirences = {
        "bin", "getnetlac", "safra", "sipag", "stone", "vero", "adiq", "bigcard", "biz", 
        "brasil card", "cabal", "cardse", "carto", "comprocard", "convcard", "credishop", 
        "ctf frota", "fitcard", "globalpayments", "marketpay", "mettacard", "orgcard", 
        "portalcard", "rede", "resomaq", "softnex", "telenet", "valecard", "valeshop", "cielo"
    }
    
    if adquirence_lower in valid_adquirences:
        return adquirence_lower, logic_number, code
    else:
        return "unsupported adquirence type"

def process_data(adquirence, logic_number) -> str:
    """
    Processa o número lógico baseado no tipo de adquirente.

    Args:
        adquirence (str): O tipo de adquirente, representado por uma string.
        logic_number (str): O número lógico que precisa ser processado.

    Returns:
        str: O número lógico processado. 
    """
    match adquirence:
        case "bin" | "fitcard" | "getnetlac" | "policard" | "safra" | "sipag" | "siscred" | "softnex" | "valeshop":
            return logic_number.zfill(15)
        case _: 
            return logic_number

def validate_logic_number(data) -> dict:
    """
    Valida o número lógico e o código baseado no tipo de adquirente recebido via requisição HTTP POST.

    Requisição esperada:
        - JSON com as chaves "adquirente", "logico" e "codigo".

    Returns:
        dict: JSON com a mensagem de sucesso ou erro
    """
    try:
        if not isinstance(data, dict):
            raise TypeError("The argument must be a JSON dictionary.")
        
        result = handle_data(data)
        if isinstance(result, tuple):
            adquirence, logic_number, code = result
        else:
            return {"Error": result}

        logic_number = process_data(adquirence, logic_number)
        
        match adquirence:
            case "adiq" | "bigcard" | "biz" | "brasil card" | "cabal" | "cardse" | "carto" | "comprocard" | "convcard" | "credishop" | "ctf frota" | "fitcard" | "globalpayments" | "marketpay" | "mettacard" | "orgcard" | "portalcard" | "rede" | "resomaq" | "softnex" | "telenet" | "valecard" | "valeshop":
                if re.match(r"^\d{15}$", logic_number):
                    return {"Success": f"{adquirence} processed with logic number {logic_number}"}

            case "bin" | "getnetlac" | "safra" | "sipag":
                if re.match(r"^\d{15}$", logic_number) and re.match(r"^TF[a-zA-Z0-9]{8}$", code):
                    return {"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}

            case "cielo":
                if re.match(r"^4\d{8}$", logic_number):
                    return {"Success": f"{adquirence} processed with logic number {logic_number}"}
                else:
                    return {"Error": "Logic number does not match the param"}

            case "stone":
                if re.match(r"^[a-zA-Z0-9]{32}$", logic_number) and re.match(r"^\d{9}$", code):
                    return {"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}

            case "vero" | "josias":
                return {"Info": f"{adquirence} is not yet supported"}

            case _:
                return {"Error": "Unsupported adquirence type"}
    except TypeError as e:
        return {"Error": f"Invalide param: {e}"}
    except Exception as e:
        return {"Error": f"Generic error: {e}"}

if __name__ == "__main__":
    # Exemplo de uso
    test_data = {
        "adquirente": "bin",
        "logico": "123456",
        "codigo": "TF12345678"
    }
    print(validate_logic_number(test_data))
