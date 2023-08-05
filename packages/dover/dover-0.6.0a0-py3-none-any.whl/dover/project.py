from pathlib import Path
from itertools import chain
from . import util
from . import parse


class ConfigurationError(Exception):
    pass


def version_regex():

    regex = [parse.get_version_assignment_regex(), parse.get_embedded_version_regex()]

    def _version_regex(input_text):

        for rgx in regex:
            match = rgx.match(input_text)
            if match:
                return match.groupdict()["version"]
        return None

    return _version_regex


class VersionedFile:
    """Represents a file that contains a version string in one of these basic formats:

        version = 0.0.0
        __version__ = 0.0.0
        v0.0.0

    """

    def __init__(self):
        self.re_ver = version_regex()
        self.file_path = None
        self.relative_path = None
        self.content = None
        self.versioned_lines = []
        self._updates = 0

    @staticmethod
    def init(file_path, root_dir):
        vfile = VersionedFile()
        vfile.file_path = file_path
        vfile.relative_path = file_path.relative_to(root_dir)
        with file_path.open("r") as fh_:
            vfile.content = fh_.readlines()
        vfile.collect_version_info()
        return vfile

    @property
    def name(self):
        return self.file_path.name

    def collect_version_info(self):
        for index, line in enumerate(self.content):
            version_str = self.re_ver(line.strip())
            if version_str:
                self.versioned_lines.append((index, line, version_str))

    def __iter__(self):
        for index, line, version_str in self.versioned_lines:
            yield (
                "{:0>4}".format(index),
                "({})".format(line.strip()),
                str(self.relative_path),
                version_str,
            )

    def update(self, new_version):
        for index, line, version_str in self.versioned_lines:
            self._updates += 1
            self.content[index] = line.replace(version_str, str(new_version))

    def save(self):
        with self.file_path.open("w") as fh_:
            fh_.write("".join(self.content))


def print_versioned_lines(vfiles):
    elements = [(p, i, l) for i, l, p, v in chain(*vfiles)]
    for line in util.format_seqs(
        elements, fmt=(util.bold("{{: <{}}} "), "{{: <{}}} ", "{{: <{}}}")
    ):
        print(line)


def print_versioned_updates(vfiles, new_version):
    elements = [(p, v, new_version) for i, l, p, v in chain(*vfiles)]
    for line in util.format_seqs(
        elements, fmt=(util.bold("{{: <{}}} "), "({{: <{}}} -> ", "{{: <{}}})")
    ):
        print(line)


def find_config_file(cwd=None):
    """Fetches a suitable configuration file to look for dover file options.

    """
    if not cwd:
        cwd = Path.cwd()
    cfg_opts = (".dover", ".dover.cfg", "dover.cfg", "setup.cfg", "pyproject.toml")
    for cfg in cfg_opts:
        cfg_pth = Path(cwd, cfg)
        if cfg_pth.exists() and cfg_pth.is_file():
            return cfg_pth

    raise ConfigurationError("Dover found no configuration files!")


def raise_if_file_not_exist(dfile, errmsg):
    if not dfile.exists():
        raise ConfigurationError(errmsg)


def toml_parser(config_file):
    """
    Yields each file listed in the projects pyproject.toml file.

    """
    import toml

    cfg = toml.load(str(config_file))
    try:
        files = cfg["tool"]["dover"]["versioned_files"]
        for file_ in files:
            dfile = Path(config_file.parent, file_)
            raise_if_file_not_exist(
                dfile,
                "Invalid versioned file reference. Path does not exist: {}".format(
                    dfile.name
                ),
            )
            yield dfile
    except KeyError:
        raise ConfigurationError("Could not read dover section from pyproject.toml")


def ini_parser(config_file):
    """
    Yields each file listed in the projects ini config file.

    """
    from configparser import ConfigParser

    config = ConfigParser()
    config.read(config_file)

    for section in config.sections():
        if section.startswith("dover:file:"):
            section_file = section.split(":")[2]
            dfile = Path(config_file.parent, section_file)
            raise_if_file_not_exist(
                dfile,
                "Invalid configuration section: [{}]. Path does not exist.".format(
                    section
                ),
            )
            yield dfile


def collect_versioned_files(config_file):
    if config_file.suffix == ".toml":
        config_parser = toml_parser(config_file)
    else:
        config_parser = ini_parser(config_file)

    return [VersionedFile.init(dfile, config_file.parent) for dfile in config_parser]


class VersionMissMatchError(Exception):
    pass


def assert_versions(versioned_files):
    versions = []
    for vfile in versioned_files:
        for vline in vfile.versioned_lines:
            index, line, version_str = vline  # pylint: disable=unused-variable
            versions.append(version_str)

    canonical_version = versions.pop()
    if not all([version == canonical_version for version in versions]):
        elements = [(p, v, l) for i, l, p, v in chain(*versioned_files)]
        version_list = "\n".join(util.format_seqs(elements))
        raise VersionMissMatchError(
            "Not all file versions match:\n\n{}".format(version_list)
        )

    return canonical_version
