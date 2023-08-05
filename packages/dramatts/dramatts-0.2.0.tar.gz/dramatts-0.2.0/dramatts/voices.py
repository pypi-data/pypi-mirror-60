"""
voices.py - voices config class for dramaTTS
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


class VoiceConfig:

    base_pitch_offset = 0
    base_tempo = 1.0
    base_volume = 1.0

    def __init__(self, voice_name='cmu_us_slt_cg', pitch_shift=0, tempo=1.0, volume=1.0, speaker_name=None):
        """Creates a voice config that allows changing pitch and tempo of the festival voices

        Args:
            voice_name(str): A festival voice name
            pitch_shift(int): SoX pitch shift value (+-100ths of a semitone)
            tempo(float): SoX tempo factor (1.0 = no change)
            volume(float): Volume factor (1.0 = no change, >1.0 = louder)
        """

        self.speaker_name = speaker_name
        self.voice_name = voice_name
        self.user_pitch_shift = int(pitch_shift)
        self.user_tempo = tempo
        self.user_volume = volume

    @property
    def pitch_shift(self):
        """Final pitch shift"""
        return self.base_pitch_offset + self.user_pitch_shift

    @property
    def tempo(self):
        """Final tempo"""
        return self.base_tempo * self.user_tempo

    @property
    def volume(self):
        """Final volume"""
        return self.base_volume * self.user_volume

    def create_voice_dict(self):
        """Creates a dictionary representation of the voice config"""

        voice_dict = {
            'voice_name': self.voice_name,
            'user_pitch_shift': self.user_pitch_shift,
            'user_tempo': self.user_tempo,
            'user_volume': self.user_volume
        }

        return voice_dict

    def update_parameters(self, voice=None, pitch_shift=0, tempo=1.0, volume=1.0):
        """Updates the voice parameters"""

        if voice:
            self.voice_name = voice
        self.user_pitch_shift = int(pitch_shift)
        self.user_tempo = tempo
        self.user_volume = volume


class MaleVoice(VoiceConfig):
    """Predefined male voice example"""

    base_voice_name = 'cmu_us_rms_cg'
    base_pitch_offset = 100
    base_tempo = 1.2
    base_volume = 1.0

    def __init__(self, speaker_name='Joe Doe', pitch_shift=0, tempo=1.0, volume=1.0):

        super().__init__(voice_name=self.base_voice_name, speaker_name=speaker_name, pitch_shift=pitch_shift,
                         tempo=tempo, volume=volume)


class FemaleVoice(VoiceConfig):
    """Predefined female voice example"""

    base_voice_name = 'cmu_us_slt_cg'
    base_pitch_offset = 0
    base_tempo = 1.0
    base_volume = 1.0

    def __init__(self, speaker_name='Jane Doe', pitch_shift=0, tempo=1.0, volume=1.0):

        super().__init__(voice_name=self.base_voice_name, speaker_name=speaker_name, pitch_shift=pitch_shift,
                         tempo=tempo, volume=volume)

