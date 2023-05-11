# create a flask app with hello world route
from flask import Flask, request
app = Flask(__name__)
import subprocess
import os
import json

IN_GDAL_DOCKER = os.environ.get('IN_GDAL_DOCKER', False)
command = """docker run --rm osgeo/gdal:ubuntu-full-latest gdalinfo -json """
if IN_GDAL_DOCKER:
    command = """gdalinfo -json """

@app.route('/', methods=['POST'])
def get_info():
    # if /stac-item path exists on system, take the file from there
    # otherwise, take the file from the request body
    filePathFromRequest = request.json['file_url']
    filePath = None
    if os.path.exists('/stac-items'):
        filePath = '/stac-items/' + filePathFromRequest.split("/")[-1]
    else:
        filePath = filePathFromRequest

    # call the gdalinfo command with the filePath
    try:
        full_command = command + filePath
        print(full_command)
        result = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        error = result.stderr.decode('utf-8')
        if error:
            if "ERROR 1" in error:
                return json.dumps({"error": "File not found"}), 404
            else:
                return json.dumps({"error": error}), 400
        # TODO: urls might need to be re-written to include the original filePathFromRequest ?
        return json.loads(result.stdout.decode('utf-8'))
    except json.decoder.JSONDecodeError as e:
        return {'error': "File you are pointing to might not exist or is not a valid file."}, 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7002)
