import csv
import configparser
import logging as log
import json
import click
import requests
from requests.auth import HTTPBasicAuth


class idm2cnClient:
    # init logging
    log.basicConfig(
        filename='client.log',
        level=log.INFO,
        format='%(asctime)s : %(levelname)s: %(message)s')

    log.getLogger().addHandler(log.StreamHandler())

    config = None

    ca = "../chain.txt"
    url = ''
    user = ''
    password = ''

    # create an auth object
    auth = None

    def __init__(self, configPath='../teacher.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(configPath)

        self.ca = "../chain.txt"
        self.url = self.config['api']['hostname'] + '/teacher'
        self.user = self.config['api']['user']
        self.password = self.config['api']['password']

        # create an auth object
        self.auth = HTTPBasicAuth(self.user, self.password)

    # csv

    def decomment(self, csvfile):
        for row in csvfile:
            raw = row.split('#')[0].strip()
            if raw:
                yield raw

    def post(self, username, active):
        data = {}
        data["username"] = username
        data["active"] = active
        r = requests.post(self.url, data=data, verify=self.ca, auth=self.auth)
        return r.status_code, r.json()

    def getCsv(self, pathToCsv):
        inputData = []
        numberOfRows = 0
        with open(pathToCsv, 'r') as f:
            reader = csv.DictReader(self.decomment(f), delimiter=';')
            for row in reader:
                inputData.append(row)
                numberOfRows += 1
        rowNumber = 0
        for data in inputData:
            r = requests.get(
                self.url,
                data=data,
                verify=self.ca,
                auth=self.auth)
            log.info(f"{rowNumber}/{numberOfRows}:{data['username']}")
            log.info(str(r.status_code) + ':' + str(r.json()))
            rowNumber += 1

    def postCsv(self, pathToCsv):
        inputData = []
        numberOfRows = 0
        with open(pathToCsv, 'r') as f:
            reader = csv.DictReader(self.decomment(f), delimiter=';')
            for row in reader:
                inputData.append(row)
                numberOfRows += 1
        rowNumber = 0
        for data in inputData:
            r = requests.post(
                self.url,
                data=data,
                verify=self.ca,
                auth=self.auth)
            log.info(str(rowNumber) + '/' + str(numberOfRows))
            log.info(str(r.status_code) + ':' + str(r.json()))
            rowNumber += 1

    def get(self, username):
        data = {}
        data['username'] = username
        r = requests.get(self.url, data=data, verify=self.ca, auth=self.auth)
        return r.text


@click.group()
def cli():
    pass


@click.command()
@click.option('-u', '--user', type=click.STRING, default='rc')
@click.option('-c', '--csv', 'filename', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True), default=".rc")
def get(user, filename, config):
    client = idm2cnClient(config)
    if filename:
        print(client.getCsv(filename))
        return
    while user:
        data = {}
        data['username'] = user
        print("REQUEST:")
        print(json.dumps(data, indent=4))
        print("RESPONSE:")
        print(client.get(user))
        print("#########")
        user = click.prompt("user")


@click.command()
@click.argument('user', type=click.STRING)
@click.argument('active', type=click.INT)
def post(user, active):
    client = idm2cnClient()
    print(client.post(user, active))
    print(user)


@click.command()
@click.option('--url', prompt=True)
@click.option('--user', prompt=True)
@click.option('--password', hide_input=True, prompt=True)
@click.option('--config', type=click.Path(), default=".rc")
def configure(url, user, password, config):
    with open(config, "w") as handle:
        handle.write("[api]\n")
        handle.write(f"hostname = {url}\n")
        handle.write(f"user= {user}\n")
        handle.write(f"password= {password}\n")
    print(f"config written to {config}")


cli.add_command(get)
cli.add_command(post)
cli.add_command(configure)

if __name__ == "__main__":
    cli()
