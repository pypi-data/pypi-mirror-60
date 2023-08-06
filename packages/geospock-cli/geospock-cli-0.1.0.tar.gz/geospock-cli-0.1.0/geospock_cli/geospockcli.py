# Copyright (c) 2014-2020 GeoSpock Ltd.

import click
import json

from geospock_cli.auth import *
from pkg_resources import resource_string

messages = json.loads(resource_string('geospock_cli', "messages.json").decode("utf-8"))


def get_header(profile):
    config = get_config()
    if profile not in config:
        click.echo(messages["profileError"].format(profile))
        return None, None
    request_address = config[profile]["request_address"]
    credentials = get_credentials_from_file(config, profile)

    if credentials:
        headers = {"content-type": "application/json", "authorization": "Bearer " + credentials["access_token"]}
        return headers, request_address
    else:
        return None, None


def display_result(result, output_object):
    try:
        if output_object:
            click.echo(json.dumps(result["data"][output_object], indent=4))
        else:
            click.echo(json.dumps(result["data"], indent=4))
    except Exception as e:
        click.echo(messages["graphQLError"] + str(result))
        click.echo(e)


def process_request(request, profile="default", output_object=None):
    header, request_address = get_header(profile)

    if header:
        try:
            response = parse_and_make_request(request_address, "POST", json.dumps(request), header)
            response_json = json.loads(response)
            if "errors" in response_json:
                click.echo(json.dumps(response_json["errors"], indent=4))
                click.echo("The following data was returned in addition to the error messages above: ", nl=False)
                display_result(response_json, output_object)
            else:
                display_result(response_json, output_object)

        except ConnectionRefusedError as e:
            exit(click.echo("Connection refused"))
        except Exception as e:
            exit(click.echo(e))
    else:
        click.echo(messages["noHeader"])


def init(clientid, audience, auth0url, request_address, profile):
    write_to_config(clientid, audience, auth0url, request_address, profile)


@click.command(help=messages["helpRun"], context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
@click.argument('command')
@click.option('--profile', default="default")
def run(ctx, command, profile):
    if command == "help" and len(ctx.args) == 0:
        help_all(profile)
    elif command == "help":
        help_command(profile, ctx.args[0])

    # We want the number of additional arguments to be even (i.e. number % 2 == 0) so that every {--argumentName}
    # corresponds to an {argumentValue}
    elif len(ctx.args) % 2 != 0:
        click.echo(messages["argNumberWrong"])
    else:
        args = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}
        if command == "init":
            # Saving info to config.json
            try:
                init(args["clientid"], args["audience"], args["auth0url"], args["request-address"], profile)
            except KeyError:
                click.echo(messages["helpInit"])
        elif command == "get-credentials":
            # Add to credentials file
            if get_header(profile):
                click.secho("Credentials saved", fg="green")
        else:
            run_command(command, profile, args)


def run_command(command, profile, args):
    # Where we have an argument ending in the following, read from a file rather than taking the direct string
    file_indicator = ".json"
    response_json = get_command_from_server(profile, command)
    if response_json is None:
        click.echo("Could not get command {} from service".format(command))
    elif "responseTemplate" in response_json:
        graphql = response_json["responseTemplate"]
        internal_name = response_json["internalName"]
        parameters = response_json["parameters"]
        new_args = dict()
        arg_missing = False
        for parameter in parameters:
            if (parameter["name"] in args and parameter["type"] in ["String", "Int", "ID", "Boolean"] and
                    not parameter["fromFile"]):
                new_args[parameter["internalName"]] = args[parameter["name"]]
            elif parameter["name"] in args and parameter["type"] == "enum":
                if args[parameter["name"]] in parameter["enumValues"]:
                    new_args[parameter["internalName"]] = args[parameter["name"]]
                else:
                    arg_missing = True
                    click.echo("Value {0} not allowed for argument --{1}. Allowed values: {2}".format(args[parameter["name"]], parameter["name"], parameter["enumValues"]))
            elif parameter["name"] in args \
                    and args[parameter["name"]][-len(file_indicator):] == file_indicator \
                    and parameter["fromFile"] \
                    and parameter["type"] == "String":
                with open(args[parameter["name"]], "r") as input_file:
                    new_args[parameter["internalName"]] = json.dumps(json.load(input_file))
            elif parameter["name"] in args \
                    and args[parameter["name"]][-len(file_indicator):] == file_indicator \
                    and parameter["fromFile"]:
                with open(args[parameter["name"]], "r") as input_file:
                    new_args[parameter["internalName"]] = json.load(input_file)
            elif "default" in parameter:
                new_args[parameter["internalName"]] = parameter["default"]
            elif len(parameter["subParams"]) == 0 and parameter["required"]:
                click.echo("Required argument --{0} not provided for command {1}".format(parameter["name"], command))
                arg_missing = True
            elif len(parameter["subParams"]) > 0:
                input_dict = dict()
                for sub_param in parameter["subParams"]:
                    if sub_param["name"] in args and sub_param["type"] in ["String", "Int", "ID", "Boolean"]:
                        input_dict[sub_param["internalName"]] = args[sub_param["name"]]
                    elif sub_param["name"] in args and sub_param["type"] == "enum":
                        if args[sub_param["name"]] in sub_param["enumValues"]:
                            input_dict[sub_param["internalName"]] = args[sub_param["name"]]
                        else:
                            arg_missing = True
                            click.echo("Value {0} not allowed for argument --{1}. Allowed values: {2}".format(
                                args[sub_param["name"]], sub_param["name"], sub_param["enumValues"]))
                    elif sub_param["name"] in args \
                            and args[sub_param["name"]][-len(file_indicator):] == file_indicator \
                            and sub_param["fromFile"] \
                            and sub_param["type"] == "String":
                        with open(args[sub_param["name"]], "r") as input_file:
                            input_dict[sub_param["internalName"]] = json.dumps(json.load(input_file))
                    elif sub_param["name"] in args \
                            and args[sub_param["name"]][-len(file_indicator):] == file_indicator \
                            and sub_param["fromFile"]:
                        with open(args[sub_param["name"]], "r") as input_file:
                            input_dict[sub_param["internalName"]] = json.load(input_file)
                    elif "default" in sub_param:
                        input_dict[sub_param["internalName"]] = sub_param["default"]
                        # Add in sub_params from file
                    elif sub_param["required"]:
                        click.echo("Required argument --{0} not provided for command {1}".format(sub_param["name"],
                                                                                                 command))
                        arg_missing = True
                new_args[parameter["internalName"]] = input_dict
        if not arg_missing:
            request = {"operationName": internal_name, "query": graphql, "variables": new_args}
            process_request(request, profile, internal_name)
    else:
        click.echo("Query not found")


