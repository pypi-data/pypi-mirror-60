import os
import re

from bs4 import BeautifulSoup

from linter.helpers.list_helpers import index_of_string_in_list
from linter.linters.base import Linter


class CheckHeadings(Linter):
    """
    All top level headings should be of type H1, not type H2
    """

    def lint(self):
        for i in range(len(self.lines)):
            if '<h2' in self.lines[i].strip() and 'class="govuk-heading-l"' in self.lines[i].strip():
                self.append_error("The page heading should be H1", i + 1, self.lines[i].strip())


class FindHardcodedStrings(Linter):
    """
    Finds hardcoded strings in HTML
    """

    def lint(self):
        soup = BeautifulSoup(self.text, "html.parser")
        result = soup.stripped_strings

        for i in result:
            if not i.startswith("{{") and not i.startswith("{%"):
                self.append_error("Use LITE Content Library instead of hardcoding strings",
                                  index_of_string_in_list(i, self.lines), i)


class TagsSpacing(Linter):
    """
    Tags should have a space after them eg {{ hello }} instead of {{hello}}
    or {% hello %} instead of {%hello%}
    """

    def _lint(self, char, char2):
        tags = re.findall("{" + char + "(\S*?)" + char2 + "}", self.text)
        for item in tags:
            self.append_error("Tag contents should have a surrounding space eg "
                              "{" + char + " " + item + " " + char2 + "} instead of {" + char + item + char2 + "}",
                              index_of_string_in_list("{" + char + item + char2 + "}", self.lines))

    def lint(self):
        self._lint("{", "}")
        self._lint("%", "%")


class CheckFilenames(Linter):
    """
    HTML files and folders should use dashes instead of underscores in its filename
    """

    def lint(self):
        if "_" in self.file:
            self.append_error("Use dashes instead of underscores in filenames and folders, like so: " +
                              self.file.replace("_", "-"))


class EnforceBlockTitle(Linter):
    """
    All pages should have {% block title %}
    """

    def lint(self):
        if "{% block title %}" not in self.text and "includes/" not in self.file and "tabs/" not in self.file:
            self.append_error("Missing page title - use {% block title %}Title goes here{% endblock %} to set it")


class UnusedFiles(Linter):
    """
    Find unused HTML files
    """

    def _find_file(self, look_for_file_name):
        for root, _, files in os.walk(self.base_directory):
            for file_name in files:
                if file_name.endswith(".html") or file_name.endswith(".py"):
                    with open(f"{root}/{file_name}") as f:
                        if look_for_file_name in f.read():
                            return True

        return False

    def lint(self):
        if self.file.endswith(".html") and not self.file.endswith("404.html") and not self.file.endswith("500.html"):
            if not self._find_file(self.file):
                self.append_error("⚠️  This file isn't being used anywhere")


class PreventInlineStyles(Linter):
    """
    Prevent inline styles
    """

    def lint(self):
        for i in range(len(self.lines)):
            if 'style=' in self.lines[i].strip() and "display:none;visibility:hidden" not in self.lines[i].strip():
                self.append_error("Don't use inline styles", i + 1, self.lines[i].strip())


class OneLoadBlock(Linter):
    """
    Each HTML file should have at most one {% load %} block
    """

    def lint(self):
        load_blocks = [x for x in self.lines if "{% load" in x]
        if len(load_blocks) > 1:
            load_blocks.pop(0)
            initial_index = 0
            for block in load_blocks:
                index = self.lines.index(block, initial_index) + 1
                self.append_error("More than one {% load %} block", index, block)
                initial_index = index


class AllTagsUsed(Linter):
    """
    Ensure each template tag imported in {% load %} is actually used
    """

    def lint(self):
        load_blocks = [x for x in self.lines if "{% load" in x]
        if load_blocks:
            load_block = load_blocks.pop(0)
            template_tags = load_block[7:-3].strip().split(" ")

            for template_tag in template_tags:
                if template_tag == "sass_tags":
                    continue
                text = self.text.replace(load_block, "")
                if template_tag not in text:
                    self.append_error(f"Template tag '{template_tag}' not used in file",
                                      index_of_string_in_list(load_block, self.lines),
                                      load_block)


