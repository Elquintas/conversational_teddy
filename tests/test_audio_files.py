import os

# import pytest


def test_files_exist_in_folder():
    """Test that the required files exist in the folder."""

    folder_animals = "./samples/animals/"
    folder_instruments = "./samples/instruments/"
    folder_spells_post = "./samples/spells-post/"
    folder_spells_pre = "./samples/spells-pre/"
    folder_system = "./samples/system/"

    files_animals = [
        "bear.wav",
        "cricket.wav",
        "donkey.wav",
        "horse.wav",
        "pig.wav",
        "wolf.wav",
        "cow.wav",
        "dog.wav",
        "eagle.wav",
        "monkey.wav",
        "raccoon.wav",
    ]
    files_instruments = ["drum.wav", "guitar.wav", "piano.wav"]
    files_spells_post = [
        "spell_post1.wav",
        "spell_post2.wav",
        "spell_post3.wav",
        "spell_post4.wav",
    ]
    files_spells_pre = [
        "spell_pre1.wav",
        "spell_pre2.wav",
        "spell_pre3.wav",
        "spell_pre4.wav",
        "spell_pre5.wav",
        "spell_pre6.wav",
    ]
    files_system = ["correct.wav", "wrong.wav", "start_rec.wav", "stop_rec.wav"]

    for file_name in files_animals:
        file_path = os.path.join(folder_animals, file_name)
        assert os.path.exists(
            file_path
        ), f"File {file_name} does not exist in the folder."

    for file_name in files_instruments:
        file_path = os.path.join(folder_instruments, file_name)
        assert os.path.exists(
            file_path
        ), f"File {file_name} does not exist in the folder."

    for file_name in files_spells_post:
        file_path = os.path.join(folder_spells_post, file_name)
        assert os.path.exists(
            file_path
        ), f"File {file_name} does not exist in the folder."

    for file_name in files_spells_pre:
        file_path = os.path.join(folder_spells_pre, file_name)
        assert os.path.exists(
            file_path
        ), f"File {file_name} does not exist in the folder."

    for file_name in files_system:
        file_path = os.path.join(folder_system, file_name)
        assert os.path.exists(
            file_path
        ), f"File {file_name} does not exist in the folder."
