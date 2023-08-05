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
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import copy
import timeit
import warnings
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

    return response


class ProjectManager:

    """Manager for a dramaTTS session"""

    def __init__(self, script_parser, audio_renderer, output_folder=None):
        
        """Initializes the projoect manager
        
        Args:
            script_parser(ScriptParser):
            audio_renderer(AudioRenderer):
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

        self.start_scene = 1
        self.end_scene = None

        self.preferences = None
        
        self.preferences_path = None
        
        self.import_speakers = False
        self.import_speakers_file = None
        self.narrator = VoiceConfig()
        self.default_speaker = MaleVoice()

        self.import_substitutions = False
        self.import_substitutions_file = None

        self.load_preferences()
        self.audio_renderer.check_installed_components()

        if self.import_speakers:
            self.audio_renderer.import_voices(self.import_speakers_file)

        if self.import_substitutions:
            self.script_parser.import_substitutions(self.import_substitutions_file)

    @property
    def default_config_path(self):
        """Returns the default config path"""
        return Path(Path.home(), '.dramatts_config.json')

    def create_prefs_dict(self):
        """Creates a dictionary with the preferences settings"""

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
                'import_speakers': self.import_speakers,
                'import_speakers_file': self.import_speakers_file,
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
                'import_substitutions': self.import_substitutions,
                'import_substitutions_file': self.import_substitutions_file
            }
        }

        return prefs

    def process_prefs_dict(self, prefs):
        """Processes the prefs dict - assings to internal variables"""

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

        self.import_speakers = prefs['speaker_options']['import_speakers']
        path_str = prefs['speaker_options']['import_speakers_file']
        self.import_speakers_file = Path(path_str) if path_str else None
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

        self.import_substitutions = prefs['substitutions']['import_substitutions']
        path_str = prefs['substitutions']['import_substitutions_file']
        self.import_substitutions_file = Path(path_str) if path_str else None

    def load_preferences(self, filepath=None):
        """Loads the preferences from a json file

        Args:
            filepath(pathlib.Path): If none the default config file ~/.dramatts_config.json will be assumed
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
            filepath(pathlib.Path): If none the default config file ~/.dramatts_config.json will be assumed
        """
        # get config dict
        config_dict = self.create_prefs_dict()

        if filepath is None:
            filepath = self.default_config_path

        with open(filepath, 'w') as file:
            file.write(json.dumps(config_dict, indent=4, default=str))

        print('Preferences saved to:', filepath)

    def get_scene_no_str(self, scene_no):
        """Returns a string representation of the scene number"""
        return str(scene_no).zfill(self.digits_scene_no)

    def get_line_no_str(self, line_no):
        """Returns a string representation of the line number"""
        return str(line_no).zfill(self.digits_line_no)

    def get_scene_folder_path(self, scene_no):
        """Returns the path object to a scene subfolder"""
        sub_folder = 'scene_{}'.format(self.get_scene_no_str(scene_no))
        abs_sub_folder = pathlib.Path().joinpath(self.output_folder, sub_folder)
        return abs_sub_folder

    def render_line_from_dict(self, line_dict):
        """Renders a line based on the dictionary provided by the script parser

        Args:
            line_dict(dict): An Element of the list returned by ScriptParser.get_filtered_valid_lines
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

        #self.render_line(scene_no=line_dict['scene_no'], line_no=line_dict['scene_line_no'])

        self.audio_renderer.render_audio(voice=speaker, text=text,
                                         filename=full_filename, normalize=self.normalize)

        return line_dict

    def render_line(self, scene_no, line_no):
        """Renders a script line

        Args:
            scene_no(int): Number of scene (1-based)
            line_no(int): Number of line (1-based)

        Returns:
            pathlib.Path: Path to rendered filename
        """

        line = list(self.script_parser.lines.values())[scene_no-1][line_no-1]
        speaker = line[0]
        text = line[1]

        # check if the voice for the speaker is defined - if not use the narrator's voice
        if speaker not in self.audio_renderer.voices.keys():
            speaker = 'Narrator'

        abs_sub_folder = self.get_scene_folder_path(scene_no)

        # create subfolder if it doesn't exist
        if not os.path.isdir(abs_sub_folder):
            os.mkdir(abs_sub_folder)

        filename = 'scene_{}_line_{}.wav'.format(self.get_scene_no_str(scene_no), self.get_line_no_str(line_no))

        full_filename = pathlib.Path().joinpath(abs_sub_folder, filename)

        self.audio_renderer.render_audio(voice=speaker, text=text, filename=full_filename, normalize=self.normalize)

        return full_filename

    def render_scene(self, scene_no): #, speaker=None):
        """Renders a scene

        Args:
            scene_no(int): Number of scene to render (one-based index)
            speaker(str): Speaker name, if only lines for a specific speaker shall be rendered
                          (if None all speakers will be rendered)
        """

        scene_wav_files = []

        scene_key = list(self.script_parser.lines.keys())[scene_no-1]

        scene_text = scene_key

        scene_folder = self.get_scene_folder_path(scene_no)

        # create subfolder if it doesn't exist
        if not os.path.isdir(scene_folder):
            os.mkdir(scene_folder)

        title_filename = 'scene_{}_line_{}.wav'.format(self.get_scene_no_str(scene_no), self.get_line_no_str(0))
        abs_title_filename = pathlib.Path().joinpath(scene_folder, title_filename)

        # render scene title, if not restricted to a single speaker other than narrator.
        if self.speaker_to_render in [None, 'Narrator']:
            self.audio_renderer.render_audio(voice='Narrator', text=scene_text, filename=abs_title_filename,
                                             normalize=self.normalize)
            scene_wav_files.append(abs_title_filename)

        # render lines in scene
        for i, line in enumerate(self.script_parser.lines[scene_key]):
            if self.speaker_to_render is None:
                render_line = True
            else:
                if self.speaker_to_render == line[0]:
                    render_line = True
                else:
                    render_line = False

            if render_line:
                line_file_name = self.render_line(scene_no=scene_no, line_no=i+1)
                scene_wav_files.append(line_file_name)
                print('Line {}/{} of scene {} rendered.'.format(i + 1, len(self.script_parser.lines[scene_key]),
                                                                scene_no))

        # merge sound files to a single file
        scene_filename = pathlib.Path().joinpath(self.output_folder,
                                               'scene_{}.wav'.format(self.get_scene_no_str(scene_no)))
        file_strings = [str(file) for file in scene_wav_files]  # subprocess does not work with WindowsPath
        subprocess.run([str(self.audio_renderer.sox_path), *file_strings, str(scene_filename)])

        return scene_no

    def render_script(self):
        """Renders the complete script into an audio file for each scene
        """

        # check some preconditions before starting to render
        if not self.output_folder.exists():
            print('The output folder {} does not exist. '
                  'Create it first or select another output folder to start the rendering.'.format(self.output_folder))
            return
        if self.script_parser.lines_list is None:
            print('No parsed lines found. Import a project or script first!')
            return
        # TODO: add some more checks, valid voices for selected speakers,
        #  required components: festival_client, text2wave, sox

        scenes = self.script_parser.get_filtered_valid_lines(first_scene=self.start_scene, last_scene=self.end_scene,
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

        lines_total = len(scenes)
        lines_finished = 0
        last_scene = self.start_scene - 1
        # start rendering line after line
        with ThreadPoolExecutor(max_workers=self.audio_renderer.cpu_threads) as executor:
            for line_dict in executor.map(self.render_line_from_dict, scenes):
                lines_finished += 1
                if line_dict['scene_no'] > last_scene:
                    print('Starting to render scene {}'.format(line_dict['scene_no']))
                    last_scene += 1
                print("{}/{} lines finalized.".format(lines_finished, lines_total))

        # combine the files of the individual scenes:
        # This should better be done after all line have rendered, otherwise we will have to check, that all threads
        # rendering lines of a specific scene have finished.
        end_scene = self.end_scene if self.end_scene else self.script_parser.scene_count - 1
        for scene in range(self.start_scene, end_scene + 1):
            scene_folder = Path().joinpath(self.output_folder,
                                           'scene_{}'.format(self.get_scene_no_str(scene)))
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
        """Adds default speaker for character

        Args:
            character_name_list(list): List of character name sorted acc. to their lines spoken
        """
        counter = 0
        for character in self.script_parser.get_lines_per_character().keys():
            if character not in self.audio_renderer.voices.keys():
                self.audio_renderer.voices[character] = copy.deepcopy(self.default_speaker)
                counter += 1

        print('{} characters added to the speaker list.'.format(counter))

    def combine_audio(self, input_path=None, output_path=None):
        """Combines all files in one directory (excluding subdirs)

        Args:
            input_path(pathlib.Path): Folder name of files to combine (defaults to output_folder)
            output_path(pathlib.Path): Filename of combined file (defaults to output_folder + .wav)

        """
        if input_path is None:
            input_path = self.output_folder
        if output_path is None:
            output_path = Path(str(self.output_folder) + '.wav')

        filenames = [folder[2] for folder in os.walk(input_path)][0]
        filenames.sort()
        if filenames:
            filepaths = [Path().joinpath(input_path, filename) for filename in filenames]
            file_strings = [str(file) for file in filepaths]

            subprocess.run([str(self.audio_renderer.sox_path), *file_strings, str(output_path)])

            print('Combined files in folder {} to file {}.'.format(input_path, output_path))
        else:
            warnings.warn('No files in {} found. Please check the input file path.'.format(input_path))

    def normalize_audio(self):
        """Normalizes all audio segments and rebuild file for scene"""
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
        """Creates a dictionary representation of the current project settings"""

        render_options = self.create_prefs_dict()['render_options']
        render_options['start_scene'] = self.start_scene
        render_options['end_scene'] = self.end_scene
        render_options['output_folder'] = str(self.output_folder)

        project = {
            'file_format_version': '1.0',
            'script_lines': self.script_parser.get_filtered_valid_lines(),
            'characters': self.script_parser.characters,
            'substitutions': self.script_parser.substitutions,
            'speakers': self.audio_renderer.create_voices_dict(),
            'render_options': render_options,
        }
        
        return project
    
    def process_project_dict(self, project):
        """Reads a project dict and assigns to internal variables"""
        
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

    def save_project(self, filepath=None):
        """Save the complete project"""

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
        """Loads a project from a file"""

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


class ScriptParser:

    def __init__(self, input_file=None, start_line=0, end_line=None, substitutions=None):

        self.filename = input_file
        self.start_line = start_line
        self.end_line = end_line
        self.text = None
        self.characters = None
        self.lines_list = None

        if substitutions:
            self.substitutions = substitutions
        else:
            self.substitutions = []

    def read_input(self):
        """Reads the input file"""
        with open(self.filename, 'r') as file:
            text = file.readlines()
        print('Read {} lines from: {}'.format(len(text), self.filename))

        self.text = text

    def substiute_text(self, text):
        """Substitutes elements in text (supports regex as defined by python re module)

        Args:
            text(str): Text to check/modify
        """

        for subst in self.substitutions:
            if subst['regex']:
                p = re.compile(subst['search_text'])
                text = p.sub(subst['subst'], text)
            else:
                text = text.replace(subst['search_text'], subst['subst'])

        return text

    def parse_lines(self):
        """Parses lines and identifies line type"""
        print("---------------------------------\n"
              "Starting to parse script lines...\n"
              "---------------------------------\n")

        parsed_lines = []
        usable_line_type = None
        self.characters = ['Narrator']
        # if self.characters is None:
        #     self.characters = ['Narrator']

        for i, line in enumerate(self.text[self.start_line:self.end_line]):

            # substitute some words first...
            line = self.substiute_text(line)

            if line in ['\n', ' \n', ' ']:  # empty line
                parsed_lines.append(
                    {
                        'line_no': i + 1,
                        'line_type': 'empty',
                        'speaker': None,
                        'content': None
                    }
                )
            elif re.match('^[0-9]+\. ', line) is not None:
                print('Found scene in line {}'.format(i))
                last_scene = line.replace('\n', '')
                line_type = 'Scene'
                content = last_scene
                usable_line_type = line_type
                parsed_lines.append(
                    {
                        'line_no': i + 1,
                        'line_type': line_type,
                        'speaker': 'Narrator',
                        'content': content
                    }
                )
            # if the line starts with at least two upper case letters - this is a dialog indicator
            elif re.match('^[A-Z]{2,}', line) is not None:
                # character = line.replace('\n', '')
                line_type = 'DialogIndicator'
                #last_dialog_speaker = character.split(" ")[0]
                last_dialog_speaker = re.match('[A-Z -]*', line).group().strip()
                print('Found dialog indicator for {} in line {}'.format(last_dialog_speaker, i))
                content = line.replace('\n', '')
                usable_line_type = line_type
                if last_dialog_speaker not in self.characters:
                    self.characters.append(last_dialog_speaker)
                parsed_lines.append(
                    {
                        'line_no': i + 1,
                        'line_type': line_type,
                        'speaker': 'Narrator',
                        'content': content
                    }
                )
            # all other lines are either narrative descriptions or dialog content (depending on the preceding line)
            else:
                content = line.replace('\n', '')
                if usable_line_type == 'DialogIndicator':   # this is Dialogue Content
                    line_type = 'DialogContent'
                    speaker = last_dialog_speaker
                    usable_line_type = line_type

                    # check for inline comments in speech
                    comments = re.findall('(\(.*?\))', content)
                    if comments:
                        # print('Found comment(s) in line {}:'.format(i), comments)
                        trail_text = content
                        for comment in comments:
                            lead_text, _, trail_text = trail_text.partition(comment)
                            parsed_lines.append(
                                {
                                    'line_no': i + 1,
                                    'line_type': 'DialogContent',
                                    'speaker': speaker,
                                    'content': lead_text
                                }
                            )
                            parsed_lines.append(
                                {
                                    'line_no': i + 1,
                                    'line_type': 'InlineComment',
                                    'speaker': 'Narrator',
                                    'content': comment
                                }
                            )
                            if comment == comments[-1]:  # after the last comment render the trailing text
                                parsed_lines.append(
                                    {
                                        'line_no': i + 1,
                                        'line_type': 'DialogContent',
                                        'speaker': speaker,
                                        'content': trail_text
                                    }
                                )
                    else:   # no in line comments in line
                        parsed_lines.append(
                            {
                                'line_no': i + 1,
                                'line_type': 'DialogContent',
                                'speaker': speaker,
                                'content': content
                            }
                        )
                else:   # this is narrative desc.
                    line_type = 'NarrativeDesc'
                    speaker = 'Narrator'
                    parsed_lines.append(
                        {
                            'line_no': i + 1,
                            'line_type': line_type,
                            'speaker': speaker,
                            'content': content
                        }
                    )
        self.lines_list = parsed_lines

    def get_characters_from_parsed_lines(self):
        """Gets all characters from parsed lines"""
        characters = []
        for line in self.lines_list:
            if line['speaker'] not in characters:
                characters.append(line['speaker'])

        self.characters = characters

    @property
    def scene_count(self):
        """Returns the number of scenes in the script"""

        if self.lines:
            return len(self.lines.keys())
        else:
            return 0

    @property
    def valid_lines_list(self):
        """Return only non-empty lines"""
        # remove all empty lines

        non_empty = [line for line in self.lines_list if line['line_type'] != 'empty']

        # Convert all UPPER CASE words in Capital Case to avoid festival treating them as abbreviations
        for i, line in enumerate(non_empty):
            matches = re.findall('[A-Z]{2,}', line['content'])
            if matches:
                new_line_content = line['content']
                for match in matches:
                    new_line_content = new_line_content.replace(match, match.capitalize())
                non_empty[i]['content'] = new_line_content

        # add scene numbers and line number in scene
        scene_number = 0
        scene_line_counter = 0
        for line in non_empty:
            if line['line_type'] == 'Scene':
                scene_number += 1
                scene_line_counter = 0
            line['scene_no'] = scene_number
            line['scene_line_no'] = scene_line_counter

            scene_line_counter += 1

        return non_empty

    def get_filtered_valid_lines(self, first_scene=0, last_scene=None, speaker=None):
        """Returns valid lines (including additional keys for the scene number and the line number within
        the scene) with optional filters for speaker and scene numbers"""

        if last_scene is None:
            last_scene = self.scene_count

        lines_filtered = []

        for line in self.valid_lines_list:
            if first_scene <= line['scene_no'] <= last_scene:   # filter for scenes
                if speaker is None or line['speaker'] == speaker:   # filter for speaker
                    lines_filtered.append(line)

        return lines_filtered

    @property
    def lines(self):
        """Creates a structured representation of the parsed lines - a ordered dict for each scene"""

        lines_dict = collections.OrderedDict()
        last_scene = 'Preface'

        for line in self.valid_lines_list:
            if len(lines_dict.keys()) == 0:
                if line['line_type'] != 'Scene':  # lines before first scene - add scene 'Preface'
                    lines_dict['Preface'] = []
                else:
                    lines_dict[line['content']] = []
                    last_scene = line['content']
            else:
                if line['line_type'] == 'Scene':
                    lines_dict[line['content']] = []
                    last_scene = line['content']
                else:
                    lines_dict[last_scene].append([line['speaker'], line['content']])

        return lines_dict

    def get_lines_per_character(self):
        """Counts the lines for each speaker

        Returns:
            dict: key = character name - value = no. of lines
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

    # def export_character_list(self):
    #     """write character list"""
    #     with open('characters.json', 'w') as file:
    #         file.write(json.dumps(self.characters, indent=4))

    def export_parsed_lines(self, filename):
        """Exports the parsed lines"""
        with open(filename, 'w') as file:
            file.write(json.dumps(self.lines_list, indent=4))

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


class AudioRenderer:

    def __init__(self,  voices=None, first_scene=1, cpu_threads=4):

        self.cpu_threads = cpu_threads
        self.norm_level = -3    # normalize level for sound files

        self.counter = 0    # line counter for file naming

        # self.default_speaker = VoiceConfig(voice_name='cmu_us_rms_cg', pitch_shift=100, tempo=1.2, volume=1.0)
        self.scene_offset = first_scene

        self.sox_path = None
        self.festival_path = None
        self.festival_client_path = None
        self.text2wave_path = None

        self.installed_festival_voices = None

        # self.sox_version = None
        # self.festival_version = None

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
        """Returns feedback from command line tool

        Args:
            command_name(str): Name of command to check
            path(pathlib.Path): Path to the executable, if None see below
            cmd_args(tuple): Command line arguments to pass to tool

        Note:
            If path is none the command line tool needs to be added to your PATH (environment variable).
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
        """Returns the installed festival voices"""
        #TODO: add check if the request succeeded
        if os.name == 'posix':
            shell = True
        else:
            shell = False
        # cmd_str = '{} -b \"(print (voice.list))\"'.format(self.festival_path)
        # voice_str = subprocess.check_output(cmd_str, shell=shell).decode()
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
        """Checks the voice parameters for correctness (e.g. voice installed)

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
        """Get path to external executable"""
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
        """Checks an individual external tool

        Args:
            path(pathlib.Path): Path to executable (incl. exectable name)
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
        """Checks if required components are installed

        Returns:
            bool: True if all components are found
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
        """Plays a test text for the current voice"""

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
        """Creates the voices from a dict"""

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
