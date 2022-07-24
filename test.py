"""Unit tests for rss_reader.py script"""

import unittest
from io import StringIO
from unittest.mock import patch
import rss_reader
from tempfile import gettempdir
from datetime import datetime
from unittest.mock import MagicMock
from colorama import Fore
from colorama import Style


class TestReader(unittest.TestCase):

    
    def test_connect(self):
        test_cases = [
            {
                'argum': 'abcd',
                'expect_res': "Error: Invalid URL. Check the entered argument 'source'\n"
            },
            {
                'argum': 'https://n.yahoo.com/rss/',
                'expect_res': "Error: Connection to the sourse URL failed.\n"
            }
        ]
       # expected_output = "Error: Invalid URL. Check the entered argument 'source'\n"
        for test_case in test_cases:
            with patch('sys.stdout', new = StringIO()) as fake_out:
                rss_reader.connect(test_case['argum']) 
                self.assertEqual(fake_out.getvalue(), test_case['expect_res'])

    def test_news_counter(self):
        new_obj = rss_reader.MyFeedParser(False)
        test_cases = [
            {
                'argum1': 10,
                'argum2': 5,
                'expect_res': 5
            },
            {
                'argum1': 10,
                'argum2': 12,
                'expect_res': 10
            },
            {
                'argum1': 10,
                'argum2': None,
                'expect_res': 10
            }
        ]
        for test_case in test_cases:
            self.assertEqual(new_obj.news_counter(test_case['argum1'], test_case['argum2']), test_case['expect_res'])

    def test_cash_read(self):
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new = StringIO()):
                new_obj = rss_reader.MyFeedParser(True)
                mydate = datetime.strptime('1900-01-01', '%Y-%m-%d')
                new_obj.cash_read(mydate, 'abc', True, None)
    
    def test_print_json(self):
        new_obj = rss_reader.MyFeedParser(False)
        new_obj.feed = 'feed1'
        new_obj.news = [
            {
            'title': 'title1', 'pubdate': 'date1', 'link': 'link1', 'description': 'descr1', 
            'media_url': '', 'media_path': '', 'feed': 'feed1', 'source': 'source'
            }
        ]
        expected_output = '{\n  "feed": "feed1",\n  "news": [\n    {\n      "title": "title1",\n      "pubdate": '
        expected_output += '"date1",\n      "link": "link1",\n      "description": "descr1"\n    }\n  ]\n}\n'
        with patch('sys.stdout', new = StringIO()) as fake_out:
            new_obj.print_json(False)
            self.assertEqual(fake_out.getvalue(), expected_output)

    def test_print_html(self):
        new_obj = rss_reader.MyFeedParser(False)
        new_obj.feed = 'feed1'
        new_obj.news = [
            {
            'title': 'title1', 'pubdate': 'date1', 'link': 'link1', 'description': 'descr1', 
            'media_url': '', 'media_path': '', 'feed': 'feed1', 'source': 'source'
            },
            {
            'title': 'title2', 'pubdate': 'date2', 'link': 'link2', 'description': 'descr2', 
            'media_url': '', 'media_path': '', 'feed': 'feed2', 'source': 'source'
            }
        ]
        expected_result = True
        result = new_obj.print_html(gettempdir(), False)
        self.assertEqual(expected_result, result)

    def test_print_pdf(self):
        new_obj = rss_reader.MyFeedParser(False)
        new_obj.feed = 'feed1'
        new_obj.news = [
            {
            'title': 'title1', 'pubdate': 'date1', 'link': 'link1', 'description': 'descr1', 
            'media_url': '', 'media_path': '', 'feed': 'feed1', 'source': 'source'
            },
            {
            'title': 'title2', 'pubdate': 'date2', 'link': 'link2', 'description': 'descr2', 
            'media_url': '', 'media_path': '', 'feed': 'feed2', 'source': 'source'
            }
        ]
        expected_result = True
        result = new_obj.print_pdf(gettempdir(), False)
        self.assertEqual(expected_result, result)
    
    def test___str__(self):
        new_obj = rss_reader.MyFeedParser(False)
        new_obj.feed = 'feed1'
        new_obj.news = [
            {
            'title': 'title1', 'pubdate': 'date1', 'link': 'link1', 'description': 'descr1', 
            'media_url': '', 'media_path': '', 'feed': 'feed1', 'source': 'source'
            }
        ]
        expected_output = '\n' + f'Feed: {Fore.RED}feed1{Style.RESET_ALL}' + '\n' + '\n'
        expected_output += f'Title: {Fore.BLUE}title1{Style.RESET_ALL}' + '\n'
        expected_output += f'Date: {Fore.GREEN}date1{Style.RESET_ALL}' + '\n'
        expected_output += f'Link: {Fore.YELLOW}link1{Style.RESET_ALL}' + '\n'
        expected_output += 'Description: descr1' + '\n' + '\n' + '\n'
        with patch('sys.stdout', new = StringIO()) as fake_out:
            print(new_obj)
            self.assertEqual(fake_out.getvalue(), expected_output)
    
    @ staticmethod
    def mock_print_pdf(path, verbose):
        print('pdf')

    @ staticmethod
    def mock_print_html(path, verbose):
        print('html')

    @ staticmethod
    def mock_print_json(verbose):
        print('json')

    def test_choose_printout(self):
        new_obj = rss_reader.MyFeedParser(False)
        new_obj.print_html = MagicMock(side_effect = self.mock_print_html)
        new_obj.print_pdf = MagicMock(side_effect = self.mock_print_pdf)
        new_obj.print_json = MagicMock(side_effect = self.mock_print_json)
        new_obj.feed = 'feed1'
        new_obj.news = [
            {
            'title': 'title1', 'pubdate': 'date1', 'link': 'link1', 'description': 'descr1', 
            'media_url': '', 'media_path': '', 'feed': 'feed1', 'source': 'source'
            }
        ]
        expected_output = '\n' + f'Feed: {Fore.RED}feed1{Style.RESET_ALL}' + '\n' + '\n'
        expected_output += f'Title: {Fore.BLUE}title1{Style.RESET_ALL}' + '\n'
        expected_output += f'Date: {Fore.GREEN}date1{Style.RESET_ALL}' + '\n'
        expected_output += f'Link: {Fore.YELLOW}link1{Style.RESET_ALL}' + '\n'
        expected_output += 'Description: descr1' + '\n' + '\n' + '\n'
        test_cases = [
            {
                'json': True,
                'html': False,
                'pdf': False,
                'expect_res': 'json\n'
            },
            {
                'json': False,
                'html': True,
                'pdf': False,
                'expect_res': 'html\n'
            },
            {
                'json': False,
                'html': False,
                'pdf': True,
                'expect_res': 'pdf\n'
            },
            {
                'json': False,
                'html': False,
                'pdf': False,
                'expect_res': expected_output
            },
            {
                'json': True,
                'html': True,
                'pdf': False,
                'expect_res': 'json\n'+'html\n'
            },
            {
                'json': True,
                'html': False,
                'pdf': True,
                'expect_res': 'json\n'+'pdf\n'
            }
        ]
        for test_case in test_cases:
             with patch('sys.stdout', new = StringIO()) as fake_out:
                new_obj.choose_printout(test_case['json'], test_case['html'], test_case['pdf'], False)
                self.assertEqual(fake_out.getvalue(), test_case['expect_res'])
        

if __name__ == '__main__':
    unittest.main()