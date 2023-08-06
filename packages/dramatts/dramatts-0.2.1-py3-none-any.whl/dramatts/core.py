"""
core.py - TTS audio renderer for plays/scripts
Copyright (C) 2020 Thies Hecker

This file is part of the dramaTTS project.

dramaTTS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import subprocess
import pathlib
from pathlib import Path
import collections
import re
import json
import os
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future, wait, FIRST_COMPLETED
import concurrent
import copy
import timeit
import warnings
# from enum import Enum, unique
from dramatts.voices import *


def handle_getstatusoutput(commandpath, cmd_args):
    """Returns the output from subprocess.getstatusoutput taking into account the os.name

    Args:
        commandpath(pathlib.Path): Path to executable including executable name
        cmd_args(tuple): Tuple with command line arguments (str) to pass to the programm
    """

    if os.name == 'posix':
        command_str = '\"{}\"'.format(commandpath)     # to handle white spaces in folder names...
        for cmd_arg in cmd_args:
            command_str = command_str + ' ' + cmd_arg
        response = subprocess.getstatusoutput(command_str)
    elif os.name == 'nt':
        response = subprocess.getstatusoutput([str(commandpath), *cmd_args])    # this seems to work only in MS win...
    else:
        warnings.warn('Unsupported file system: {}'.format(os.name))
        response = None

    return response


def convert_version_string(version_str):
    """Converts a version string into integer values for major, minor, patch

    Args:
        version_str(str): Version string like '1.0.0' or '1.0'

    Returns:
        tuple: Tuple of int values (major, minor, patch). Patch will be None, if two digit version_str provided.
    """

    version_numbers = version_str.split('.')

    if len(version_numbers) == 3:
        major, minor, patch = version_numbers
        major = int(major)
        minor = int(minor)
        patch = int(patch)
    else:   # only two digits
        major, minor = version_numbers
        major = int(major)
        minor = int(minor)
        patch = None

    return major, minor, patch

# @unique
# class ContentType(Enum):
#
#     SceneTitle = 1
#     DialogueIndicator = 2
#     DialogueContent = 3
#     InlineComment = 4
#     NarrativeDescription = 5


class ProjectManager:

    def __init__(self, script_parser, audio_renderer, output_folder=None):

        """Manager for a dramaTTS session
        
        Args:
            script_parser(ScriptParser): ScriptParser object
            audio_renderer(AudioRenderer): AudioRenderer object
            output_folder(pathlib.Path): Folder for the generated audio files

        Attributes:
            project_filepath(pathlib.Path): Path to the project file
            script_parser(ScriptParser): ScriptParser object
            audio_renderer(AudioRenderer): AudioRenderer object
            output_folder(pathlib.Path): Folder for the generated audio files
            speaker_to_render(str): Speaker name, if output for a specific speaker only shall be rendered (otherwise
                                    None)
            normalize(bool): If true the audio output will be normalized
            combine(bool): If true the files for the individual scenes will be combined to single file too
            start_scene(int): First scene to render
            end_scene(int): Last scene to render - if None the last scene in the play will be assumed
            digits_scene_no(int): Number of digits for zero padding in the scene folders/file names
            digits_line_no(int): Number of digist for zero padding of the line numbers in the wave files
            preferences(dict): Dictonary to store the program preferences - see create_prefs_dict method for details
        """
        self.project_filepath = None

        self.script_parser = script_parser
        self.audio_renderer = audio_renderer

        if output_folder:
            folder_name = output_folder
        else:
            folder_name = 'output'
        self.output_folder = pathlib.Path().joinpath(os.getcwd(), folder_name)

        self.speaker_to_render = None
        self.normalize = False  # automatically apply normalize to rendered audio
        self.combine = False

        self.digits_scene_no = 3    # digits used for zero padding of scene numbers in file/folder names
        self.digits_line_no = 3     # digit used for zero padding of line numbers in file names

        self.start_scene = 0
        self.end_scene = None

        self.preferences = None

        self.narrator = VoiceConfig()
        self.default_speaker = MaleVoice()

        # self.preferences_path = None

        # The import speakers / substitutions and their file names will be overwritten by the load_preferences method
        # this is just to initialize these values in the init before the method is called.
        self._import_speakers = False
        self._import_speakers_file = None
        self._import_substitutions = False
        self._import_substitutions_file = None

        self.terminate_threads = False

        self.load_preferences()
        self.audio_renderer.check_installed_components()

        if self._import_speakers:
            self.audio_renderer.import_voices(self._import_speakers_file)

        if self._import_substitutions:
            self.script_parser.import_substitutions(self._import_substitutions_file)

    @property
    def default_config_path(self):
        """pathlib.Path: Default config path"""
        return Path(Path.home(), '.dramatts_config.json')

    def create_prefs_dict(self):
        """dict: Creates a dictionary with the preferences settings
        """

        prefs = {
            'file_format_version': '1.0',
            'executable_paths': {
                'festival': self.audio_renderer.festival_path,
                'text2wave': self.audio_renderer.text2wave_path,
                'festival_client': self.audio_renderer.festival_client_path,
                'sox': self.audio_renderer.sox_path
            },
            'render_options': {
                'normalize_audio': self.normalize,
                'dB_level': self.audio_renderer.norm_level,
                'use_festival_server': self.audio_renderer.use_festival_server,
                'festival_server_name': self.audio_renderer.festival_server_name,
                'festival_server_port': self.audio_renderer.festival_server_port,
                'combine_output': self.combine,
                'cpu_threads': self.audio_renderer.cpu_threads
            },
            'speaker_options': {
                'import_speakers': self._import_speakers,
                'import_speakers_file': self._import_speakers_file,
                'narrator_settings': {
                    'voice': self.narrator.voice_name,
                    'pitch_shift': self.narrator.pitch_shift,
                    'tempo': self.narrator.tempo,
                    'volume': self.narrator.volume
                },
                'default_speaker_settings': {
                    'voice': self.default_speaker.voice_name,
                    'pitch_shift': self.default_speaker.pitch_shift,
                    'tempo': self.default_speaker.tempo,
                    'volume': self.default_speaker.volume
                }
            },
            'substitutions': {
                'import_substitutions': self._import_substitutions,
                'import_substitutions_file': self._import_substitutions_file
            }
        }

        return prefs

    def process_prefs_dict(self, prefs):
        """Processes the preferences dict (see create_prefs_dict) and assings values to internal variables"""

        # try:
        path_str = prefs['executable_paths']['festival']
        self.audio_renderer.festival_path = Path(path_str) if path_str else None
        path_str = prefs['executable_paths']['text2wave']
        self.audio_renderer.text2wave_path = Path(path_str) if path_str else None
        path_str = prefs['executable_paths']['festival_client']
        self.audio_renderer.festival_client_path = Path(path_str) if path_str else None
        path_str = prefs['executable_paths']['sox']
        self.audio_renderer.sox_path = Path(path_str) if path_str else None

        self.normalize = prefs['render_options']['normalize_audio']
        self.audio_renderer.norm_level = prefs['render_options']['dB_level']
        self.audio_renderer.use_festival_server = prefs['render_options']['use_festival_server']
        self.audio_renderer.festival_server_name = prefs['render_options']['festival_server_name']
        self.audio_renderer.festival_server_port = prefs['render_options']['festival_server_port']
        self.combine = prefs['render_options']['combine_output']
        self.audio_renderer.cpu_threads = prefs['render_options']['cpu_threads']

        self._import_speakers = prefs['speaker_options']['import_speakers']
        path_str = prefs['speaker_options']['import_speakers_file']
        self._import_speakers_file = Path(path_str) if path_str else None
        speaker_settings = prefs['speaker_options']['narrator_settings']
        self.narrator = VoiceConfig(voice_name=speaker_settings['voice'],
                                    pitch_shift=speaker_settings['pitch_shift'],
                                    tempo=speaker_settings['tempo'],
                                    volume=speaker_settings['volume'])
        speaker_settings = prefs['speaker_options']['default_speaker_settings']
        self.default_speaker = VoiceConfig(voice_name=speaker_settings['voice'],
                                           pitch_shift=speaker_settings['pitch_shift'],
                                           tempo=speaker_settings['tempo'],
                                           volume=speaker_settings['volume'])

        self._import_substitutions = prefs['substitutions']['import_substitutions']
        path_str = prefs['substitutions']['import_substitutions_file']
        self._import_substitutions_file = Path(path_str) if path_str else None

    def load_preferences(self, filepath=None):
        """Loads the preferences from a json file

        Args:
            filepath(pathlib.Path): If none the default config file (see default_config_path property method)
        """
        if filepath is None:
            if self.default_config_path.exists():
                # loads preferences from default config
                with open(self.default_config_path, 'r') as file:
                    json_str = file.read()
                json_data = json.loads(json_str)
                self.process_prefs_dict(prefs=json_data)
                print('Preferences imported from default config:', self.default_config_path)
            else:
                # create a new preferences file
                print('Could not find default preferences file - creating new file', self.default_config_path)
                self.save_preferences(self.default_config_path)
        else:
            if filepath.exists():
                with open(filepath, 'r') as file:
                    json_str = file.read()
                json_data = json.loads(json_str)
                self.process_prefs_dict(prefs=json_data)
                print('Preferences imported from:', filepath)
            else:
                print('Preferences file {} does not exist - loading default file {}'.format(filepath,
                                                                                            self.default_config_path))
                self.load_preferences()
                
    def save_preferences(self, filepath=None):
        """Saves the preferences to a json file

        Args:
            filepath(pathlib.Path): If none the default config file will be used
                                    (see default_config_path property method)
        """
        # get config dict
        config_dict = self.create_prefs_dict()

        if filepath is None:
            filepath = self.default_config_path

        with open(filepath, 'w') as file:
            file.write(json.dumps(config_dict, indent=4, default=str))

        print('Preferences saved to:', filepath)

    def get_scene_no_str(self, scene_no):
        """str: Returns a string representation of the scene number"""
        return str(scene_no).zfill(self.digits_scene_no)

    def get_line_no_str(self, line_no):
        """str: Returns a string representation of the line number"""
        return str(line_no).zfill(self.digits_line_no)

    def get_scene_folder_path(self, scene_no):
        """pathlib.Path: Returns the path to a scene subfolder"""
        sub_folder = 'scene_{}'.format(self.get_scene_no_str(scene_no))
        abs_sub_folder = pathlib.Path().joinpath(self.output_folder, sub_folder)
        return abs_sub_folder

    def render_line_from_dict(self, line_dict):
        """Renders a line based on the dictionary provided by the script parser

        Args:
            line_dict(dict): An element of the list returned by ScriptParser.get_filtered_valid_lines method

        Returns:
            dict: Returns the argument
        """
        speaker = line_dict['speaker']
        scene_no = line_dict['scene_no']
        line_no = line_dict['scene_line_no']
        text = line_dict['content']

        # check if the voice for the speaker is defined - if not use the narrator's voice
        if speaker not in self.audio_renderer.voices.keys():
            speaker = 'Narrator'

        abs_sub_folder = self.get_scene_folder_path(scene_no)

        # create subfolder if it doesn't exist
        # if not abs_sub_folder.exists():
        try:
            os.mkdir(abs_sub_folder)
        except FileExistsError:
            pass

        filename = 'scene_{}_line_{}.wav'.format(self.get_scene_no_str(scene_no), self.get_line_no_str(line_no))

        full_filename = pathlib.Path().joinpath(abs_sub_folder, filename)

        self.audio_renderer.render_audio(voice=speaker, text=text,
                                         filename=full_filename, normalize=self.normalize)

        return line_dict

    @staticmethod
    def _cancelled_thread_finished(thread):
        """Callback function for cancelled threads, which were still running

        Args:
            thread(concurrent.futures.Future): Future of the thread
        """
        print('One further thread finished.')

    def render_script(self):
        """Renders the script into audio files
        """

        # check some preconditions before starting to render
        if not self.output_folder.exists():
            print('The output folder {} does not exist. '
                  'Create it first or select another output folder to start the rendering.'.format(self.output_folder))
            return
        if self.script_parser.lines_list is None:
            print('No parsed lines found. Import a project or script first!')
            return

        if len(self.audio_renderer.invalid_voices) > 0:
            print('Your speaker configurations contain invalid parameters. Please check the speaker configurations!')
            return

        if not self.audio_renderer.external_tools['festival']['installed']:
            print('No valid festival installation found. Configure festival first.')
            return
        else:
            if (self.audio_renderer.use_festival_server
                    and not self.audio_renderer.external_tools['festival_client']['installed']):
                print('Festival server option selected, but festival_client application not found.')
                return
            if (not self.audio_renderer.use_festival_server
                    and not self.audio_renderer.external_tools['text2wave']['installed']):
                print('Could not find text2wave script. Configure text2wave first.')
                return

        if not self.audio_renderer.external_tools['sox']['installed']:
            print('No valid SoX installation found. Configure SoX first.')

        lines = self.script_parser.get_filtered_valid_lines(first_scene=self.start_scene, last_scene=self.end_scene,
                                                            speaker=self.speaker_to_render)

        if self.audio_renderer.use_festival_server:
            method = "festival server: {}:{}".format(self.audio_renderer.festival_server_name,
                                                     self.audio_renderer.festival_server_port)
        else:
            method = "text2wave (locally)"

        print("---------------------------------\n"
              "Starting to render script...\n"
              "(using {})\n"
              "---------------------------------\n".format(method))

        start_time = timeit.default_timer()

        lines_total = len(lines)
        lines_finished = 0
        last_scene = self.start_scene - 1
        # start rendering line after line
        with ThreadPoolExecutor(max_workers=self.audio_renderer.cpu_threads) as executor:
            future_to_renderline = {executor.submit(self.render_line_from_dict, line): line for line in lines}
            for future in concurrent.futures.as_completed(future_to_renderline):
                if self.terminate_threads:
                    # print('Cancelling render threads...')
                    running_threads = []
                    for i, remaining_future in enumerate(future_to_renderline):
                        # try to cancel all futures - finished and running will throw False
                        remaining_future.cancel()
                        if not remaining_future.done():
                            running_threads.append(remaining_future)
                            remaining_future.add_done_callback(self._cancelled_thread_finished)
                    print('{} render thread(s) still running...'.format(len(running_threads)))
                    break

                else:
                    line_dict = future_to_renderline[future]
                    lines_finished += 1
                    if line_dict['scene_no'] > last_scene:
                        print('Starting to render scene {}'.format(line_dict['scene_no']))
                        last_scene = line_dict['scene_no']
                    print("{}/{} lines finalized.".format(lines_finished, lines_total))

        if self.terminate_threads:
            print('All render threads terminated.')
            self.terminate_threads = False
            return

        # combine the files of the individual scenes:
        # This should better be done after all line have rendered, otherwise we will have to check, that all threads
        # rendering lines of a specific scene have finished.
        end_scene = self.end_scene if self.end_scene else self.script_parser.scene_count - 1
        for scene_index in range(end_scene - self.start_scene + 1):
            # get the scene number the first line belongs to - this is the start offset for the scene folder names
            scene_offset = lines[0]['scene_no']
            scene_folder = Path().joinpath(self.output_folder,
                                           'scene_{}'.format(self.get_scene_no_str(scene_index + scene_offset)))
            scene_filename = Path('{}.wav'.format(str(scene_folder)))
            self.combine_audio(input_path=scene_folder, output_path=scene_filename)

        # combine all scenes to one file if defined
        if self.combine:
            self.combine_audio(input_path=self.output_folder,
                               output_path=Path('{}.wav'.format(str(self.output_folder))))

        end_time = timeit.default_timer()

        render_time = end_time - start_time

        print("---------------------------------\n"
              "Render time: {:6.2f} s\n"
              "Script rendered to {}\n".format(render_time, self.output_folder),
              "---------------------------------\n")

    def add_speakers_for_characters(self):
        """Adds default speaker for each character found by the script parser, who does not alerady have a speaker
        assigned
        """
        counter = 0
        for character in self.script_parser.get_lines_per_character().keys():
            if character not in self.audio_renderer.voices.keys():
                self.audio_renderer.voices[character] = copy.deepcopy(self.default_speaker)
                counter += 1

        print('{} characters added to the speaker list.'.format(counter))

    def combine_audio(self, input_path=None, output_path=None):
        """Merges all files in one directory (excluding subdirs) into a single file

        Args:
            input_path(pathlib.Path): Folder name of files to combine (defaults to output_folder)
            output_path(pathlib.Path): Filename of combined file (defaults to output_folder + .wav)

        """
        # TODO: should add a check, that files are actually wave files...

        if input_path is None:
            input_path = self.output_folder
        if output_path is None:
            output_path = Path(str(self.output_folder) + '.wav')

        filenames = [folder[2] for folder in os.walk(input_path)][0]
        filenames.sort()
        if filenames:
            filepaths = [Path().joinpath(input_path, filename) for filename in filenames]
            file_strings = [str(file) for file in filepaths if '.wav' in str(file)]

            subprocess.run([str(self.audio_renderer.sox_path), *file_strings, str(output_path)])

            print('Combined files in folder {} to file {}.'.format(input_path, output_path))
        else:
            warnings.warn('No files in {} found. Please check the input file path.'.format(input_path))

    def normalize_audio(self):
        """Normalizes all audio segments and rebuilds files for each scene"""
        subdirs = sorted([subdir[0] for subdir in os.walk(self.output_folder)][1:])
        no_subdirs = len(subdirs) - 1

        norm_level = self.audio_renderer.norm_level

        for i, subdir in enumerate(subdirs):

            scene_no = subdir.split('/')[-1].split('_')[1]
            print('Entering subdir for scene', scene_no)
            files = sorted([data[2] for data in os.walk(subdir)][0])

            no_files = len(files)
            for j, filename in enumerate(files):
                if '.wav' in filename:
                    # rename orginal file first
                    input_filename = pathlib.Path().joinpath(subdir, 'raw_' + filename)
                    full_filename = pathlib.Path().joinpath(subdir, filename)
                    os.rename(full_filename, input_filename)
                    # TODO: The command below should be added to the audio renderer class as a method...
                    subprocess.run([str(self.audio_renderer.sox_path), str(input_filename), str(full_filename),
                                    'norm', str(norm_level)])
                    # remove original
                    os.remove(input_filename)

                    print('Normalized file: dir {}/{}, file {}/{}'.format(i + 1, no_subdirs, j + 1, no_files))

            # merge sound files to a single file
            os.remove(pathlib.Path().joinpath(self.output_folder, 'scene_{}.wav'.format(scene_no)))
            # shell_command = 'sox $(ls {}/*.wav | sort -n) {}/scene_{}.wav'.format(subdir, self.output_folder, scene_no)
            # subprocess.run(shell_command, shell=True)
            output_file = Path().joinpath(self.output_folder, 'scene_{}.wav'.format(scene_no))
            self.combine_audio(subdir, output_file)
            print('Rebuild file for scene {}'.format(scene_no))

    def create_project_dict(self):
        """dict: Creates a dictionary representation of the current project settings
        """

        render_options = self.create_prefs_dict()['render_options']
        render_options['start_scene'] = self.start_scene
        render_options['end_scene'] = self.end_scene
        render_options['output_folder'] = str(self.output_folder)

        save_ident_assign = {}
        for key in self.script_parser.ident_assignements.keys():
            save_ident_assign[key] = self.script_parser.ident_assignements[key]['name']

        project = {
            'file_format_version': '1.1',
            'script_lines': self.script_parser.valid_lines_list,
            'characters': self.script_parser.characters,
            'substitutions': self.script_parser.substitutions,
            'speakers': self.audio_renderer.create_voices_dict(),
            'render_options': render_options,
            'content_identifiers': self.script_parser.content_identifiers,    # added in version 1.1
            'identifier_assignments': save_ident_assign    # added in version 1.1
        }
        
        return project
    
    def process_project_dict(self, project):
        """Reads a project dict and assigns to internal variables"""

        version_major, version_minor, _ = convert_version_string(project['file_format_version'])

        self.normalize = project['render_options']['normalize_audio']
        self.audio_renderer.norm_level = project['render_options']['dB_level']
        self.audio_renderer.use_festival_server = project['render_options']['use_festival_server']
        self.combine = project['render_options']['combine_output']
        self.audio_renderer.cpu_threads = project['render_options']['cpu_threads']
        path_str = project['render_options']['output_folder']
        self.output_folder = Path(path_str) if path_str else None
        self.start_scene = project['render_options']['start_scene']
        self.end_scene = project['render_options']['end_scene']

        self.script_parser.lines_list = project['script_lines']
        self.script_parser.characters = project['characters']
        self.script_parser.substitutions = project['substitutions']
        self.audio_renderer.read_voices_dict(project['speakers'])

        # added in version 1.1
        if version_major >= 1 and version_minor >= 1:
            self.script_parser.content_identifiers = project['content_identifiers']

            for key, name in project['identifier_assignments'].items():
                for ident in self.script_parser.content_identifiers:
                    if ident['name'] == name:
                        self.script_parser.ident_assignements[key] = ident

    def save_project(self, filepath=None):
        """Save the complete project

        Args:
            filepath(pathlib.Path): path to file name (if None self.project_filepath will be used)
        """

        if filepath is None:
            if self.project_filepath:
                filepath = self.project_filepath
            else:
                print('You need to provide a filename or set the project_filepath attribute.')
                return

        project_dict = self.create_project_dict()
        with open(filepath, 'w') as file:
            file.write(json.dumps(project_dict, indent=4))

        self.project_filepath = filepath
        print('Project saved to', filepath)

    def load_project(self, filepath=None):
        """Loads a project from a file

        Args:
            filepath(pathlib.Path): path to file name (if None self.project_filepath will be used)
        """

        if filepath is None:
            if self.project_filepath:
                filepath = self.project_filepath
            else:
                print('You need to provide a filename or set the project_filepath attribute.')
                return

        with open(filepath, 'r') as file:
            data = json.loads(file.read())

        self.process_project_dict(data)
        self.project_filepath = filepath

        print('Project loaded from', filepath)

    def convert_speaker_to_comment(self, speaker_name, from_prefix='\n', from_suffix='\n', to_prefix='\n(',
                                   to_suffix='\n)'):
        """Deletes and entry in the speakers dictionary and creates a substitution adding prefixes and suffixes

        Args:
            from_prefix(str): Prefix before speaker_name to include in search text
            from_suffix(str): Suffix after speaker_name to include in search text
            to_prefix(str): Prefix before speaker_name to include in substitution
            to_suffix(str): Suffix after speaker_name to include in subsitution

        Notes:
            * This is useful, if the parser misunderstood director instructions for speaker names (DialogueIndicator)
        """

        if speaker_name in self.audio_renderer.voices.keys():
            self.audio_renderer.voices.pop(speaker_name)

            search_text = from_prefix + speaker_name + from_suffix
            subst = to_prefix + speaker_name + to_suffix

            speaker_subst = {
                "search_text": search_text,
                "subst": subst,
                "regex": True,
                "comment": "Avoid taking this as a speaker name."
            }

            self.script_parser.substitutions.append(speaker_subst)

            print('Substiution: {} --> {} has been added to substitutions list'.format(search_text, subst))


class ScriptParser:

    def __init__(self, input_file=None, start_line=0, end_line=None, substitutions=None):

        """A parser to identify content types inside a text file

        Args:

            input_file(pathlib.Path): Path to text file
            start_line(int): First line to import
            end_line(int): Last line to import - None means last line of text file
            substitutions(list): A list of text substitutions - details see Attributes

        Attributes:

            filename(pathlib.Path): Path to text file
            start_line(int): First line to import
            end_line(int): Last line to import - if None last line of text file
            substitutions(list): A list of dictionaries with keys:

                            - 'search_text'(str): Text or RegEx pattern to search for
                            - 'subst'(str): Replacement text
                            - 'regex'(bool): If true - assume 'search_text' is a RegEx
                            - 'comment'(str): Additional information on this substitution

            text(str): Raw text of the imported file
            characters(list): List of characters in the play
            lines_list(list): List of dictionaries for each line/paragraph identified in the text - dict keys:

                              - 'start'(int): index of first character inside the text
                              - 'end'(int): index of last character inside the text
                              - 'content'(str): Content of the line/paragraph
                              - 'content_type'(str):
                                    - 'SceneTitle',
                                    - 'DialogueIndicator',
                                    - 'DialogueContent',
                                    - 'InlineComment'
                                    - 'NarrativeDescription'
                              - 'speaker'(str): Name of speaker for this line - e.g. a character's name

            content_identifiers(list): List of dictionaries - for each content identifier with keys:

                                      - 'name'(str): Name of the identifier
                                      - 'pattern'(str): RegEx pattern
                                      - 'info'(str): Explantation of the content identifier
                                      - 'example'(str): An example matching the pattern

            ident_assigments(dict): Assignment of different identifier types to a content identifier - valid keys are:
                                    'SceneTitle', 'Dialogue', 'SpeakerName' and 'InlineComment' - the value must be a
                                    content identifier dictionary (e.g. an element of the content_identifiers list)

        """

        self.filename = input_file
        self.start_line = start_line
        self.end_line = end_line
        self.text = None
        self.characters = None
        self.lines_list = None

        self.content_identifiers = [
            {
                'name': 'SceneIdent01',
                'pattern': r'\n[0-9]+\. .*?\n',
                'info': 'A new line starts with at least one number followed by a dot and a whitespace. '
                        'Afterwards text. Terminated by the next line break',
                'example': '\n123. Last scene\n'
            },
            {
                'name': 'DialogueIdent01',
                'pattern': r'\n[A-Z -]{2,}\n\n.*?\n',
                'info': 'A new line starts with a string consisting of only UPPER case letters, white space and '
                        'hyphens. Is followed by two line breaks, some text and terminated by the next line break',
                'example': '\nBOB MILLER\n\nHello my name is Bob.\n'
            },
            {
                'name': 'SpeakerNameIdent01',
                'pattern': r'\n[A-Z -]{2,}\n',
                'info': 'A new line starts with a string consisting of only UPPER case letters, white space and '
                        'hyphens. It is terminated by a line break.',
                'example': '\nBOB MILLER\n'
            },
            {
                'name': 'CommentIdent01',
                'pattern': '(\(.*?\))',
                'info': 'A text part starts with (, followed by any text and terminated by ).',
                'example': '(he turns away and says)'
            },
            # 'NarrativeDescription': {     # everything not matched by the categories above will be assigned narrative
            #
            # }
        ]

        self.ident_assignements = {
            'SceneTitle': self.content_identifiers[0],
            'Dialogue': self.content_identifiers[1],
            'SpeakerName': self.content_identifiers[2],
            'InlineComment': self.content_identifiers[3]
        }

        if substitutions:
            self.substitutions = substitutions
        else:
            self.substitutions = []

    def check_content_identifiers(self):
        """Checks the content identifiers patterns vs. the example

        Returns:
            bool: True if example matches pattern
        """

        identifiers_okay = True

        for check in self.content_identifiers:
            match = re.match(check['pattern'], check['example'])
            if match is None:
                print('Example doesn\'t match pattern for', check['name'])
                identifiers_okay = False

        return identifiers_okay

    def parse_lines(self, filename=None):
        """Parses the specified text file and assign result to lines_list attribute

        Args:
            filename(pathlib.Path): Path to textfile, if None the filename attribute will be used (if defined)

        Returns:
            list: The value of the lines_list attribute
        """

        if filename is None:
            if self.filename:
                filename = self.filename
            else:
                print('No filename defined.')
                return

        # read individual text lines
        with open(filename, 'r') as file:
            text_lines = file.readlines()

        # join lines for selected range
        text = "".join(text_lines[self.start_line:self.end_line])
        print('Read {} lines from: {}'.format(len(text_lines[self.start_line:self.end_line]), self.filename))

        # call the substitute text procedure
        text = self.substiute_text(text)

        # check the different content types
        self.characters = ['Narrator']
        parsed_content = []

        # find scene titles
        pattern = self.ident_assignements['SceneTitle']['pattern']

        matches = re.finditer(pattern, text)
        for match in matches:
            parsed_content.append({
                'start': match.span()[0],
                'end': match.span()[1],
                'content': match.group(0).strip(),
                'content_type': 'SceneTitle',
                'speaker': 'Narrator'
            })

        # find dialogues
        pattern = self.ident_assignements['Dialogue']['pattern']

        matches = re.finditer(pattern, text)
        for match in matches:

            start = match.span()[0]
            # end = match.span()[1]
            dialogue_str = match.group(0)

            speaker_pattern = self.ident_assignements['SpeakerName']['pattern']

            speaker = re.match(speaker_pattern, dialogue_str)

            speaker_name = speaker.group(0)
            speaker_name_strip = speaker_name.strip()

            # add speaker to characters if not already in the list
            if speaker_name_strip not in self.characters:
                self.characters.append(speaker_name_strip)

            # add dialogue indicator to parse lines
            parsed_content.append({
                'start': speaker.span()[0] + start,
                'end': speaker.span()[1] + start,
                'content': speaker_name.strip(),
                'content_type': 'DialogueIndicator',
                'speaker': 'Narrator'
            })

            # continue for dialog content and identify inline comments
            dialog_start = speaker.span()[1] + start + 1
            _, _, dialogue_content_str = dialogue_str.partition(speaker_name)

            comment_pattern = self.ident_assignements['InlineComment']['pattern']

            comment_matches = re.finditer(comment_pattern, dialogue_content_str)
            last_start = 0
            last_end = -1
            if comment_matches:
                for comment in comment_matches:
                    comment_start = comment.span()[0]
                    comment_end = comment.span()[1]
                    if comment_start > 0:
                        dialog_content = dialogue_content_str[last_end+1:comment_start-1]
                        parsed_content.append({
                            'start': dialog_start + last_end + 1,
                            'end': dialog_start + comment_start - 1,
                            'content': dialog_content.strip(),
                            'content_type': 'DialogueContent',
                            'speaker': speaker_name_strip
                        })
                    parsed_content.append({
                        'start': dialog_start + comment_start,
                        'end': dialog_start + comment_end,
                        'content': comment.group(0).strip(),
                        'content_type': 'InlineComment',
                        'speaker': 'Narrator'
                    })
                    last_end = comment_end
                # if there is dialogue content after the last comment add this, when the loop has finished
                if last_end < len(dialogue_content_str):
                    parsed_content.append({
                        'start': dialog_start + last_end + 1,
                        'end': dialog_start + len(dialogue_content_str) - 1,
                        'content': dialogue_content_str[last_end+1:].strip(),
                        'content_type': 'DialogueContent',
                        'speaker': speaker_name_strip
                    })
            else:   # if there are no comments in the dialogue
                parsed_content.append({
                    'start': dialog_start,
                    'end': dialog_start + len(dialogue_content_str),
                    'content': dialogue_content_str.strip(),
                    'content_type': 'DialogueContent',
                    'speaker': speaker_name_strip
                })

        # sort acc. to start value
        parsed_content = sorted(parsed_content, key=lambda k: k['start'])

        # now check for everything, which is not found by matches above and assign it narrative description

        start_index = 0
        final_parsed_content = copy.deepcopy(parsed_content)
        for content_found in parsed_content:
            if content_found['start'] > start_index:
                narrative_content = text[start_index:content_found['start']-1]
                final_parsed_content.append({
                    'start': start_index,
                    'end': content_found['start'] - 1,
                    'content': narrative_content.strip(),
                    'content_type': 'NarrativeDescription',
                    'speaker': 'Narrator'
                })
            start_index = content_found['end'] + 1

        # sort again acc. to start value
        final_parsed_content = sorted(final_parsed_content, key=lambda k: k['start'])

        self.lines_list = final_parsed_content

        return final_parsed_content

    def substiute_text(self, text):
        """Substitutes elements in text (supports regex as defined by python re module)

        Args:
            text(str): Text to check/modify

        Returns:
            str: Modified text
        """

        for subst in self.substitutions:
            if subst['regex']:
                p = re.compile(subst['search_text'])
                text = p.sub(subst['subst'], text)
            else:
                text = text.replace(subst['search_text'], subst['subst'])

        return text

    def get_characters_from_parsed_lines(self):
        """Gets characters list from parsed lines and assign it to the characters attribute

        Returns:
            None
        """
        characters = []
        for line in self.lines_list:
            if line['speaker'] not in characters:
                characters.append(line['speaker'])

        self.characters = characters

    @property
    def scene_count(self):
        """int: Number of scenes in the script"""

        if self.scenes_titles:
            return len(self.scenes_titles)
        else:
            return 0

    @property
    def scenes_titles(self):
        """list: List of the scene titles"""

        scenes = []

        for line in self.valid_lines_list:
            if len(scenes) == 0:
                if line['content_type'] != 'SceneTitle':  # lines before first scene - add scene 'Preface'
                    scenes.append('Preface')
                else:
                    scenes.append(line['content'])
            else:
                if line['content_type'] == 'SceneTitle':
                    scenes.append(line['content'])

        return scenes

    @property
    def valid_lines_list(self):
        """list: Only non-empty lines/paragraphs of the lines_list attribute

        Note:
            Has additional key-value pairs cmp. lines_list:

                - 'scene_no'(int): Scene the line/paragraph belongs to
                - 'scene_line_no'(int): Line number inside the side (where 0 is always the SceneTitle).
        """
        # remove all empty lines

        if self.lines_list:

            non_empty = [line for line in self.lines_list if line['content_type'] != 'empty']

            # do some clean-up
            for i, line in enumerate(non_empty):
                # add a line number
                non_empty[i]['line_no'] = i
                # Convert all UPPER CASE words in Capital Case to avoid festival treating them as abbreviations
                matches = re.findall('[A-Z]{2,}', line['content'])
                if matches:
                    new_line_content = line['content']
                    for match in matches:
                        new_line_content = new_line_content.replace(match, match.capitalize())
                    non_empty[i]['content'] = new_line_content

                # convert multiple line break into single line breaks
                non_empty[i]['content'] = re.sub(r'\n{2,}', '\n', line['content'])

            # add scene numbers and line number in scene
            scene_number = 0
            scene_line_counter = 0
            for line in non_empty:
                if line['content_type'] == 'SceneTitle':
                    scene_number += 1
                    scene_line_counter = 0
                line['scene_no'] = scene_number
                line['scene_line_no'] = scene_line_counter

                scene_line_counter += 1
        else:
            non_empty = []

        return non_empty

    def get_filtered_valid_lines(self, first_scene=0, last_scene=None, speaker=None):
        """Filters the valid_lines_list acc. to scene range and speaker name

        Args:
            first_scene(int): Start scene
            last_scene(int): End scene - if None the last scene of the play will be assumed
            speaker(str): Name of speaker to limit filter to

        Returns:
            list: List of dicts - same format as valid_lines_list, but filtered to scene range and/or speaker
        """

        if last_scene is None:
            last_scene = self.scene_count

        lines_filtered = []

        for line in self.valid_lines_list:
            if first_scene <= line['scene_no'] <= last_scene:   # filter for scenes
                if speaker is None or line['speaker'] == speaker:   # filter for speaker
                    lines_filtered.append(line)

        return lines_filtered

    def get_lines_per_character(self):
        """Counts the lines/paragraphs for each speaker

        Returns:
            dict: key = character name - value = no. of lines, sorted by the number by line count (descending)
        """
        line_char = {'Narrator': 0}
        for character in self.characters:
            line_char[character] = 0

        for line in self.valid_lines_list:
            speaker = line['speaker']
            if speaker in line_char.keys():
                line_char[speaker] += 1
            else:
                print('Could not find {} in characters. Will be ignored'.format(speaker))

        # sort
        lines_sorted = {k: v for k, v in sorted(line_char.items(), key=lambda item: item[1], reverse=True)}

        return lines_sorted

    @property
    def identifier_names(self):
        """list: Returns a list of available identifier names"""
        return [ident['name'] for ident in self.content_identifiers]

    def export_parsed_lines(self, filename):
        """Exports the parsed lines"""
        with open(filename, 'w') as file:
            file.write(json.dumps(self.valid_lines_list, indent=4))

    def import_parsed_lines(self, filename):
        """Imports parsed lines from json"""
        with open(filename, 'r') as file:
            json_data = file.read()

        self.lines_list = json.loads(json_data)

    def export_substitutions(self, filename):
        """Exports the substitutions"""
        with open(filename, 'w') as file:
            file.write(json.dumps(self.substitutions, indent=4))

    def import_substitutions(self, filename):
        """Imports the list of substitutions from a file"""
        with open(filename, 'r') as file:
            json_data = file.read()
        self.substitutions = json.loads(json_data)

    def export_identifiers(self, filename):
        """Exports the content identifiers"""
        with open(filename, 'w') as file:
            file.write(json.dumps(self.content_identifiers, indent=4))
        print('Identifiers exported to', filename)

    def import_identifiers(self, filename):
        """Imports the list of content identifiers from a file"""
        with open(filename, 'r') as file:
            json_data = file.read()
        self.content_identifiers = json.loads(json_data)
        print('Identifiers imported from', filename)
        self.check_content_identifiers()


class AudioRenderer:

    def __init__(self, voices=None, cpu_threads=4):

        """This class provides configuration of the audio rendering and wrappers to launch the external tools (festival,
        sox) with predefined parameters for speech synthesis and post-processing

        Args:
            voices(dict): Dictionary with key = speaker name, value is a VoiceConfig object
            cpu_threads(int): Number of parallel CPU threads to use for rendering

        Attributes:
            voices(dict): Dictionary with key = speaker name, value is a VoiceConfig object
            cpu_threads(int): Number of parallel CPU threads to use for rendering
            norm_level(int): DB level to use for normalizing audio
            sox_path(pathlib.Path): Path to the SoX application
            festival_path(pathlib.Path): Path to the festival application
            festival_client_path(pathlib.Path): Path to the festival_client application
            text2wave_path(pathlib.Path): Path to the text2wave script
            installed_festival_voices(list): List of voice names installed for festival
            external_tools(dict): A dictionary with the configuration setting for the external tools - keys: 'festival',
                                  'festival_client', 'sox' and 'text2wave'. Each tool's key holds another dictionary
                                  with the keys:
                                    - 'path'(pathlib.Path): Path to application
                                    - 'version'(str): Version string
                                    - 'installed'(bool): True if the tool was found to be working
            use_festival_server(bool): True if server should be used instead of local render via text2wave
            festival_server_name(str): Hostname or IP-Address of the festival server
            festival_server_port(int): Port number of the server
            invalid_voices(list): List of speaker names with invalid configuration (e.g. defined festival voices not
                                  installed) - a dict for each invalid speaker with keys:
                                      - 'name'(str): Name of the speaker
                                      - 'index'(int): Position of the speaker in the voices attribute
                                      - 'params'(list): A list of invalid parameter names - e.g. ['voice_name']

        """

        self.cpu_threads = cpu_threads
        self.norm_level = -3    # normalize level for sound files

        self.sox_path = None
        self.festival_path = None
        self.festival_client_path = None
        self.text2wave_path = None

        self.installed_festival_voices = None

        self.external_tools = {
            'festival': {},
            'festival_client': {},
            'sox': {},
            'text2wave': {}
        }

        self.use_festival_server = False
        self.festival_server_name = 'localhost'
        self.festival_server_port = 1314

        self.invalid_voices = []

        if voices:
            self.voices = voices
        else:
            self.voices = {'Narrator': VoiceConfig('cmu_us_slt_cg')}

        # check for installed components
        self.check_installed_components()

    @staticmethod
    def get_tool_feedback(command_name, path=None, cmd_args=('--version',)):
        """Calls an external tool with certain arguments and returns feedback (for testing functionality)

        Args:
            command_name(str): Name of command to check
            path(pathlib.Path): Path to the executable, if None see below
            cmd_args(tuple): Command line arguments to pass to tool

        Note:
            If path is none the command will be invoked only with the commnand_name - assuming the executable's location
            is added to the PATH environment variable.
        """
        if path:
            command_path = path
        else:
            command_path = command_name

        try:
            # cmd_str = str(command_path)
            # for cmd_arg in cmd_args:
            #     cmd_str = cmd_str + ' ' + cmd_arg
            result = handle_getstatusoutput(commandpath=command_path, cmd_args=cmd_args)
            if result[0] != 0:
                warnings.warn('Could not find \"{}\" executable!'.format(command_name))
                version = None
            else:
                version = result[1]
        except PermissionError:
            warnings.warn('Could not find \"{}\" executable!'.format(command_name))
            version = None
        except FileNotFoundError:
            warnings.warn('Could not find \"{}\" executable!'.format(command_name))
            version = None

        return version

    def get_festvial_voices(self):
        """list: List of the installed festival voices (str)"""

        with open('get_voices.scm', 'w') as file:
            file.write('(print (voice.list))')
        voice_str = handle_getstatusoutput(commandpath=self.festival_path, cmd_args=('-b', 'get_voices.scm'))[1]
        for char in ['(', ')', '\n']:
            voice_str = voice_str.replace(char, '')
        voices = voice_str.split(' ')     # first and last chars are ( )\n

        if len(voices) > 0:
            print('Found {} voices:'.format(len(voices)))
            for voice in voices:
                print(voice, end=" ")
        else:
            print('Could not find any festival voices!')

        return voices

    def check_voices(self):
        """Checks the voice parameters for correctness (e.g. voice installed) and assigns invalid voices
         to the invalid_voices attribute

        Returns:
            list: List of dicts with speaker name, index and invalid parameter in self.voices
        """

        invalid_voices = []

        for i, name in enumerate(self.voices.keys()):
            voice_name = self.voices[name].voice_name
            pitch = self.voices[name].user_pitch_shift
            tempo = self.voices[name].user_tempo
            vol = self.voices[name].user_volume

            invalid_params = []
            invalid = True
            if voice_name not in self.installed_festival_voices:
                invalid_params.append('voice_name')
            elif type(pitch) != int:
                invalid_params.append('pitch')
            elif type(tempo) != float:
                invalid_params.append('tempo')
            elif type(vol) != float:
                invalid_params.append('vol')
            else:
                invalid = False

            if invalid:
                invalid_voices.append({'name': name, 'index': i, 'params': invalid_params})
                print('Invalid voice params found for speaker {} - invalid params:'.format(name), invalid_params)

        self.invalid_voices = invalid_voices
        return invalid_voices

    @staticmethod
    def get_ext_tool_path(exec_name):
        """Get path to external executable

        Args:
            exec_name(str): Name of the application/executable

        Returns:
            str: Path to executable if found - else None
        """
        if os.name == 'posix':
            search_cmd = 'which'
        elif os.name == 'nt':
            search_cmd = 'where'

        path_str = subprocess.getstatusoutput('{} {}'.format(search_cmd, exec_name))

        if path_str[0] == 0:
            tool_path = Path(path_str[1])
            print('Found {} in {}'.format(exec_name, tool_path))
        else:
            tool_path = None
            print('Can\'t find {}'.format(exec_name))

        return tool_path

    def check_component(self, path, tool_name, test_args, answer_str, answer_version=False):
        """Checks an individual external tool by invoking the tool with defined test arguments and validating against
        an expected answer

        Args:
            path(pathlib.Path): Path to executable (incl. executable name)
            tool_name(str): Name of tool
            test_args(tuple): Command line arguments to use for functions test (e.g. to get version string)
            answer_str(str): A required str in the answer of the command line invocation with test_args
            answer_version(bool): Extract version str form

        Returns:
            dict: with keys: path, version and installed.
        """
        tool_dict = {'path': None, 'version': None, 'installed': False}

        if path is None:
            print('Checking for {} in PATH...'.format(tool_name), end=' ')
            path = self.get_ext_tool_path(tool_name)
        tool_dict['path'] = path
        response = self.get_tool_feedback(tool_name, path, test_args)
        print('Checking {}...'.format(tool_name))
        if response:
            if answer_str in response:
                if answer_version:
                    version = ':'.join(response.split(':')[1:]).strip()
                    print('version: {}'.format(version))
                    tool_dict['version'] = version
                tool_dict['installed'] = True
                print('{} seems to be working fine.'.format(tool_name))
            else:
                print('{} is NOT working!'.format(tool_name))
        else:
            print('{} is NOT working!'.format(tool_name))

        return tool_dict

    def check_installed_components(self):
        """Checks if external components are installed and updates the external_tools attribute

        Returns: None
        """

        print('\nChecking installed external tools...'
              '\n-------------------------------------\n')
        # check for festival
        self.external_tools['festival'] = self.check_component(path=self.festival_path, tool_name='festival',
                                                               test_args=('--version',),
                                                               answer_str='Festival Speech Synthesis System: 2',
                                                               answer_version=True)
        self.festival_path = self.external_tools['festival']['path']

        # check for text2wave
        self.external_tools['text2wave'] = self.check_component(path=self.text2wave_path, tool_name='text2wave',
                                                                test_args=('-h',),
                                                                answer_str='Convert a textfile to a waveform',
                                                                answer_version=False)
        self.text2wave_path = self.external_tools['text2wave']['path']

        # check for festival_client
        self.external_tools['festival_client'] = self.check_component(path=self.festival_client_path,
                                                                      tool_name='festival_client',
                                                                      test_args=('-h',),
                                                                      answer_str='Access to festival server process',
                                                                      answer_version=False)
        self.festival_client_path = self.external_tools['festival_client']['path']

        # check for SoX
        self.external_tools['sox'] = self.check_component(path=self.sox_path, tool_name='sox', test_args=('--version',),
                                                          answer_str='SoX', answer_version=True)
        self.sox_path = self.external_tools['sox']['path']

        # check for festival voices
        if self.external_tools['festival']['installed']:
            print('Checking installed festival voices...', end=' ')
            self.installed_festival_voices = self.get_festvial_voices()
        else:
            self.installed_festival_voices = []

        # check if configure speaker's voices are okay
        if self.external_tools['festival']['installed']:
            print('\nChecking configured voices...', end=' ')
            invalid_voices = self.check_voices()
            if len(invalid_voices) > 0:
                print('Found {} invalid voice(s).'.format(len(invalid_voices)))
            else:
                print('All configured voices okay.')

    def _render_audio(self, voice, text, filename, normalize=False):
        """Renders a line of text for a given voice to the defined filename

        Args:
            voice(VoiceConfig): Voice config object
            text(str): Text to render
            filename(pathlib.Path): Filename/path to save the rendered audio to
            normalize(bool): Normalize volume if True
        """
        if self.external_tools['festival']['installed'] and self.external_tools['sox']['installed']:

            voice_name = voice.voice_name
            if voice_name not in self.installed_festival_voices:
                raise ValueError('Voice \'{}\' not found in installed voices.'.format(voice_name))
            pitch = voice.pitch_shift
            tempo = voice.tempo
            volume = voice.volume

            # filenames
            filename_raw = filename.with_suffix('.raw')
            voice_file_name = filename.with_suffix('.scm')

            # create scm file with the voice definition
            with open(str(voice_file_name), 'w') as file:
                file.write('(voice_{})\n'.format(voice_name))   # there must be \n at the end other wise festival_client fails to read the file

            if self.use_festival_server:
                # run festival_client to create the raw audio
                subprocess.run([str(self.festival_client_path), '--server', self.festival_server_name, '--port',
                                str(self.festival_server_port), '--ttw', '--output', str(filename_raw), '--prolog',
                                str(voice_file_name)], input='\"{}\"'.format(text), text=True)
            else:
                # run text2wave to create the "raw" audio file
                subprocess.run([str(self.text2wave_path), '-o', str(filename_raw), '-eval', str(voice_file_name)],
                               input='\"{}\"'.format(text), text=True)

            # post-process with SoX
            if normalize:
                subprocess.run([str(self.sox_path), str(filename_raw), str(filename), 'vol', str(volume),
                                'tempo', str(tempo), 'pitch', str(pitch), 'norm', str(self.norm_level)])
            else:
                subprocess.run([str(self.sox_path), str(filename_raw), str(filename), 'vol', str(volume),
                                'tempo', str(tempo), 'pitch', str(pitch)])

            # remove intermediate files
            filename_raw.unlink()
            voice_file_name.unlink()
        else:
            print('Could not render audio. Check if required tools are installed and paths are configured correctly.')

    def play_audio_test(self, voice, text):
        """Plays a test text for the current voice

        Args:
            voice(VoiceConfig): voice configuration
            text(str): Text for testing
        """

        outfile = pathlib.Path('temp.wav')
        self._render_audio(voice=voice, text=text, filename=outfile, normalize=False)

        # play sound
        subprocess.run([str(self.sox_path), 'temp.wav', '-d'])
        # subprocess.run(['play', 'temp.wav'])

        outfile.unlink()

    def render_audio(self, voice, text, filename, normalize=False):
        """Renders a specific script line (or part of a line) into an audio file

        Args:
            voice(str): Name of speaker
            text(str): Text to render
            filename(pathlib.Path): Path object
            normalize(bool): If true normalize the sound level
        """

        voice_config = self.voices[voice]

        self._render_audio(voice=voice_config, text=text, filename=filename, normalize=normalize)

    def create_voices_dict(self):
        """Create a dictionary with all voices"""
        voices_dict = {}

        for name in self.voices.keys():
            voices_dict[name] = self.voices[name].create_voice_dict()

        return voices_dict

    def read_voices_dict(self, voices_dict):
        """Fills voices attribute dict with VoiceConfig objects defined by values from a dictionary

        Args:
            voices_dict(dict): Dictionary with key for each speaker name. Each speaker key holds another dictionary with
                               voice parameters with following keys:
                               - 'voice_name'(str): Festival voice name
                               - 'user_pitch_shift'(int): Pitch shift offset
                               - 'user_tempo'(float): Tempo factor
                               - 'user_volume'(float): Volume factor
        """

        for name in voices_dict.keys():
            voice_name = voices_dict[name]['voice_name']
            pitch = voices_dict[name]['user_pitch_shift']
            tempo = voices_dict[name]['user_tempo']
            vol = voices_dict[name]['user_volume']
            self.voices[name] = VoiceConfig(voice_name=voice_name, pitch_shift=pitch, tempo=tempo, volume=vol)

    def export_voices(self, filename):
        """Exports all voices to a json file"""

        export_dict = self.create_voices_dict()

        json_data = json.dumps(export_dict, indent=4)

        with open(filename, 'w') as file:
            file.write(json_data)

    def import_voices(self, filename):
        """Imports voices from a json file"""

        #TODO: add option to overwrite all voices

        with open(filename, 'r') as file:
            json_data = file.read()

        voices_dict = json.loads(json_data)

        self.read_voices_dict(voices_dict)
