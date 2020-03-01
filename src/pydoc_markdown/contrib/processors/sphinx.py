# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Provides the #SphinxProcessor that converts reST/Sphinx syntax to
markdown compatible syntax.
"""

import re

from nr.databind.core import Field, Object
from nr.interface import implements
from pydoc_markdown.interfaces import Processor


class SphinxProcessorConfig(Object):
  pass


class SphinxProcessor(Preprocessor):

  CONFIG_CLASS = SphinxProcessorConfig

  def preprocess(self, root, node):
    if not node.docstring:
      return
    lines = []
    in_codeblock = False
    keyword = None
    components = {}

    for line in node.docstring.split('\n'):
      line = line.strip()

      if line.startswith("```"):
        in_codeblock = not in_codeblock

      line_codeblock = line.startswith('    ')

      if not in_codeblock and not line_codeblock:
        match = re.match(r'\s*:(?:param|parameter)\s+(\w+)\s*:(.*)?$', line)
        if match:
          keyword = 'Arguments'
          param = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.get(keyword, [])
          component.append('- `{}`: {}'.format(param, text))
          components[keyword] = component
          continue

        match = re.match(r'\s*:(?:return|returns)\s*:(.*)?$', line)
        if match:
          keyword = 'Returns'
          text = match.group(1)
          text = text.strip()

          component = components.get(keyword, [])
          component.append(text)
          components[keyword] = component
          continue

        match = re.match('\\s*:(?:raises|raise)\\s+(\\w+)\\s*:(.*)?$', line)
        if match:
          keyword = 'Raises'
          exception = match.group(1)
          text = match.group(2)
          text = text.strip()

          component = components.get(keyword, [])
          component.append('- `{}`: {}'.format(exception, text))
          components[keyword] = component
          continue

      if keyword is not None:
        components[keyword].append(line)
      else:
        lines.append(line)

    for key in components:
      self._append_section(lines, key, components)

    node.docstring = '\n'.join(lines)

  @staticmethod
  def _append_section(lines, key, sections):
    section = sections.get(key)
    if not section:
      return

    if lines and lines[-1]:
      lines.append('')

    lines.extend(['**{}**:'.format(key), ''])  # add an extra line because of markdown syntax
    lines.extend(section)

