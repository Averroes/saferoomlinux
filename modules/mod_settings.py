from flask import Blueprint, jsonify,abort,request,render_template
import getpass
import safeglobals
from libs.functions import encryptString, decryptString,convert_size,get_folder_size,handle_exception,send_response,clear_cache,log_message
import os
from libs.ConfigManager import get_services,get_default_values,save
from libs.PasswordManager import save_password, get_master_password


# Initializing the blueprint
mod_settings = Blueprint("mod_settings",__name__)


# Routes
@mod_settings.route("/",methods=['GET'])
def show_page():
    return render_template("settings.html",title="Settings")

@mod_settings.route("/services",methods=["GET"])
def get_available_services():
    
    response = {}
    # Getting a list of services
    response['services'] = get_services()
    
    # Checking the master password
    response['master'] = (get_master_password() != "")
    return jsonify(response);


@mod_settings.route("/config",methods=["GET"])
def get_config():
    try:
        response = get_default_values()
        return jsonify(response);
    except Exception as e:
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_internal_server,str(e))

@mod_settings.route("/save",methods=["POST"])
def save_config():

    # Getting JSON from request
    data = request.get_json()
    if not data:
        abort(safeglobals.http_bad_request,{"message":safeglobals.MSG_MANDATORY_MISSING})
    
    # Saving configuration
    save(data)

    # If user sends the password, generate the master password file
    if "password" in data:
        if data['password'] != "":
            save_password(data['password'])

    return jsonify(status=safeglobals.http_ok,message=safeglobals.MSG_CONFIG_OK)



@mod_settings.route("/cache",methods=["GET"])
def cache_status():
    notebook_total = 0
    evernote_notebooks = 0
    onenote_notebooks = 0
    response = {}
	
	# Calculating the size of "notebooks.json" file in Kb
    if os.path.exists(safeglobals.path_notebooks_evernote) == False:
        evernote_notebooks = 0;
    else:
		evernote_notebooks = os.path.getsize(safeglobals.path_notebooks_evernote)

    if os.path.exists(safeglobals.path_notebooks_onenote) == False:
	    onenote_notebooks = 0
    else:
	    onenote_notebooks = os.path.getsize(safeglobals.path_notebooks_onenote)

    notebook_total = evernote_notebooks + onenote_notebooks
    response['notebooks'] =  str(convert_size(notebook_total))

    # Calculating the "tags.json"
    size = 0
    if os.path.exists(safeglobals.path_tags) == True:
    	size = os.path.getsize(safeglobals.path_tags)
    response['tags'] = convert_size(size)

    # Calculating "searches.json" size
    size = 0
    if os.path.exists(safeglobals.path_searches) == True:
    	size = os.path.getsize(safeglobals.path_searches)
    response['searches'] = convert_size(size)

    # Calculating "sections.json" size
    size = 0
    files = os.listdir(safeglobals.path_cache)
    for file in files:
    	if "section" in file:
    		size = size + os.path.getsize(safeglobals.path_cache+file)

    response['sections'] = convert_size(size)

    # Calculating the size of notes cache
    size = 0
    files = os.listdir(safeglobals.path_cache)
    for file in files:
    	if "notes_" in file:
    		size = size + os.path.getsize(safeglobals.path_cache+file)
    response['notes'] = convert_size(size)

    # Calculating the size of TMP folder
    size = 0
    if os.path.exists(safeglobals.path_tmp) == True:
    	size = get_folder_size(safeglobals.path_tmp)

    response['tmp'] = convert_size(size)

    return jsonify(response)


@mod_settings.route("/clear",methods=["POST"])
def clear_data_cache():

    # Checking type
    data = request.get_json()
    if not data:
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_bad_request,safeglobals.MSG_MANDATORY_MISSING)
    # Clearing caches
    if clear_cache(data) == True:
        return jsonify(status=safeglobals.http_ok,message="")
    else:
        return handle_exception(safeglobals.TYPE_JSON,safeglobals.http_internal_server,safeglobals.MSG_INTERNAL_ERROR)