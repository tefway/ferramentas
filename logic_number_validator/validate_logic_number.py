import re
import json

class ErrInvalidParam(Exception):
    """Custom exception class for invalid parameter handling.
    
    Attributes:
        value (any): The invalid parameter that caused the exception.
        msg (str): A message describing the error.
    """
    def __init__(self, value=None, msg=None) -> None:
        if not msg:
            msg = f"Invalid parameter found, please validate.\nValue: {value}"
        super().__init__(msg)

def handle_data(data) -> any:
    """Handles and validates the input data, raising an error if required fields are missing.

    Args:
        data (dict): A dictionary containing 'adquirente', 'logico', and 'codigo' keys.

    Returns:
        tuple: A tuple containing 'adquirente', 'logico', and 'codigo' if all are valid.
        str: Error message if validation fails.

    Raises:
        ErrInvalidParam: If any required parameter ('adquirente', 'logico', or 'codigo') is missing.
    """    
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
    """Processes the logic number based on the adquirence rules.

    Args:
        adquirence (str): The name of the adquirence.
        logic_number (str): The logical number provided for the adquirence.

    Returns:
        str: Processed logical number, potentially zero-padded for some adquirences.
    """
    match adquirence:
        case "bin" | "fitcard" | "getnetlac" | "policard" | "safra" | "sipag" | "siscred" | "softnex" | "valeshop":
            return logic_number.zfill(15)
        case _: 
            return logic_number

def validate_logic_number(data) -> dict:
    """Validates the logical number and code for a given adquirence, ensuring they match specific patterns.

    Args:
        data (dict): A dictionary containing 'adquirente', 'logico', and 'codigo' keys.

    Returns:
        dict: A dictionary containing success or failure messages based on the validation.
        The returned dictionary may have:
            - "Success" if the validation passes.
            - "Failure" if the data doesn't match the expected pattern.
            - "Error" for unsupported adquirences or invalid input data.
    
    Raises:
        TypeError: If the input data is not a dictionary.
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
                else:
                    return {"Failure":f"{adquirence.upper()} does not match with the pattern"}

            case "cielo":
                if re.match(r"^4\d{7}$", logic_number):
                    return {"Success": f"{adquirence} processed with logic number {logic_number}"}
                else:
                    return {"Failure":f"{adquirence.upper()} does not match with the pattern"}

            case "stone":
                if re.match(r"^[a-zA-Z0-9]{32}$", logic_number) and re.match(r"^\d{9}$", code):
                    return {"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}
                else:
                    return {"Failure":f"{adquirence.upper()} does not match with the pattern"}

            case "vero":
                if re.match(r"^04\d{13}$", logic_number) and re.match(r"^\d{11}$", code):
                    return {"Success": f"{adquirence} processed with logic number {logic_number} and code {code}"}
                else:
                    return {"Failure":f"{adquirence.upper()} does not match with the pattern"}
                
            case _:
                return {"Error": "Unsupported adquirence type"}
    except TypeError as e:
        return {"Error": f"Invalide param: {e}"}
    except Exception as e:
        return {"Error": f"Generic error: {e}"}

if __name__ == "__main__":
    test_data = {
        "adquirente": "vero",
        "logico": "041135700123300",
        "codigo": "00411357000"
    }
    print(validate_logic_number(test_data))
