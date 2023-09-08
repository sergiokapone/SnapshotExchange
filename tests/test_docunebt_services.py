import unittest
import sys
import os  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.documentation import rst_to_html


class TestRstToHtml(unittest.TestCase):
    
    def test_rst_to_html(self):
        rst_text = """
Title
=====

Це заголовок
"""
        expected_html = (
            "<div class=\"document\" id=\"title\">\n"
            "<h1 class=\"title\">Title</h1>\n"
            "<p>Це заголовок</p>\n"
            "</div>\n"
        )
        
        result_html = rst_to_html(rst_text)
        self.assertEqual(result_html.strip(), expected_html.strip())

if __name__ == "__main__":
    unittest.main()