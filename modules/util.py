import os


def get_uniq_file_name(folder: str, file_name: str) -> str:
    i = 1
    uniq_file_name = f'{folder}/{file_name}'

    while os.path.exists(f'{uniq_file_name}'):
        uniq_file_name =f'{folder}/({i}){file_name}'
        i += 1

    return uniq_file_name