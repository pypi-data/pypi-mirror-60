# Copyright (c) 2014-2020 GeoSpock Ltd.

import http.client
import json
import os
from pathlib import Path
from time import time, sleep

import click
from pkg_resources import resource_string
from urllib.parse import urlparse

geospock_dir = Path.home().joinpath(".geospock")
geospock_file = geospock_dir.joinpath("credentials")
config_file = geospock_dir.joinpath("config.json")
messages = json.loads(resource_string('geospock_cli', "messages.json").decode("utf-8"))


def write_to_config(clientid, audience, auth0url, request_address, profile="default"):
    if not os.path.exists(geospock_dir):
        os.mkdir(geospock_dir)

    if os.path.exists(config_file):
        with open(config_file) as json_file:
            current_config = json.load(json_file)
            if profile in current_config:
                if current_config[profile]["client_id"] == clientid and \
                        current_config[profile]["audience"] == audience and \
                        current_config[profile]["auth0_url"] == auth0url and \
                        current_config[profile]["request_address"] == request_address:
                    click.echo("No change to configuration")
                else:
                    click.echo("Change in configuration - please rerun 'geospock get-credentials' for this profile")
                    with open(geospock_file, "w+") as current_geospock_file:
                        credentials = json.load(current_geospock_file)
                        credentials.pop(profile, None)
                        current_geospock_file.write(credentials)
    else:
        current_config = dict()

    current_config[profile] = dict(client_id=clientid, audience=audience, auth0_url=auth0url,
                                   request_address=request_address)

    with open(config_file, "w") as config_file_write:
        config_file_write.write(json.dumps(current_config, indent=4))


def parse_and_make_request(url: str, method: str, body:str, headers):
    parsed_url = urlparse(url)
    response = make_request(parsed_url.netloc, parsed_url.path, method, body, headers, parsed_url.scheme == "https")
    return response


def make_request(endpoint: str, path: str, method: str, body: str, headers, ssl=True):
    if ssl:
        conn = http.client.HTTPSConnection(endpoint)
    else:
        conn = http.client.HTTPConnection(endpoint)
    conn.request(method, path, body, headers)
    response = conn.getresponse().read().decode()

    return response


def get_device_code(config, profile):
    headers = {"content-type": "application/json"}
    body = {
        "client_id": config[profile]["client_id"],
        "scope": "offline_access",
        "audience": config[profile]["audience"]
    }

    res = make_request(config[profile]["auth0_url"], "/oauth/device/code", "POST", json.dumps(body), headers)
    return json.loads(res)


def get_token(device_code: str, config, profile):
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "client_id": config[profile]["client_id"]
    }

    res = make_request(config[profile]["auth0_url"], "/oauth/token", "POST", json.dumps(body), headers)
    return json.loads(res)


def show_verification_uri_message(device_code_response):
    click.echo(messages["verificationInstruction"])
    click.secho(device_code_response["verification_uri_complete"] + "\n", fg="green")


def poll_token(device_code_response, config, profile):
    device_code = device_code_response["device_code"]
    interval = device_code_response["interval"]
    expires_in = device_code_response["expires_in"]

    start_time = time()

    try:
        # Repeatedly try to use our temporary device code to get an auth token until the device code expires
        while int(time() - start_time) < expires_in:
            sleep(interval)
            token_response = get_token(device_code, config, profile)
            if "error" in token_response and token_response["error"] == "authorization_pending":
                # Device code is still valid but user has not yet logged in with their GeoSpock username/password
                click.echo(token_response["error_description"])
                show_verification_uri_message(device_code_response)
            elif "error" in token_response:
                exit(click.secho(token_response["error_description"], fg="red"))
            else:
                # User has logged in and we have got a valid response
                return token_response
    except Exception as e:
        # If we cannot poll for our auth token (e.g. auth server is offline) then report this to the user
        # More user-focused? messages.json?
        exit(click.secho(messages["pollingError"].format(e), fg="red"))

    return None


def save_tokens(tokens, profile="default", refresh_token=None):
    if tokens is None:
        click.secho("Failed to authenticate", fg="red")
        return

    if not os.path.exists(geospock_dir):
        exit(click.secho(messages["credentialsDirectory"], fg="red"))

    tokens["creation_time"] = int(time())
    if refresh_token is not None:
        tokens["refresh_token"] = refresh_token

    if os.path.exists(geospock_file) and os.path.getsize(geospock_file) > 0:
        with open(geospock_file) as json_file:
            current_geospock_file = json.load(json_file)
    else:
        current_geospock_file = dict()
    current_geospock_file[profile] = tokens
    with open(geospock_file, "w+") as output_file:
        output_file.write(json.dumps(current_geospock_file, indent=4))


def init_credentials(config, profile):
    # First get a temporary device code and show the verification url to the user
    device_code_response = get_device_code(config, profile)
    show_verification_uri_message(device_code_response)

    # Wait for the user to complete the verification using their GeoSpock credentials, and then save the auth tokens
    token_response = poll_token(device_code_response, config, profile)
    save_tokens(token_response, profile)
    return token_response


def refresh_token(refresh_token: str, config, profile):
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "refresh_token",
        "client_id": config[profile]["client_id"],
        "refresh_token": refresh_token,
    }

    res = make_request(config[profile]["auth0_url"], "/oauth/token", "POST", json.dumps(body), headers)
    return json.loads(res)


def renew_credentials(config, profile):
    # 10s leeway added to prevent using token after expiry time by requesting it just before
    leeway = 10

    with open(geospock_file) as json_file:
        tokens = json.load(json_file)[profile]

    if "creation_time" in tokens and "expires_in" in tokens and "access_token" in tokens:
        if int(time() - tokens["creation_time"] + leeway) > tokens["expires_in"]:
            try:
                token_response = refresh_token(tokens["refresh_token"], config, profile)
                save_tokens(token_response, profile, tokens["refresh_token"])
                return token_response
            except Exception as e:
                click.echo("Exception: {}".format(e))
                return None

        else:
            return tokens
    else:
        try:
            token_response = refresh_token(tokens["refresh_token"])
            save_tokens(token_response, tokens["refresh_token"])
            return token_response
        except:
            return None


def get_config():
    if os.path.exists(config_file):
        with open(config_file) as json_file:
            config = json.load(json_file)
        return config
    else:
        click.echo("Error opening config file")
        return None


def get_credentials_from_file(config, profile):
    if not config:
        return None
    elif os.path.exists(geospock_file) and os.path.getsize(geospock_file) > 0:
        with open(geospock_file) as file:
            credentials = json.load(file)
            if profile in credentials:
                return renew_credentials(config, profile)
        return init_credentials(config, profile)
    else:
        return init_credentials(config, profile)
