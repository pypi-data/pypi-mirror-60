from pytest import *
from dramatts.core import ProjectManager, AudioRenderer
from tests.test_parser import setup_parser
import os
from pathlib import Path
import shutil


def setup_manager():
    """Creates a project manager for dramaTTS"""

    parser = setup_parser()
    audio_renderer = AudioRenderer()
    manager = ProjectManager(script_parser=parser, audio_renderer=audio_renderer)
    output_folder = Path('test_output')
    manager.output_folder = output_folder

    return manager


def test_scene_script():
    """Renders a specific scene of the script and checks if expected output files exist"""

    # create empty output folder for test files
    manager = setup_manager()
    manager.start_scene = 3
    manager.end_scene = 3

    try:
        os.mkdir(manager.output_folder)
    except FileExistsError:
        shutil.rmtree(manager.output_folder)
        os.mkdir(manager.output_folder)

    manager.render_script()

    expected_files_scene = ['scene_003_line_000.wav', 'scene_003_line_001.wav', 'scene_003_line_002.wav']
    expected_combined_file = Path().joinpath(manager.output_folder, 'scene_003.wav')

    scene_folder = Path().joinpath(manager.output_folder, 'scene_003')
    file_list = [file[2] for file in os.walk(scene_folder)]

    assert expected_combined_file.exists()
    assert sorted(file_list[0]) == expected_files_scene

    #shutil.rmtree(output_folder)


def test_postprocess():
    """Test if the post-processing works"""

    manager = setup_manager()

    # we just test, if this doesn't throw an error
    manager.normalize_audio()

    combined_file = Path(str(manager.output_folder) + '.wav')
    manager.combine_audio(input_path=manager.output_folder, output_path=combined_file)

    assert combined_file.exists()

    # clean-up
    shutil.rmtree(manager.output_folder)
    combined_file.unlink()
    Path('get_voices.scm').unlink()





