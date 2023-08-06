import requests


def buscar_avatar(usuario):
    return requests.get(f'https://api.github.com/users/{usuario}').json()['avatar_url']


if __name__ == '__main__':
    print(buscar_avatar('Tchucknoia'))
