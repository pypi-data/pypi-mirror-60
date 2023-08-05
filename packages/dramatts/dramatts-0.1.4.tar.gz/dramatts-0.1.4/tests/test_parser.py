from pytest import *
from dramatts.core import ScriptParser
from pathlib import Path


def setup_parser():
    """Creates a parser object"""

    parser = ScriptParser()

    # define an example script file to import
    parser.filename = Path('../examples/example_01.txt')

    # load the lines from the file
    parser.read_input()

    # parse the lines
    parser.parse_lines()

    return parser


def test_char_ident():
    """Check if all characters in the text are identified correctly"""

    parser = setup_parser()

    assert parser.characters == ['Narrator', 'BOB', 'MARY-ANN']


def test_scene_ident():
    """Check if the scenes have been identified correctly"""

    # first check the scene count, note that the example starts with some words before the first scene starts
    # This text part will be interpreted as scene "0" (therefore adding one scene to the scene count)

    parser = setup_parser()

    assert parser.scene_count == 6

    # next check the scene names by using the keys of the lines attribute (which is an ordered dict with the scene names
    # as keys)
    # Note that the lines before the first scene are assigned to scene name 'Preface'

    assert list(parser.lines.keys()) == [
        'Preface',
        '1. Scene without any text content',
        '2. Scene with only narrative descriptions',
        '3. Scene with dialogue content',
        '4. Scene with dialogue content and narrator text',
        '5. Scene with dialogue and inline comment'
    ]


def test_line_content():
    """Tests if the line content is identified correctly"""

    parser = setup_parser()

    # test the lines dict for the second line of the 3rd scene
    assert parser.lines['3. Scene with dialogue content'][1][0] == 'BOB'
    assert parser.lines['3. Scene with dialogue content'][1][1] == 'Hello I am Bob and this is my line of dialogue.'

    # test the valid_lines list for the same line (which is the 7th line in the text)
    # note that 'scene_no' == 0 is the 'Preface' and 'scene_line_no' == 0 is the scene title line
    assert parser.valid_lines_list[6]['scene_no'] == 3
    assert parser.valid_lines_list[6]['scene_line_no'] == 2
    assert parser.valid_lines_list[6]['speaker'] == 'BOB'
    assert parser.valid_lines_list[6]['content'] == 'Hello I am Bob and this is my line of dialogue.'
    assert parser.valid_lines_list[6]['line_type'] == 'DialogContent'


def test_line_filter():
    """Check if the get_filtered_valid_lines method works correctly"""

    parser = setup_parser()

    filtered_lines = parser.get_filtered_valid_lines(first_scene=3, last_scene=3, speaker=None)

    assert len(filtered_lines) == 3

    filtered_lines = parser.get_filtered_valid_lines(first_scene=4, last_scene=5, speaker='BOB')

    assert filtered_lines[0]['content'] == 'Hi, Mary-Ann how are you doing?'
    # note that the line scene 5 is split into two line due to the inline comment
    assert filtered_lines[1]['content'] == 'I wonder what this lever does... '
    assert filtered_lines[2]['content'] == ' ...I don\'t see any effect...'

