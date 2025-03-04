
# Permet de créer le dictionnaire plus facilement
# HasError: si le dictionnaire contient une erreur ou pas
# Result: le retour de la fonction initial
# Code: le code HTTP de la req
# Error: par défaut à none, le dictionnaire de l'erreur à renvoyer
def resDict(result, code, hasError=False, error=None):
    return {
        "hasError": hasError,
        "result": result,
        "code": code,
        "error": error
    }