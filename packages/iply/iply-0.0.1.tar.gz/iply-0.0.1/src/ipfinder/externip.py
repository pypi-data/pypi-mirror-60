import requests
import click

@click.command()
@click.option('--find_ip', default=True, help='Simple CLI to discover your public IPv4 Address.')
def external_IP(find_ip):
    """
    Super simple function to obtain the Public IP.
    """
    try:
        response = requests.get('https://ident.me')
    except Exception as e:
        print('There was an error: \nError: {}'.format(e))
    else:
        if int(response.status_code) == 200:
            print("Your External IP: {}".format(response.text))
        else:
            raise Exception("Invalid Status Code.\n "
                            "Status Code: {}".format(response.status_code))