class EnsureAllIDsAreUnique(Linter):
    """
    Ensure all IDs used in a file are unique to that file
    """

    def lint(self):
        reg = "id=\"(.*?)\""
        ids = re.findall(reg, self.text)
        ids_completed = []
        for id in ids:
            ids_completed.append(id)
            if ids_completed.count(id) == 2:
                self.append_error("IDs should be unique",
                                  0,
                                  "id=\"" + id + "\"")


class BlockOrdering(Linter):
    """
    {% load %} block should be after {% extends %}, but before first {% block %}
    """

    def lint(self):
        load_blocks = [x for x in self.lines if "{% load" in x]
        try:
            extend_block = self.text.index("{% extends")
            load_block = self.text.index("{% load")
            block_block = self.text.index("{% block")

            if load_block < extend_block or load_block > block_block:
                self.append_error("{% load %} block should be after {% extends %}, but before first {% block %}",
                                  self.lines.index(load_blocks[0]) + 1)
        except ValueError:
            pass


class PreventTwoPaneOverwite(Linter):
    """
    Ensure that body isn't overwritten in two-pane pages
    """

    def lint(self):
        if "two-pane.html" in self.text and "{% block body %}" in self.text:
            self.append_error("Extend base.html instead of two-pane.html if you're just going to override body")


class EnforceSingleQuotesInBlocks(Linter):
    """
    {%%} blocks should have single quotes, not double
    """

    def lint(self):
        blocks = re.findall("{% (.*) %}", self.text)
        for item in blocks:
            if "\"" in item:
                self.append_error("{%%} Blocks should use single quotes not double",
                                  index_of_string_in_list(item, self.lines))


class BlocksSpacing(Linter):
    """
    Ensure blocks are spaced correctly
    """

    def lint(self):
        # Blocks should NOT have an empty line below them
        # eg
        # {% block javascript %}
        # 	DO STUFF HERE!
        # {% endblock %}
        for i in range(len(self.lines)):
            if self.lines[i].startswith("{% block") and not self.lines[i].rstrip().endswith("endblock %}"):
                try:
                    if self.lines[i + 1].strip() == "":
                        self.append_error("Blocks should not have an empty line after them",
                                          i + 1,
                                          self.lines[i].strip() + '\n    ' + self.lines[i + 1].strip())
                except IndexError:
                    pass

        # End Blocks should NOT be proceeded with an empty line
        # eg
        # {% block javascript %}
        # 	DO STUFF HERE!
        # {% endblock %}
        for i in range(len(self.lines)):
            if self.lines[i].startswith("{% endblock %}"):
                try:
                    if self.lines[i - 1].strip() == "":
                        self.append_error("End blocks should not have an empty line before them",
                                          i - 1,
                                          self.lines[i].strip() + '\n    ' + self.lines[i - 1].strip())
                except IndexError:
                    pass

        # End Blocks should be succeeded by an empty line
        # eg
        #   ...
        # {% endblock %}
        #
        # {% block javascript %}
        # 	...
        # {% endblock %}
        for i in range(len(self.lines)):
            if self.lines[i].rstrip() == "{% endblock %}":
                try:
                    if self.lines[i + 1].strip() != "":
                        self.append_error("End blocks should be succeeded by an empty line",
                                          i + 1,
                                          self.lines[i].strip() + '\n    ' + self.lines[i + 1].strip())
                except IndexError:
                    pass


class TabsOverSpaces(Linter):
    def lint(self):
        for line in self.lines:
            indent = abs(len(line.lstrip()) - len(line))
            substring = line[:indent]
            if " " in substring:
                self.append_error("We use tabs over spaces", index_of_string_in_list(line, self.lines))