def help_all(profile):
    commands_json = get_commands_from_server(profile)
    max_len = max([len(key) for key in commands_json])
    click.echo(messages["helpAllCommands"])
    for command in commands_json:
        arg_list = []
        for arg in commands_json[command]["parameters"]:
            if arg["fromFile"] or len(arg["subParams"]) == 0:
                arg_list.append("--" + arg["name"])
            else:
                for sub_arg in arg["subParams"]:
                    arg_list.append("--" + sub_arg["name"])
        if len(arg_list) == 0:
            click.echo("{value:>{width}}".format(value=command, width=max_len))
        else:
            click.echo("{value:>{width}}".format(value=command, width=max_len) + " " +
                       str(arg_list).replace("'", "").replace("[", "").replace("]", "").replace(",", ""))


def help_command(profile, command):
    command_json = get_command_from_server(profile, command)
    if command_json:
        click.echo("Usage: geospock {0} ARGUMENTS".format(command))
        click.echo(messages["requiredArguments"])
        if len(command_json["parameters"]) == 0:
            click.echo(messages["noArgsNeeded"])
        for arg in command_json["parameters"]:
            if arg["fromFile"] or len(arg["subParams"]) == 0:
                click.echo("\t--" + arg["name"] + ": " + arg["type"] + ("!" if arg["required"] else "")
                           + (" (default: " + str(arg["default"]) + ")" if "default" in arg else "")
                           + (" " + str(arg["enumValues"]) if arg["type"] == "enum" else ""))
            else:
                for sub_arg in arg["subParams"]:
                    click.echo("\t--" + sub_arg["name"] + ": " + sub_arg["type"] + ("!" if sub_arg["required"] else "")
                               + (" (default: " + str(sub_arg["default"]) + ")" if "default" in sub_arg else "")
                               + (" " + str(sub_arg["enumValues"]) if sub_arg["type"] == "enum" else ""))
    else:
        click.echo("Command {} not recognised.".format(command))


def get_commands_from_server(profile):
    graphql = resource_string('geospock_cli', "graphql_templates/getCommands.graphql").decode("utf-8")
    request = {"operationName": "getCliCommands", "query": graphql, "variables": {}}
    header, request_address = get_header(profile)

    if header:
        try:
            response = parse_and_make_request(request_address, "POST", json.dumps(request), header)
            response_json = json.loads(response)
            if "errors" in response_json:
                click.echo(json.dumps(response_json["errors"], indent=4))
                try:
                    display_result(response_json, None)
                except Exception as e:
                    click.echo(e)
            else:
                return json.loads(response_json["data"]["getCliCommands"])
        except ConnectionRefusedError as e:
            exit(click.echo("Connection refused"))
        except Exception as e:
            exit(click.echo(e))
    else:
        click.echo(messages["noHeader"])
    return None


def get_command_from_server(profile, command):
    graphql = resource_string('geospock_cli', "graphql_templates/getCommand.graphql").decode("utf-8")
    request = {"operationName": "getCliCommand", "query": graphql, "variables": {"commandName": command}}
    header, request_address = get_header(profile)

    if header:
        try:
            response = parse_and_make_request(request_address, "POST", json.dumps(request), header)
            response_json = json.loads(response)
            if "errors" in response_json:
                click.echo(json.dumps(response_json["errors"], indent=4))
                try:
                    display_result(response_json, None)
                except Exception as e:
                    click.echo(e)
            else:
                return json.loads(response_json["data"]["getCliCommand"])
        except ConnectionRefusedError as e:
            exit(click.echo("Connection refused"))
        except Exception as e:
            exit(click.echo(e))
    else:
        click.echo(messages["noHeader"])
    return None


if __name__ == '__main__':
    run()
