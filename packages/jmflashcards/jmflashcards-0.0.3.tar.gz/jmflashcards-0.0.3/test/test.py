import os
import sys
import asyncio
from unittest import TestCase, IsolatedAsyncioTestCase
from tempfile import mkdtemp
from shutil import rmtree
from unittest.mock import Mock, patch, mock_open, call, AsyncMock
from jmflashcards.commands import load_config
from jmflashcards.runner import run_command
from jmflashcards.latex import render_latex_to_file
from jmflashcards.parser import FlashCard, Entry, Side, MathSide, ImageSide, \
        TextSide
from jmflashcards.fcdeluxe import FCDFlashCard

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FLASHCARD_DIR = "flashcards"
FLASHCARD_PATH = os.path.join(CURRENT_DIR, FLASHCARD_DIR)
NUM_ENTRIES = 5

def test_run_command():
    async def test():
        await run_command("ls", cwd="/tmp")
    asyncio.run(test())


# TODO Configure the load config procedure
CONFIG_FILE_WORKING ="""
input_dir: /dev/null
output_dir: /dev/urandom
question_keys: 
    - one
    - two
answer_keys:
    - three
    - four
"""

class ConfigurationTestCase(TestCase):
    def test_defaultconfig(self):
        from jmflashcards.commands import INPUT_DIR, OUTPUT_DIR, \
                QUESTION_KEYS, ANSWER_KEYS
        with patch('jmflashcards.commands.open',
                mock_open(read_data="")): 
            result = load_config()
            self.assertIn("input_dir", result)
            self.assertEqual(result['input_dir'], INPUT_DIR)
            self.assertIn("output_dir", result)
            self.assertEqual(result['output_dir'], OUTPUT_DIR)
            self.assertIn("question_keys", result)
            for key in QUESTION_KEYS:
               self.assertIn(key, result['question_keys'])
            self.assertIn("answer_keys", result)
            for key in ANSWER_KEYS:
               self.assertIn(key, result['answer_keys'])

    def test_custom_config(self):
        with patch('jmflashcards.commands.open', 
                mock_open(read_data=CONFIG_FILE_WORKING)): 
            result = load_config()
            self.assertIn("input_dir", result)
            self.assertEqual(result['input_dir'], "/dev/null")
            self.assertIn("output_dir", result)
            self.assertEqual(result['output_dir'], "/dev/urandom")
            self.assertIn("question_keys", result)
            for key in ('one', 'two'):
               self.assertIn(key, result['question_keys'])
            self.assertIn("answer_keys", result)
            for key in ('three', 'four'):
               self.assertIn(key, result['answer_keys'])


class FlashCardTestCase(TestCase):

    def setUp(self):
        self.syncronizer = Mock()
        self.syncronizer.question_keys = ('question',)
        self.syncronizer.answer_keys = ('answer',)
        self.repository = Mock()
        self.repository.syncronizer = self.syncronizer
        self.repository.directory = FLASHCARD_PATH

        self.flashcard = FlashCard('test', self.repository)
        self.flashcard.parse()

    def test_one(self):
        self.assertEqual(len(self.flashcard.entries), NUM_ENTRIES)
        for entry in self.flashcard.entries:
            self.assertTrue(isinstance(entry, Entry))
            self.assertTrue(isinstance(entry.question, Side))
            self.assertTrue(isinstance(entry.answer, Side))

class TextParseTestCase(TestCase):

    def _get_side(self, raw_text, name="question"):
        mock_entry = Mock()
        return Side.build_from_raw(mock_entry, name, raw_text)

    def assert_side_class(self, raw_text, side_class):
        side = self._get_side(raw_text)
        if not isinstance(side, side_class):
            self.fail("Expression '%s' should have been parsed as class '%s' but returned class '%s'" % (raw_text, side_class.__name__, side.__class__.__name__))

    def test_expression_parsing(self):
        self.assert_side_class("texto", TextSide)
        self.assert_side_class("\\$texto", TextSide)
        self.assert_side_class("\\~texto", TextSide)
        self.assert_side_class("\\\\texto", TextSide)
        self.assert_side_class("$texto", MathSide)
        self.assert_side_class("~texto", ImageSide)

    def assert_text_parsing(self, raw_text, expected):
        self.assert_side_class(raw_text, TextSide)
        side = self._get_side(raw_text)
        cured = side.get_cured_text()
        self.assertEqual(expected, cured, 
                "Text '%s' should have rendered like '%s' but rendered '%s'" % ( raw_text, 
                    expected, cured))

    def test_text_parsing(self):
        self.assert_text_parsing("\\$text", "$text")
        self.assert_text_parsing("\\~text", "~text")
        self.assert_text_parsing("\\\\text", "\\text")

from jmflashcards.fcdeluxe import FCDELUXE_DIR_NAME, \
        FCDFlashCardRenderer, FCDRepository, FCDELUXE_HEADER

class FlashCardsDeluxeTestCase(IsolatedAsyncioTestCase):
    def setUp(self):
        self.syncronizer = Mock()
        self.repository = Mock()
        self.repository.syncronizer = self.syncronizer
        self.repository.directory = FLASHCARD_PATH
        self.syncronizer.question_keys = ('question',)
        self.syncronizer.answer_keys = ('answer',)

    async def test_build(self):
        flashcard = FlashCard('test', self.repository)
        flashcard.parse()
        output_dir = mkdtemp(prefix="mockoutput_dir")
        fcd_repository = FCDRepository(output_dir)
        renderer = FCDFlashCardRenderer(fcd_repository)
        fcd_flashcard = await renderer.render(flashcard)

        file_name = flashcard.reference + ".txt"
        file_path = os.path.join(output_dir, FCDELUXE_DIR_NAME, file_name)
        media_dir_path = os.path.join(output_dir, FCDELUXE_DIR_NAME, 
                FCDFlashCard.get_media_dir_name(flashcard.reference))

        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(os.path.isfile(file_path))
        self.assertTrue(os.path.exists(media_dir_path))
        self.assertTrue(os.path.isdir(media_dir_path))

        f = open(file_path)
        text = f.read()
        f.close()

        def fail_msg(msg, text=text):
            line = "."*70
            content = msg, line, text, line
            return "\n".join(content)

        lines = text.split('\n')
        self.assertEqual(lines[0], FCDELUXE_HEADER[:-1])
        line_counter = 0
        for line in lines[1:]:
            if not line:
                continue
            line_counter += 1
            fields = line.split('\t')
            self.assertEqual(len(fields), 6, 
                    fail_msg("Invalid entry fields count", text=repr(line)))
            for f_field in fields[2:]:
                if f_field:
                    file_path = os.path.join(media_dir_path, f_field)
                    self.assertTrue(os.path.exists(file_path), 
                            fail_msg("File '%s' dont exist" % file_path))
        self.assertEqual(line_counter, NUM_ENTRIES)
        rmtree(output_dir)

from jmflashcards.latex import render_latex_to_file, WORK_DIR

class LatexRendererTestCase(IsolatedAsyncioTestCase):
    output_file = "/tmp/output.png"
    tex_expression = "\\alpha"

    async def test_run(self):
        await render_latex_to_file(self.tex_expression, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

if __name__ == "__main__":
    import unittest
    unittest.main()

