"""
core.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
import os
from sympy import preview as sympy_preview

# Include dir
include_dir = os.path.abspath(__file__ + '/../../_include')


# Class for building a Whitepaper
# TODO look at https://docs.python.org/3/library/webbrowser.html
class Whitepaper:
    """
    Whitepaper produces documents using code
    """

    # Initialize
    def __init__(self, title, description=None, toc_depth=0, path='.'):
        """
        Initialize instance of Whitepaper class

        `toc_depth` indicates the level to go down into the table of contents. By default a value of 0 is passed,
        which means that no table of contents is generated. Values > 1 indicate how many Sections we go down.

        Parameters
        ----------
        title : str
            Name of whitepaper.
        toc_depth : int
            Section depth for table of contents (Default: 0).
        path : str
            Location to store report
        """

        # Report
        self.title = title
        self.description = description if description is not None else ''
        self.toc_depth = toc_depth
        self.path = path

        # Whitepaper _depth is always 0
        self._depth = 0

        # Internally use to store
        self._sections = []
        self._section_id = -1

    def _create_include_path(self):
        # Make include path if it does not yet exist
        path = os.path.join(self.path, '_include')
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def _render_title(self, backend, buffer):
        if backend == 'stdout':
            print(self.title)

        elif backend == 'html':
            buffer.write('<center><h1>{}</h1></center>'.format(self.title))

    def add_section(self, section):
        assert isinstance(section, Section)
        self._section_id += 1
        self._sections.append(section)

    def render(self, backend='stdout'):
        """
        Render the Whitepaper instance

        Choices for `backend`:
        * stdout
        * markdown
        * html
        * latex
        * xlsx
        * pdf

        Parameters
        ----------
        backend : str
            The backend writer (Default: stdout).
        """

        # Open buffer if necessary
        buffer = None
        ext = None
        if backend == 'html':
            ext = 'html'
        if ext is not None:
            buffer = open(self.title + '.' + ext, 'w')

        # Set up file
        if backend == 'html':
            buffer.write('<html><head><title>{}</title></head><body>'.format(self.title))

        # Render title
        self._render_title(backend, buffer)

        # Make include path if it does not yet exist
        path = os.path.join(self.path, '_include')
        if not os.path.exists(path):
            os.mkdir(path)

        # Loop through all sections and render them
        for section in self._sections:
            # noinspection PyProtectedMember
            section._render(backend, buffer, path)

        # Finish up file
        if backend == 'html':
            buffer.write('</body></html>')

        # Close buffer
        if buffer is not None:
            buffer.close()

    # Render html using jinja
    # TODO html file named after Whitepages title
    def render_html(self, template=None, header=True, footer=None):
        """
        Render html
        """

        # If template_file is None, use from include; split into path and file
        if template is None:
            template = os.path.join(include_dir, 'html', 'template.html')
        template_path, template_file = os.path.split(template)

        # Read in template
        env = Environment(loader=FileSystemLoader(searchpath=template_path), autoescape=False)
        template = env.get_template(template_file)

        # Create _include path
        path = self._create_include_path()

        # Data we need to send to jinja
        title = self.title
        # noinspection PyProtectedMember
        sections = [(section.title, section._render('html', path)) for section in self._sections]

        # Render the html from the template
        if footer is None:
            footer = """
                generated on {now}
                <br>
                compiled by <a href="https://github.com/LockhartLab/whitepaper">whitepaper</a>
            """.format(now=datetime.now())
        html = template.render(title=title, sections=sections, header=header, footer=footer)

        # Write out the html
        output_file = open('index.html', 'w')
        output_file.write(html)
        output_file.close()


# Section of the Whitepaper report
# TODO could offer section to download files?
class Section:
    """

    """

    def __init__(self, title, parent=None):

        # Title of the section
        self.title = title

        # If parent is not None, we can add this Section to it
        if parent is not None:
            parent.add_section(self)

        # By default, set the _depth to 1; otherwise add 1 from parent
        # noinspection PyProtectedMember
        self._depth = 1 if parent is None else parent._depth + 1

        # A place to store all the sections we add
        self._sections = []
        self._equation_id = -1

    # Render section
    # TODO change title to it's own div, named with _depth
    def _render(self, backend, path):
        # Render section title
        # output = self._render_title(backend)
        output = ''
        if backend == 'html' and self._depth > 1:
            output = '<br><b>{}</b><br>'.format(self.title)

        # Create path if it doesn't exist
        path = os.path.join(path, self.title)
        if not os.path.exists(path):
            os.mkdir(path)

        # Loop through all subsections and render
        for section in self._sections:
            # noinspection PyProtectedMember
            output += section._render(backend, path)

        return output

    def _render_title(self, backend):
        output = ''
        if backend == 'html':
            output = '<h2>{0}</h2>'.format(self.title)
        return output

    # Add code
    def add_code(self, code, escape=True):
        self._sections.append(Code(code))

    # Add Equation to the Section
    def add_equation(self, equation):
        """
        Add equation to the Section

        Parameters
        ----------
        equation : str
            Equation in LaTeX format
        """

        # Increment equation ID
        self._equation_id += 1

        # Add equation
        self._sections.append(Equation(equation, self._equation_id))

    def add_graphic(self):
        pass

    def add_section(self, section):
        self._sections.append(section)

    def add_table(self):
        pass

    def add_text(self, text, md=True):
        self._sections.append(Text(text, md))


# TODO should this extend Section?
class Code:
    def __init__(self, code, escape=True):
        self.code = code
        # TODO enable escape
        self.escape = escape

    def _render(self, backend, path):
        # stdout, just print text
        output = ''
        if backend == 'html':
            output = self.code
        return output


# TODO we should be able to create a section directly from one of these subclasses
class Equation:
    def __init__(self, equation, _id):
        self.equation = equation
        self._id = _id

    def _render(self, backend, path):
        # stdout
        # html
        output = ''
        if backend == 'html':
            # File name
            filename = os.path.join(path, 'equation_{}.svg'.format(self._id))

            # Save equation as image
            sympy_preview(self.equation, output='svg', viewer='file', filename=filename, euler=True, dpioptions=500)

            # Check if file was failed to be written
            if not os.path.exists(path):
                raise FileNotFoundError('failed to generate equation; ensure proper latex packages installed')

            # Add to buffer
            output = '<center><img src={} /></center>'.format(filename)
        return output


# TODO enable support for inline equations
# TODO should this extend Section?
class Text(Section):
    def __init__(self, text, md=True):
        self.title = ''
        self.text = text
        self.md = md

    def _render(self, backend, path):
        # stdout, just print text
        output = ''
        if backend == 'html':
            if self.md:
                output = markdown(self.text)
            else:
                output = self.text
        return output


