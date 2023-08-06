class ansible_inventory():

    def __init__(self):
        self._sections = dict()

    def add_section(self, section):
        if section in self._sections:
            raise DuplicateSectionError(section)
        self._sections[section] = dict()

    def set(self, section, key, value):
        if not section:
            raise NoSectionError(section) from None
        try:
            setdict = self._sections[section]
        except KeyError:
            raise NoSectionError(section) from None
        setdict[key.lower()] = value

    def write(self, fp):
        for section in self._sections:
            self._write_section(fp, section, self._sections[section].items())

    def _write_section(self, fp, section_name, section_item):
        fp.write("[{}]\n".format(section_name))
        for key, value in section_item:
            fp.write("{} {}\n".format(key, value))


class Error(Exception):
    """Base class for ansible_inventory exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class NoSectionError(Error):
    """Raised when no section matches a requested option."""

    def __init__(self, section):
        Error.__init__(self, 'No section: %r' % (section,))
        self.section = section
        self.args = (section, )


class DuplicateSectionError(Error):
    """Raised when a section is repeated in an input source."""

    def __init__(self, section, source=None, lineno=None):
        msg = [repr(section), " already exists"]
        if source is not None:
            message = ["While reading from ", repr(source)]
            if lineno is not None:
                message.append(" [line {0:2d}]".format(lineno))
            message.append(": section ")
            message.extend(msg)
            msg = message
        else:
            msg.insert(0, "Section ")
        Error.__init__(self, "".join(msg))
        self.section = section
        self.source = source
        self.lineno = lineno
        self.args = (section, source, lineno)