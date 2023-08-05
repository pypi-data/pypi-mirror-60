import os.path
import subprocess
import sys
import unittest

if "TEST_DIR" not in os.environ:
    print("Warning: TEST_DIR environment variable not set.", file=sys.stderr)
    print("Using c test data.", file=sys.stderr)

sys.path.append(os.path.join(os.path.dirname(__file__), os.environ.get("TEST_DIR", "c")))
sys.path.append(os.path.join(os.path.dirname(__file__), "tools"))

import examples
import lexeme as lex
import scanner

class Scanner:
    def __init__(self, dirname=None):
        if dirname is None:
            dirname = os.path.join(os.path.dirname(__file__), os.environ.get("TEST_DIR", "c"))
        self.path = os.path.abspath(os.path.join(dirname, "run_match"))

    def longest(self, pinput):
        """Wrapper for running run_match longest."""
        out = subprocess.check_output(
            [self.path, "longest"],
            input=f"{pinput}\n".encode())
        token, lexeme = out.decode()[:-1].split('\n', maxsplit=1)
        return token, lexeme

    def single(self, scanner_type, pinput):
        """Wrapper for running run_match single."""
        out = subprocess.check_output(
            [self.path, "single", "-s", scanner_type],
            input=f"{pinput}\n".encode())
        return out.decode()[:-1]

    def tokenize(self, pinput):
        """Wrapper for running run_match tokenizer."""
        out = subprocess.check_output(
            [self.path, "tokenizer"],
            input=f"{pinput}\n".encode())
        return out.decode()

def parametrize_longest_match_test(test_case, scanner_type):
    for word, label in test_case.test_data[scanner_type]:
        token, lexeme = test_case.scanner.longest(word)
        if label:
            test_case.assertEqual(token, scanner_type)
            test_case.assertEqual(lexeme, word)
        else:
            test_case.assertNotEqual(token, scanner_type)

def parametrize_single_match_test(test_case, scanner_type):
    for word, label in test_case.test_data[scanner_type]:
        lexeme = test_case.scanner.single(scanner_type, word)
        test_case.assertEqual(lexeme, word if label else "")

class MatchTest(unittest.TestCase):
    def setUp(self):
        self.test_data = {}
        for scanner_type in scanner.SCANNER:
            path = os.path.join(os.path.dirname(__file__), f"data/{scanner_type}.csv")
            with open(path, "r") as file:
                self.test_data[scanner_type] = examples.read(file)
        self.scanner = Scanner()

    def test_longest(self):
        for scanner_type in scanner.SCANNER:
            with self.subTest(scanner_type=scanner_type):
                parametrize_longest_match_test(self, scanner_type)

    def test_single(self):
        for scanner_type in scanner.SCANNER:
            with self.subTest(scanner_type=scanner_type):
                parametrize_single_match_test(self, scanner_type)

    def test_tokenize(self):
        identifier = lex.identifier()
        number = lex.number()
        character = lex.character()
        string = lex.string()
        expected = "".join([
            f"identifier {identifier}\n",
            f"whitespace  \n",
            f"number {number}\n",
            f"whitespace \t\n",
            f"character {character}\n",
            f"whitespace \n\n",
            f"string {string}\n",
            f"whitespace \n\n"
        ])
        actual = self.scanner.tokenize(f"{identifier} {number}\t{character}\n{string}")
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
