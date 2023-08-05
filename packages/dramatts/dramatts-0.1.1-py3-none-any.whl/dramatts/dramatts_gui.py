"""
dramatts_gui.py - GUI for dramaTTS
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

from dramatts import name
from dramatts.gui import *
from dramatts.core import *
from dramatts.voices import *
from PyQt5.Qt import QMainWindow, QApplication, QTableWidgetItem, QFileDialog, QColor, QTableWidget, QInputDialog
from PyQt5 import Qt
import sys
from multiprocessing.pool import ThreadPool
from setuptools_scm import get_version
import pkg_resources


class EmittingStream(QtCore.QObject):
    """
    Class EmittingStream and its implementation taken from
    https://stackoverflow.com/questions/8356336/how-to-capture-output-of-pythons-interpreter-and-show-in-a-text-widget
    posted by Ferdinand Beyer (edited 2012/07/22)
    """
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class GUI(QMainWindow, Ui_MainWindow):

    def __init__(self, project_manager, debug=False, version=None):

        """GUI interface for dramaTTS

        Args:
            project_manager(ProjectManager): dramaTTS project manager
        """

        super().__init__()

        self.manager = project_manager
        self.version = version

        self.speaker_index = 0
        self.speaker_name = 'Narrator'

        # intialize UI
        self.setupUi(self)
        self.update_speaker_list()
        self.update_subst_table()
        self.get_tools_versions()

        # udpate program version in name str
        progname_str = 'dramaTTS v{}'.format(self.version)
        self.setWindowTitle(progname_str)
        license_text = self.lblLicense.text()
        license_text = license_text.replace('dramaTTS', progname_str, 1)
        self.lblLicense.setText(license_text)

        self.process = None

        self.__pool__ = ThreadPool()

        # set table header label
        self.tblSubst.setHorizontalHeaderLabels(['Search string / Pattern', 'Substitution', 'Regex?', 'Comment'])
        self.tblLineProps.setHorizontalHeaderLabels(['Parameter', 'Value'])
        self.tblCharacters.setHorizontalHeaderLabels(['Role name', 'Line count'])
        self.tblSpeakerParameters.setHorizontalHeaderLabels(['Parameter', 'Value'])

        # update preferences
        self.display_preferences()

        # update render settings
        self.update_render_settings()

        # UI events
        self.lvSpeakers.itemSelectionChanged.connect(self.update_speaker_param_table)
        self.listScriptLines.itemSelectionChanged.connect(self.update_parse_line_props_table)

        self.butPlayTest.clicked.connect(self.play_test_phrase)
        self.butUpdateSpeaker.clicked.connect(self.update_speaker_parameters)
        self.butExportSpeakers.clicked.connect(self.export_speakers)
        self.butImportSpeakers.clicked.connect(self.import_speakers)
        self.butImportScript.clicked.connect(self.import_script)
        self.butAddCharacters.clicked.connect(self.add_speakers_for_characters)
        self.butSetOutputFolder.clicked.connect(self.define_outputfolder)
        self.butRender.clicked.connect(self.start_render)
        self.butExportParsedLines.clicked.connect(self.export_parsed_lines)
        self.butImportParsed.clicked.connect(self.import_parsed_lines)
        self.butUpdateLineProps.clicked.connect(self.update_line_parameters)
        self.butNormailzeAudio.clicked.connect(self.normalize_audio)
        self.butCombineAudio.clicked.connect(self.combine_audio)
        self.butSetSoXPath.clicked.connect(self.set_sox_path)
        self.butSelectFestivalPath.clicked.connect(self.set_festival_path)
        self.butSetText2wavePath.clicked.connect(self.set_text2wave_path)
        self.butSetFestivalClientPath.clicked.connect(self.set_festival_client_path)
        self.butRemoveSubst.clicked.connect(self.remove_subst_entry)
        self.butAddSubst.clicked.connect(self.add_subst_entry)
        self.butUpdateSubst.clicked.connect(self.update_subst_entries)
        self.butImportSubst.clicked.connect(self.import_substitutions)
        self.butExportSubst.clicked.connect(self.export_substitutions)
        self.butAddSpeaker.clicked.connect(self.add_speaker)
        self.butRemoveSpeaker.clicked.connect(self.remove_speaker)
        self.butSavePrefs.clicked.connect(self.save_preferences)
        self.butExportPrefs.clicked.connect(self.export_preferences)
        self.butImportPrefs.clicked.connect(self.import_preferences)
        self.butNewProject.clicked.connect(self.new_project)
        self.butOpenProject.clicked.connect(self.load_project)
        self.butSaveProject.clicked.connect(self.save_project)
        self.butSaveProjectAs.clicked.connect(self.save_project_as)

        self.butSetDefaultSpeakersPath.clicked.connect(self.set_default_speakers_path)
        self.butSetDefaultSubstPath.clicked.connect(self.set_default_subst_path)

        self.chbLimitSpeaker.clicked.connect(self.toggle_speaker_select)

        self.rbutPlain.clicked.connect(self.update_parsed_lines_list)
        self.rbutParsed.clicked.connect(self.update_parsed_lines_list)

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        if not debug:
            sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        self.check_external_tools()

        self.show()

    # -------------------------------------
    # Generic GUI methods
    # -------------------------------------

    @staticmethod
    def get_selected_index_from_list(lv_widget):
        """Returns the selected line index from a list box widget"""
        line_index = lv_widget.selectedIndexes()
        if line_index in [None, []]:
            line_index = 0
        else:
            line_index = line_index[0].row()
        return line_index

    @staticmethod
    def fill_table(table_widget, record_dict):
        """Clears and fills a with a new record dictionary"""

        # clear
        table_widget.clearContents()
        for i in range(table_widget.rowCount()):
            table_widget.removeRow(0)

        for i, key in enumerate(record_dict.keys()):
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(str(record_dict[key]))
            table_widget.insertRow(i)
            table_widget.setItem(i, 0, key_item)
            table_widget.setItem(i, 1, value_item)

    @staticmethod
    def read_2column_table(table_widget):
        """Reads a parameter value table and places the data into a dictionary"""
        table_dict = {}
        for row in range(table_widget.rowCount()):
            key = table_widget.item(row, 0).text()
            value = table_widget.item(row, 1).text()
            table_dict[key] = value

        # print(table_dict)
        return table_dict

    @staticmethod
    def remove_table_row(table_widget, source_list):
        """Removes the currently selected table row and the corresponding entry in the source list

        Args:
            table_widget(QTableWidget)
            source_list(list)
        """
        if table_widget.rowCount() > 0:
            index = table_widget.currentIndex()
            table_widget.removeRow(index.row())

            source_list.pop(index.row())

            if index.row() > 0:
                table_widget.selectRow(index.row() - 1)
            else:
                table_widget.selectRow(index.row())

            print(index.row())

    @staticmethod
    def add_table_row(table_widget, init_value_list=None):
        """Adds a table item at the current row selection and return the row index

        Args:
            table_widget(QTableWidget)
            init_value_list(list): An optional list with initial values for each table column
        """

        if init_value_list:
            if len(init_value_list) != table_widget.columnCount():
                warnings.warn('Number of init. values must match column number!')
                return

        index = table_widget.currentIndex().row()
        print(index)
        if index < 0:
            index = 0
        table_widget.insertRow(index)

        for i in range(table_widget.columnCount()):
            if init_value_list:
                value = init_value_list[i]
            else:
                value = None
            table_widget.setItem(index, i, QTableWidgetItem(value))

        table_widget.selectRow(index)
        return index

    @staticmethod
    def read_general_table(table_widget, data_types=None, dict_keys=None):
        """Reads the table content and returns a list (rows) of lists (column)
        Args:
            table_widget(QTableWidget)
            data_types(list): List of data type for each column
            dict_keys(list): Dictionary keys for each column. If provided the column values will be stored in a dict
                             if not in a list

        Note:
            All values are strings.
        """
        if data_types:
            if len(data_types) != table_widget.columnCount():
                warnings.warn('Number of data types must match column number! Data was not updated')
                return
        if dict_keys:
            if len(dict_keys) != table_widget.columnCount():
                warnings.warn('Number of dict keys must match column number! Data was not updated')
                return

        table_values = []
        for row in range(table_widget.rowCount()):
            if dict_keys:
                row_values = {}
            else:
                row_values = []
            for column in range(table_widget.columnCount()):
                value = table_widget.item(row, column).text()
                if data_types:
                    if data_types[column] == bool:
                        if value == 'True':
                            value = True
                        else:
                            value = False
                    else:
                        value = data_types[column](value)
                if dict_keys:
                    row_values[dict_keys[column]] = value
                else:
                    row_values.append(value)
            table_values.append(row_values)

        return table_values

    # -----------------------------------
    # specific GUI methods
    # -----------------------------------

    def refresh_all_guis(self):
        """Refreshes all GUI elements, which store project data"""

        # defocus all table & list widget indices
        self.tblCharacters.setCurrentCell(-1, -1)
        self.tblLineProps.setCurrentCell(-1, -1)
        self.tblSpeakerParameters.setCurrentCell(-1, -1)
        self.tblSubst.setCurrentCell(-1, -1)
        self.lvSpeakers.setCurrentRow(-1)
        self.listScriptLines.setCurrentRow(-1)

        self.spinStartLine.setValue(self.manager.script_parser.start_line)
        if self.manager.script_parser.end_line:
            self.spinEndLine.setValue(self.manager.script_parser.end_line)
        else:
            self.spinEndLine.setValue(0)
        self.update_parsed_lines_list()
        self.update_parse_line_props_table()
        self.update_speaker_list()
        self.update_subst_table()
        self.update_render_settings()

    def save_project(self):
        """Saves the current project"""
        if self.manager.project_filepath is None:
            filename, _ = QFileDialog().getSaveFileName()
        else:
            filename = self.manager.project_filepath

        if filename:
            self.manager.save_project(filename)
            self.manager.project_filepath = filename

    def save_project_as(self):
        """Saves the project to new file name"""

        filename, _ = QFileDialog().getSaveFileName()

        if filename:
            self.manager.save_project(filename)

    def load_project(self):
        """Loads a project from a file"""

        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.load_project(filename)
            self.refresh_all_guis()

    def new_project(self):
        """Create a new project"""

        new_parser = ScriptParser()
        new_renderer = AudioRenderer()
        new_manager = ProjectManager(script_parser=new_parser, audio_renderer=new_renderer)

        self.manager = new_manager
        self.refresh_all_guis()
        print('New project created.')

    def save_preferences(self):
        """Saves the preferences (to the default config file)"""
        self.read_pref_values()
        self.manager.save_preferences()

    def export_preferences(self):
        """Exports the preferences to a specific file"""
        filename, _ = QFileDialog().getSaveFileName()

        if filename:
            self.read_pref_values()
            self.manager.save_preferences(filename)

    def import_preferences(self):
        """Imports the preferences from a file"""

        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.load_preferences(filename)
            self.display_preferences()

    def update_render_settings(self):
        """Updates the UI elements for the render settings"""

        self.leOutputFolder.setText(str(self.manager.output_folder))
        self.chbCombine.setChecked(self.manager.combine)
        self.spinSceneOffset.setValue(self.manager.start_scene)
        if self.manager.end_scene:
            self.spinLastScene.setValue(self.manager.end_scene)
        else:
            self.spinLastScene.setValue(0)
        # render only one speaker
        if self.manager.speaker_to_render:
            self.chbLimitSpeaker.setChecked(True)
        else:
            self.chbLimitSpeaker.setChecked(False)
        self.cmbSpeakerSelect.setCurrentText(self.manager.speaker_to_render)
        self.chbNormalizeAudio.setChecked(self.manager.normalize)
        self.spindBLevel.setValue(self.manager.audio_renderer.norm_level)
        self.spinCPUthreads.setValue(self.manager.audio_renderer.cpu_threads)
        self.chbUseServer.setChecked(self.manager.audio_renderer.use_festival_server)
        self.leFestivalServerName.setText(self.manager.audio_renderer.festival_server_name)
        self.leFestivalServerPort.setText(str(self.manager.audio_renderer.festival_server_port))


    def display_preferences(self):
        """Updates the GUI with the loaded preferences"""

        self.leFestivalPath.setText(str(self.manager.audio_renderer.festival_path))
        self.leText2WavePath.setText(str(self.manager.audio_renderer.text2wave_path))
        self.leFestivalClientPath.setText(str(self.manager.audio_renderer.festival_client_path))
        self.leSoxPath.setText(str(self.manager.audio_renderer.sox_path))

        self.chbNormalizeAudioDefault.setChecked(self.manager.normalize)
        self.spinDBlevelDefault.setValue(self.manager.audio_renderer.norm_level)
        self.spinCPUThreadsDefault.setValue(self.manager.audio_renderer.cpu_threads)
        self.chbUseFesitvalServerDefault.setChecked(self.manager.audio_renderer.use_festival_server)
        self.chbCombineAudioDefault.setChecked(self.manager.combine)

        self.chbImportDefaultSpeakers.setChecked(self.manager.import_speakers)
        self.leDefaultSpeakerFile.setText(str(self.manager.import_speakers_file))
        self.cmbDefaultNarratorVoice.addItems(self.manager.audio_renderer.installed_festival_voices)
        self.cmbDefaultNarratorVoice.setCurrentText(self.manager.narrator.voice_name)
        self.spinDefaultNarratorPitch.setValue(self.manager.narrator.pitch_shift)
        self.spinDefaultNarratorTempo.setValue(self.manager.narrator.tempo)
        self.spinDefaultNarratorVolume.setValue(self.manager.narrator.volume)
        self.cmbDefaultSpeakerVoice.addItems(self.manager.audio_renderer.installed_festival_voices)
        self.cmbDefaultSpeakerVoice.setCurrentText(self.manager.default_speaker.voice_name)
        self.spinPitchDefaultSpeaker.setValue(self.manager.default_speaker.pitch_shift)
        self.spinTempoDefaultSpeaker.setValue(self.manager.default_speaker.tempo)
        self.spinVolumeDefaultSpeaker.setValue(self.manager.default_speaker.volume)
        
        self.chbImportDefaultSubst.setChecked(self.manager.import_substitutions)
        self.leDefaultSubstFile.setText(str(self.manager.import_substitutions_file))

    def read_pref_values(self):
        """Reads the GUI values and assigns to internal variables"""

        path_str = self.leFestivalPath.text()
        self.manager.audio_renderer.festival_path = Path(path_str) if path_str else None
        path_str = self.leText2WavePath.text()
        self.manager.audio_renderer.text2wave_path = Path(path_str) if path_str else None
        path_str = self.leFestivalClientPath.text()
        self.manager.audio_renderer.festival_client_path = Path(path_str) if path_str else None
        path_str = self.leSoxPath.text()
        self.manager.audio_renderer.sox_path = Path(path_str) if path_str else None

        self.manager.normalize = self.chbNormalizeAudioDefault.isChecked()
        self.manager.audio_renderer.norm_level = self.spinDBlevelDefault.value()
        self.manager.audio_renderer.cpu_threads = self.spinCPUThreadsDefault.value()
        self.manager.audio_renderer.use_festival_server = self.chbUseFesitvalServerDefault.isChecked()
        self.manager.combine = self.chbCombineAudioDefault.isChecked()

        self.manager.import_speakers = self.chbImportDefaultSpeakers.isChecked()
        path_str = self.leDefaultSpeakerFile.text()
        self.manager.import_speakers_file = Path(path_str) if path_str else None

        voice = self.cmbDefaultNarratorVoice.currentText()
        pitch = self.spinDefaultNarratorPitch.value()
        tempo = self.spinDefaultNarratorTempo.value()
        volume = self.spinDefaultNarratorVolume.value()
        self.manager.narrator = VoiceConfig(voice_name=voice, pitch_shift=pitch, tempo=tempo, volume=volume)
        voice = self.cmbDefaultSpeakerVoice.currentText()
        pitch = self.spinPitchDefaultSpeaker.value()
        tempo = self.spinTempoDefaultSpeaker.value()
        volume = self.spinVolumeDefaultSpeaker.value()
        self.manager.default_speaker = VoiceConfig(voice_name=voice, pitch_shift=pitch, tempo=tempo, volume=volume)

        self.manager.import_substitutions = self.chbImportDefaultSubst.isChecked()
        path_str = self.leDefaultSubstFile.text()
        self.manager.import_substitutions_file = Path(path_str) if path_str else None

    def check_external_tools(self):
        """Checks the external tools"""
        self.manager.audio_renderer.check_installed_components()

    def get_tools_versions(self):
        """Checks for the required installed tool versions"""
        self.manager.audio_renderer.check_installed_components()
        festival_version = self.manager.audio_renderer.external_tools['festival']['version']
        sox_version = self.manager.audio_renderer.external_tools['sox']['version']

        if festival_version:
            self.leFestivalVersion.setText(festival_version)
            self.leFestivalVersion.setStyleSheet("color: black;  background-color: white")
        else:
            self.leFestivalVersion.setText('Could not find valid festival version')
            self.leFestivalVersion.setStyleSheet("color: red;  background-color: white")

        if sox_version:
            self.leSoXversion.setText(sox_version)
            self.leSoXversion.setStyleSheet("color: black;  background-color: white")
        else:
            self.leSoXversion.setText('Could not find valid sox version')
            self.leSoXversion.setStyleSheet("color: red;  background-color: white")

        festival_installed = self.manager.audio_renderer.external_tools['festival']['installed']
        sox_installed = self.manager.audio_renderer.external_tools['sox']['installed']
        text2wave_installed = self.manager.audio_renderer.external_tools['text2wave']['installed']
        festival_client_installed = self.manager.audio_renderer.external_tools['festival_client']['installed']

        if festival_installed and sox_installed and text2wave_installed:
            self.butRender.setEnabled(True)
            self.butNormailzeAudio.setEnabled(True)
            self.butCombineAudio.setEnabled(True)
        elif sox_installed:
            self.butRender.setEnabled(False)
            self.butNormailzeAudio.setEnabled(True)
            self.butCombineAudio.setEnabled(True)
        else:
            self.butRender.setEnabled(False)
            self.butNormailzeAudio.setEnabled(False)
            self.butCombineAudio.setEnabled(False)

    def update_parsed_lines_list(self):
        """Updates the parsed lines and characters list"""
        self.listScriptLines.clear()
        self.tblCharacters.clearContents()
        self.cmbSpeakerSelect.clear()

        if self.manager.script_parser.lines_list:
            if self.rbutParsed.isChecked():
                line_contents = [line['speaker'] + ": " + line['content']
                                 for line in self.manager.script_parser.valid_lines_list]
                list_source = self.manager.script_parser.valid_lines_list
            else:   # self.rbutPlain.isEnabled():
                line_contents = [line['content'] for line in self.manager.script_parser.lines_list]
                list_source = self.manager.script_parser.lines_list
            self.listScriptLines.addItems(line_contents)

            # define colors to highlight line types
            for i, line in enumerate(list_source):
                if line['line_type'] == 'Scene':
                    self.listScriptLines.item(i).setForeground(QColor('red'))
                elif line['line_type'] == 'DialogContent':
                    self.listScriptLines.item(i).setForeground(QColor('blue'))
                elif line['line_type'] == 'DialogIndicator':
                    self.listScriptLines.item(i).setForeground(QColor('green'))
                elif line['line_type'] == 'InlineComment':
                    self.listScriptLines.item(i).setForeground(QColor('darkviolet'))
                else:   # narrative desc.
                    self.listScriptLines.item(i).setForeground(QColor('black'))

            self.fill_table(self.tblCharacters, self.manager.script_parser.get_lines_per_character())

            self.cmbSpeakerSelect.addItems(self.manager.script_parser.characters)

    def toggle_speaker_select(self):
        """Toggles the speaker limit select combobox on/off"""
        if self.chbLimitSpeaker.isChecked():
            self.cmbSpeakerSelect.setEnabled(True)
        else:
            self.cmbSpeakerSelect.setEnabled(False)

    def update_subst_table(self):
        """Udpates the table of substitutions"""
        # clear
        self.tblSubst.clearContents()
        for i in range(self.tblSubst.rowCount()):
            self.tblSubst.removeRow(0)

        for i, subst in enumerate(self.manager.script_parser.substitutions):
            search_text = QTableWidgetItem(subst['search_text'])
            subst_text = QTableWidgetItem(subst['subst'])
            if subst['regex']:
                regex = QTableWidgetItem('True')
            else:
                regex = QTableWidgetItem('False')
            comment = QTableWidgetItem(subst['comment'])

            self.tblSubst.insertRow(i)
            self.tblSubst.setItem(i, 0, search_text)
            self.tblSubst.setItem(i, 1, subst_text)
            self.tblSubst.setItem(i, 2, regex)
            self.tblSubst.setItem(i, 3, comment)

    def remove_subst_entry(self):
        """Remove a subst. from the list"""

        self.remove_table_row(self.tblSubst, self.manager.script_parser.substitutions)
        # self.update_subst_table()

    def add_subst_entry(self):
        """Add a subst. to the list"""
        index = self.add_table_row(self.tblSubst)
        self.manager.script_parser.substitutions.insert(index, {
            'search_text': '', 'subst': '', 'regex': False, 'comment': None
        })

    def update_subst_entries(self):
        """Updates the subst. list with the current table values"""
        table_values = self.read_general_table(self.tblSubst, data_types=[str, str, bool, str],
                                               dict_keys=['search_text', 'subst', 'regex', 'comment'])
        if table_values:
            self.manager.script_parser.substitutions = table_values
            print('Substitutions have been updated')
        else:
            print('Could not update substitutions!')
        self.update_subst_table()

    def add_speakers_for_characters(self):
        """Adds default speaker for characters without speaker"""

        self.manager.add_speakers_for_characters()
        self.manager.audio_renderer.check_voices()
        self.update_speaker_list()
        # self.update_speaker_table()

    def add_speaker(self):
        """Adds a new speaker to the speaker list"""
        speaker_name, _ = QInputDialog().getText(self, 'Add speaker', 'Speaker name:')
        if speaker_name:
            speaker_name = speaker_name.upper()
            if speaker_name in self.manager.audio_renderer.voices.keys():
                print('Speaker {} already in speaker list. '
                      'Please use a different name or remove the existing speaker first.'.format(speaker_name))
            else:
                self.manager.audio_renderer.voices[speaker_name] = copy.deepcopy(
                    self.manager.audio_renderer.default_speaker)
                self.manager.audio_renderer.check_voices()
                self.update_speaker_list()
                print('Speaker {} has been added to the speaker list.'.format(speaker_name))

    def remove_speaker(self):
        """Removes a speaker from the speaker list"""
        row = self.lvSpeakers.currentRow()
        speaker_name = self.lvSpeakers.currentItem().text()
        if speaker_name == 'Narrator':  # it doesn't make sense to delete the Narrator
            print('The narrator cannot be deleted.')
        else:
            del self.manager.audio_renderer.voices[speaker_name]
            self.manager.audio_renderer.check_voices()
            if row > 0:
                row -= 1
            else:
                row = 0
            self.lvSpeakers.setCurrentRow(row)
            self.update_speaker_list()
            self.update_speaker_param_table()
            print('Speaker {} has been removed'.format(speaker_name))

    def update_speaker_list(self):
        """Updates the speaker list"""
        last_idx = self.lvSpeakers.currentRow()
        self.lvSpeakers.clear()
        speaker_names = self.manager.audio_renderer.voices.keys()

        # self.manager.audio_renderer.check_voices()
        self.lvSpeakers.addItems(speaker_names)
        self.lvSpeakers.setCurrentRow(last_idx)

        for invalid_voice in self.manager.audio_renderer.invalid_voices:
            invalid_item = self.lvSpeakers.item(invalid_voice['index'])
            invalid_item.setForeground(QColor('red'))

        # update the combo box with all characters
        # self.cmbSpeakerSelect.clear()
        # self.cmbSpeakerSelect.addItems(speaker_names)

    def get_speaker_params(self):
        """Fetches the speaker params from a the parameter table"""
        speaker_params = self.read_2column_table(self.tblSpeakerParameters)

        try:
            voice = speaker_params['voice_name']
            pitch = int(float(speaker_params['user_pitch_shift']))
            tempo = float(speaker_params['user_tempo'])
            vol = float(speaker_params['user_volume'])
            return [voice, pitch, tempo, vol]
        except ValueError:
            print('Failed to read speaker parameters from table!')
            return None

    def update_speaker_parameters(self):
        """reads the speaker params from table and updates the speaker"""
        params = self.get_speaker_params()
        speaker_name = self.lvSpeakers.currentItem().text()

        if params:
            self.manager.audio_renderer.voices[speaker_name].update_parameters(*params)
            print('Speaker parameters updated.')
        else:
            print('Could not update speaker parameters!')

        self.manager.audio_renderer.check_voices()

        self.update_speaker_param_table()   # make sure cast above are reflected in the table + color highlighting
        self.update_speaker_list()  # in case a change renders a speak invalid, the color in the list should change

        # should capture this, if speakers with fixed festival voice exist...
        # try:
        #     self.manager.audio_renderer.voices[self.speaker_name].voice_name = voice
        # except AttributeError:
        #     pass

    def update_speaker_param_table(self):
        """Udpates the info in the speaker table"""

        # speaker_name = self.lvSpeakers.selectedItems()[0].text()
        speaker_idx = self.lvSpeakers.currentRow()

        # print('Speaker row: {}, speaker name: {}'.format(speaker_idx, speaker_name))

        if speaker_idx < 0:
            self.tblSpeakerParameters.clearContents()
        else:
            speaker_name = list(self.manager.audio_renderer.voices.keys())[speaker_idx]

            # speaker_name = list(self.manager.audio_renderer.voices.keys())[self.speaker_index]
            # self.speaker_name = speaker_name

            voice_dict = self.manager.audio_renderer.voices[speaker_name].create_voice_dict()

            self.fill_table(self.tblSpeakerParameters, voice_dict)

            for invalid_voice in self.manager.audio_renderer.invalid_voices:
                if invalid_voice['name'] == speaker_name:
                    for param in invalid_voice['params']:
                        invalid_item = self.tblSpeakerParameters.findItems(param, Qt.Qt.MatchExactly)[0]
                        row = invalid_item.row()
                        self.tblSpeakerParameters.item(row, 0).setForeground(QColor('red'))
                        self.tblSpeakerParameters.item(row, 1).setForeground(QColor('red'))

    def update_parse_line_props_table(self):
        """Updates the table for the parsed lines"""
        line_index = self.get_selected_index_from_list(self.listScriptLines)

        if self.manager.script_parser.lines_list:
            if self.rbutParsed.isChecked():
                line_props = self.manager.script_parser.valid_lines_list[line_index]
            else:
                line_props = self.manager.script_parser.lines_list[line_index]

            self.fill_table(self.tblLineProps, line_props)
        else:
            self.tblLineProps.clearContents()

    def update_line_parameters(self):
        """reads the speaker params from table and updates the speaker"""

        line_params = self.read_2column_table(self.tblLineProps)

        selected_line = self.get_selected_index_from_list(self.listScriptLines)

        if self.rbutParsed.isChecked():
            print("Lines can only be updated in \"Original Text\" mode")
            return
        else:
            self.manager.script_parser.lines_list[selected_line] = line_params
            print('Parameters for line {} have been updated.'.format(selected_line))

        self.update_parsed_lines_list()

    def play_test_phrase(self):
        """Plays the test phrase for the currently seleted speaker"""
        params = self.get_speaker_params()

        if params and params[0] in self.manager.audio_renderer.installed_festival_voices:
            temp_speaker = VoiceConfig(*params)

            text = self.txtTestPhrase.toPlainText()
            #print(self.speaker_name)
            print('Rendering audio for test phrase...')
            self.__pool__.apply_async(self.manager.audio_renderer.play_audio_test, args=(temp_speaker, text))
            # self.manager.audio_renderer.play_audio_test(temp_speaker, text)
        else:
            print('Failed to play audio! Please check speaker parameters.')

    def set_sox_path(self):
        """Set path for SoX"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.audio_renderer.sox_path = pathlib.Path(filename)
            self.leSoxPath.setText(filename)
            self.get_tools_versions()

    def set_festival_path(self):
        """Set path for festival"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.audio_renderer.festival_path = pathlib.Path(filename)
            self.leFestivalPath.setText(filename)
            self.get_tools_versions()

    def set_festival_client_path(self):
        """Set path for festival_client"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.audio_renderer.festival_client_path = pathlib.Path(filename)
            self.leFestivalClientPath.setText(filename)
            self.get_tools_versions()

    def set_text2wave_path(self):
        """Set path for festival"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.audio_renderer.text2wave_path = pathlib.Path(filename)
            self.leText2WavePath.setText(filename)
            self.get_tools_versions()

    def set_default_speakers_path(self):
        """Set path for default speakers"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.import_speakers_file = pathlib.Path(filename)
            self.leDefaultSpeakerFile.setText(filename)

    def set_default_subst_path(self):
        """Set path for defaulf substitutions"""
        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.import_substitutions_file = pathlib.Path(filename)
            self.leDefaultSubstFile.setText(filename)

    def export_speakers(self):
        """Exports the speakers to json"""

        filename, _ = QFileDialog().getSaveFileName()

        if filename:
            if '.json' not in filename:
                filename += '.json'

            self.manager.audio_renderer.export_voices(filename=filename)

        print('Exported speakers to {}'.format(filename))

    def import_speakers(self):
        """Import speakers from a json file"""

        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.audio_renderer.import_voices(filename=filename)
            self.update_speaker_list()

        print('Imported voices from {}'.format(filename))

    def import_script(self):
        """Imports a script file"""

        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.script_parser.filename = filename

            self.manager.script_parser.read_input()
            self.parse_script()

    def parse_script(self):
        """Parses the script"""

        self.manager.script_parser.start_line = self.spinStartLine.value() - 1
        end_line = self.spinEndLine.value()
        if end_line == 0:
            self.manager.script_parser.end_line = None
        else:
            self.manager.script_parser.end_line = end_line - 1

        self.manager.script_parser.parse_lines()
        self.update_parsed_lines_list()

    def import_parsed_lines(self):
        """Imports parsed lines from a file"""

        filename, _ = QFileDialog().getOpenFileName(initialFilter='.json')

        if filename:
            self.manager.script_parser.import_parsed_lines(filename=filename)
            self.manager.script_parser.get_characters_from_parsed_lines()
            self.manager.script_parser.get_lines_per_character()
            self.update_parsed_lines_list()

    def export_parsed_lines(self):
        """Exports the parsed lines to a file"""

        filename, _ = QFileDialog().getSaveFileName()

        if filename:
            if '.json' not in filename:
                filename += '.json'

            self.manager.script_parser.export_parsed_lines(filename=filename)

    def export_substitutions(self):
        """Exports the substitutions"""

        filename, _ = QFileDialog().getSaveFileName()

        if filename:
            if '.json' not in filename:
                filename += '.json'

            self.manager.script_parser.export_substitutions(filename=filename)

    def import_substitutions(self):
        """Imports the substitutions"""

        filename, _ = QFileDialog().getOpenFileName()

        if filename:
            self.manager.script_parser.import_substitutions(filename=filename)
            self.update_subst_table()

    def define_outputfolder(self):
        """Selects a folder for the output"""
        output_folder = QFileDialog().getExistingDirectory()

        self.manager.output_folder = output_folder
        self.leOutputFolder.setText(output_folder)
        self.leOutputFolder.setEnabled(False)

    def start_render(self):
        """Starts the rendering of the audio files"""

        self.manager.audio_renderer.use_festival_server = self.chbUseServer.isChecked()

        first_scene = self.spinSceneOffset.value()
        last_scene = self.spinLastScene.value()
        if last_scene == 0:
            last_scene = None

        if self.chbLimitSpeaker.isChecked():
            speaker = self.cmbSpeakerSelect.currentText()
        else:
            speaker = None

        if self.chbNormalizeAudio.isChecked():
            self.manager.normalize = True
            self.manager.audio_renderer.norm_level = self.spindBLevel.value()
        else:
            self.manager.normalize = False

        self.manager.audio_renderer.scene_offset = self.spinSceneOffset.value()
        self.manager.audio_renderer.cpu_threads = self.spinCPUthreads.value()
        self.manager.audio_renderer.festival_server_name = self.leFestivalServerName.text()
        self.manager.audio_renderer.festival_server_port = self.leFestivalServerPort.text()
        self.manager.start_scene = first_scene
        self.manager.end_scene = last_scene
        self.manager.speaker_to_render = speaker

        # sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.__pool__.apply_async(self.manager.render_script)

    def normalize_audio(self):
        """Normalizes the audio files"""
        self.manager.audio_renderer.norm_level = self.spindBLevel.value()
        self.manager.normalize_audio()

    def combine_audio(self):
        """Combines all scene files into one file"""
        self.manager.combine_audio()

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.txtLog.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.txtLog.setTextCursor(cursor)
        self.txtLog.ensureCursorVisible()


if __name__ == '__main__':

    # get version string
    try:
        version = get_version(root='..', relative_to=__file__)  # version from source code repo
    except LookupError:
        version = pkg_resources.get_distribution(name).version  # if this is an installed package

    # default substitutions
    text_subst = [
        {'search_text': '"', 'subst': '', 'regex': False, 'comment': 'Causes string parsing errors'},
        {'search_text': '(con\'t)', 'subst': '(continued)', 'regex': False, 'comment': None},
        {'search_text': '(Con\'t)', 'subst': '(continued)', 'regex': False, 'comment': None},
        {'search_text': '(cont.)', 'subst': '(continued)', 'regex': False, 'comment': None},
        {'search_text': '(Cont.)', 'subst': '(continued)', 'regex': False, 'comment': None},
        {'search_text': '...', 'subst': '... ', 'regex': False, 'comment': None},
        {'search_text': '..', 'subst': '.. ', 'regex': False, 'comment': None}
    ]

    parser = ScriptParser(substitutions=text_subst)
    renderer = AudioRenderer()

    manager = ProjectManager(script_parser=parser, audio_renderer=renderer)

    app = QApplication(sys.argv)
    gui = GUI(project_manager=manager, debug=True, version=version)

    sys.exit(app.exec_())

