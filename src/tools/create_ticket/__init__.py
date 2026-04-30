"""Azure Function: create_ticket."""
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    # TODO: Implement
    return func.HttpResponse(json.dumps({"status": "not implemented"}), status_code=501)
