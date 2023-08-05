"""This is a yaml parser module."""
import os.path
import yaml


class YamlParser:
    # pylint: disable=too-few-public-methods
    """
    The YamlParser initializes a yamlfile
    and loads the content of the file into the content variable
    """
    content = None

    def __init__(self, yaml_path):
        if not os.path.isfile(yaml_path):
            raise Exception("Yaml file '{path_to_file}' "
                            "does not exist and could not "
                            "be loaded".format(path_to_file=yaml_path))
        with open(yaml_path, 'r', encoding='utf-8') as stream:
            self.content = yaml.load(stream, Loader=yaml.FullLoader)

    def data(self, namespace):
        """
        Once the YamlParser has been initialised
        content variable will be set, if a namespace
        is set, then the yaml node matching the namespace
        will be returned
        """
        return self.content[namespace]
