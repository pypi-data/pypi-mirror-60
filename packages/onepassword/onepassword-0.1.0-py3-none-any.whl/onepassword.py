import json
import os
import subprocess
from uuid import uuid4


class DeletionFailure(Exception):
    def __init__(self, item_name, vault):
        message = f"Unable to delete item '{item_name}' from vault '{vault}'"

        super().__init__(message)
        self.message = message


class Unauthorized(Exception):
    pass


class MissingCredentials(Exception):
    pass


class SigninFailure(Exception):
    pass


class UnknownResource(Exception):
    pass


class UnknownResourceItem(Exception):
    pass


class UnknownError(Exception):
    pass


class OnePassword(object):

    def __init__(self, secret=None, token=None, uuid=None):
        if secret is not None:
            self.uuid = str(uuid4())
            self.session_token = _get_access_token(secret, shorthand=self.uuid)
        elif token is not None and uuid is not None:
            self.uuid = uuid
            self.session_token = token
        else:
            raise MissingCredentials()

    def list(self, resource):
        op_command = f"op list {resource} --session={self.session_token}"
        try:
            return json.loads(run_op_command_in_shell(op_command))
        except json.decoder.JSONDecodeError:
            raise UnknownResource(resource)

    def create_document_in_vault(self, filename, title, vault):
        op_command = f"op create document {filename} --title='{title}' --vault='{vault}' --session={self.session_token}"
        return json.loads(run_op_command_in_shell(op_command))

    def delete_item(self, item_name, vault):
        op_command = f"op delete item {item_name} --vault='{vault}' --session={self.session_token}"
        try:
            run_op_command_in_shell(op_command)
        except subprocess.CalledProcessError:
            raise DeletionFailure(item_name, vault)
        return "ok"

    def get(self, resource, item_name):
        op_command = f"op get {resource} '{item_name}' --session={self.session_token}"
        try:
            return run_op_command_in_shell(op_command)
        except subprocess.CalledProcessError:
            raise UnknownResourceItem(f"{resource}: {item_name}")


def run_op_command_in_shell(op_command):
    process = subprocess.run(op_command,
                             shell=True,
                             check=False,
                             capture_output=True,
                             env=os.environ)
    try:
        process.check_returncode()
    except subprocess.CalledProcessError as e:
        error_messages = ["not currently signed in",
                          "Authentication required"]
        if any(msg in process.stderr.decode("UTF-8") for msg in error_messages):
            raise Unauthorized()
        else:
            raise UnknownError(e)

    return process.stdout.decode("UTF-8").strip()


def print_onepassword_cli_version():
    subprocess.run(["/bin/bash", "-c", "op --version"], check=True)


def _get_access_token(secret, shorthand):
    try:
        process = subprocess.run(
            (f"echo '{secret['password']}' | "
             f"op signin {secret['signin_address']} {secret['username']} {secret['secret_key']} "
             f"--output=raw --shorthand={shorthand}"),
            shell=True,
            capture_output=True
        )
        process.check_returncode()
        return process.stdout.decode('UTF-8').strip()
    except subprocess.CalledProcessError as e:
        raise SigninFailure(f"Error signing in: '{process.stderr.decode('UTF-8').strip()}'")


def login(secret, shorthand="automation"):
    os.environ[f"OP_SESSION_{shorthand}"] = _get_access_token(secret, shorthand)
