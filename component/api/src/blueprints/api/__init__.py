# standard library
import os
import http
from pathlib import Path

# external library
from flask import Blueprint, jsonify, request

# project library
import common.constants as constants

from . import api_helper

api = Blueprint('api', __name__, url_prefix="/api")

master_address = os.environ.get("MASTERSERVER_ADDR", default="master")

@api.route("/tts", methods=["POST"])
def tts():
    # init
    input_path_obj = Path.cwd() / "data/input"
    match_dict = {
        "text": "string"
    }

    # save file
    file_list = request.files.getlist('files')

    if len(file_list) == 0:
        return jsonify(api_helper.generate_err_json("no files"))

    file_obj = file_list[0] # only 1
    file_name = file_obj.filename
    file_path_obj = input_path_obj / file_name
    file_obj.save(str(file_path_obj))

    # create input message
    parsed_message = api_helper.parse_form(request, match_dict)
    if parsed_message["status"] == constants.Status.ERROR:
        return jsonify(parsed_message), http.HTTPStatus.BAD_REQUEST.value

    parsed_message["data"] = {file_name: api_helper.base64_encode(file_path_obj)}

    # send to message
    result_dict = api_helper.submit_job(master_address, parsed_message)

    return jsonify(result_dict)