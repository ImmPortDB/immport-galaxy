import logging
import os

from .interface import ToolSource
from .interface import PagesSource
from .interface import PageSource
from .interface import ToolStdioExitCode
from .yaml import YamlInputSource

from .output_actions import ToolOutputActionGroup
from .output_objects import ToolOutput

from galaxy.tools.deps import requirements
from galaxy.tools.cwl import tool_proxy

from galaxy.util.odict import odict

log = logging.getLogger(__name__)


class CwlToolSource(ToolSource):

    def __init__(self, tool_file):
        self._cwl_tool_file = tool_file
        self._id, _ = os.path.splitext(os.path.basename(tool_file))
        self._tool_proxy = tool_proxy(tool_file)
        self._source_path = tool_file

    @property
    def tool_proxy(self):
        return self._tool_proxy

    def parse_tool_type(self):
        return 'cwl'

    def parse_id(self):
        log.warn("TOOL ID is %s" % self._id)
        return self._id

    def parse_name(self):
        return self._id

    def parse_command(self):
        return "$__cwl_command"

    def parse_environment_variables(self):
        environment_variables = []
        # TODO: Is this even possible from here, should instead this be moved
        # into the job.

        # for environment_variable_el in environment_variables_el.findall("environment_variable"):
        #    definition = {
        #        "name": environment_variable_el.get("name"),
        #        "template": environment_variable_el.text,
        #    }
        #    environment_variables.append(
        #        definition
        #    )

        return environment_variables

    def parse_help(self):
        return ""

    def parse_sanitize(self):
        return False

    def parse_strict_shell(self):
        return True

    def parse_stdio(self):
        # TODO: remove duplication with YAML
        from galaxy.jobs.error_level import StdioErrorLevel

        # New format - starting out just using exit code.
        exit_code_lower = ToolStdioExitCode()
        exit_code_lower.range_start = float("-inf")
        exit_code_lower.range_end = -1
        exit_code_lower.error_level = StdioErrorLevel.FATAL
        exit_code_high = ToolStdioExitCode()
        exit_code_high.range_start = 1
        exit_code_high.range_end = float("inf")
        exit_code_lower.error_level = StdioErrorLevel.FATAL
        return [exit_code_lower, exit_code_high], []

    def parse_interpreter(self):
        return None

    def parse_version(self):
        return "0.0.1"

    def parse_description(self):
        return self._tool_proxy.description() or ""

    def parse_input_pages(self):
        page_source = CwlPageSource(self._tool_proxy)
        return PagesSource([page_source])

    def parse_outputs(self, tool):
        output_instances = self._tool_proxy.output_instances()
        outputs = odict()
        output_defs = []
        for output_instance in output_instances:
            output_defs.append(self._parse_output(tool, output_instance))
        # TODO: parse outputs collections
        for output_def in output_defs:
            outputs[output_def.name] = output_def
        return outputs, odict()

    def _parse_output(self, tool, output_instance):
        name = output_instance.name
        # TODO: handle filters, actions, change_format
        output = ToolOutput( name )
        if "File" in output_instance.output_data_type:
            output.format = "_sniff_"
        else:
            output.format = "expression.json"
        output.change_format = []
        output.format_source = None
        output.metadata_source = ""
        output.parent = None
        output.label = None
        output.count = None
        output.filters = []
        output.tool = tool
        output.hidden = ""
        output.dataset_collector_descriptions = []
        output.actions = ToolOutputActionGroup( output, None )
        return output

    def parse_requirements_and_containers(self):
        containers = []
        docker_identifier = self._tool_proxy.docker_identifier()
        if docker_identifier:
            containers.append({"type": "docker",
                               "identifier": docker_identifier})
        return requirements.parse_requirements_from_dict(dict(
            requirements=[],  # TODO: enable via extensions
            containers=containers,
        ))

    def parse_profile(self):
        return "16.04"


class CwlPageSource(PageSource):

    def __init__(self, tool_proxy):
        cwl_instances = tool_proxy.input_instances()
        self._input_list = map(self._to_input_source, cwl_instances)

    def _to_input_source(self, input_instance):
        as_dict = input_instance.to_dict()
        return YamlInputSource(as_dict)

    def parse_input_sources(self):
        return self._input_list
