import ast
import glob
import io
import json
import logging
import os
import shlex
import sys
from collections import defaultdict
from typing import List, Dict, Any, Optional
from flake8_flask.constants import PROJECT_ROOT
from flake8_flask.flask_base_visitor import FlaskBaseVisitor

from pyt.analysis.constraint_table import initialize_constraint_table
from pyt.analysis.fixed_point import analyse
from pyt.cfg import make_cfg
from pyt.core.ast_helper import generate_ast
from pyt.core.module_definitions import project_definitions
from pyt.core.project_handler import get_directory_modules, get_modules
from pyt.vulnerabilities import find_vulnerabilities
from pyt.vulnerabilities.vulnerability_helper import Vulnerability
from pyt.web_frameworks import FrameworkAdaptor, is_flask_route_function
from pyt.__main__ import retrieve_nosec_lines


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class FakeNode:  # Need this class to fake property accesses for flake8
    def __init__(self, lineno, col_offset):
        self.lineno = lineno
        self.col_offset = col_offset


class FlaskTaintVisitor(FlaskBaseVisitor):
    name = "r2c-flask-taint"

    def __init__(self, target):
        super(FlaskTaintVisitor, self).__init__()
        self.already_ran_once: bool = False
        self.target = target

    @classmethod
    def make_command(cls, target_files: List[str], definitions_file: str) -> List[str]:
        return ["-t", shlex.quote(definitions_file), "--json"] + [
            shlex.quote(f) for f in target_files
        ]

    def get_definitions_file_path(self) -> str:
        path = os.path.join(PROJECT_ROOT, "taint_definitions", f"{self.name}.pyt")
        if os.path.exists(path):
            return path
        raise FileNotFoundError(
            f"Definitions file '{os.path.abspath(path)}' does not exist"
        )

    def get_blackbox_file_path(self) -> str:
        path = os.path.join(PROJECT_ROOT, "taint_definitions", "blackbox.json")
        if os.path.exists(path):
            return path
        raise FileNotFoundError(
            f"Blackbox file '{os.path.abspath(path)}' does not exist"
        )

    # Override in subclass
    def is_call_dangerous_sink(self, call_node: ast.Call) -> bool:
        return False

    def find_target_files(self, path: str) -> List[str]:
        if os.path.isfile(path):
            return [path]

        # Get every .py file in the target directory
        # Useful so we get sources and sinks across files
        targets = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".py"):
                    targets.append(os.path.join(root, filename))
        return targets

    def violation_message(self, vuln: Vulnerability) -> str:
        source = vuln.get("source")
        sink = vuln.get("sink")
        return f"{self.name} found unsanitized user input flowing from '{source.get('label')}' in {source.get('path')}:{source.get('line_number')} to '{sink.get('label')}'"

    def filter_sanitized_vulnerabilities(self, vuln: Vulnerability) -> bool:
        # This is a poor man's sanitizer. I expected the behavior of pyt's
        # sanitizer to walk the chain and filter out nodes with sanitizer
        # labels. However, it tries to be smart about it and misses some
        # cases. This implemented the behavior I expected, but isn't very smart.
        vulnd = vuln.as_dict()
        with open(self.get_definitions_file_path(), "r") as fin:
            taint_definitions = json.load(fin)
        sanitizers = (
            taint_definitions.get("sinks", {})
            .get(vulnd.get("sink_trigger_word", []), [])
            .get("sanitisers", [])
        )
        logger.debug(f"Sanitizers: {sanitizers}")
        chain = vulnd.get("reassignment_nodes", [])
        for sanitizer in sanitizers:
            for node in chain:
                if sanitizer in node.get("label", ""):
                    logger.debug(
                        f"Found sanitized vulnerability. Sanitized by {sanitizer}. Vuln: {vulnd}"
                    )
                    return False
        return True

    def run_taint(self) -> List[Vulnerability]:
        if self.already_ran_once:
            logger.debug(
                f"{self.__class__.__name__} already ran taint once on this project. No need to run taint again."
            )
            return []

        logger.debug("Running pyt taint engine...")

        # Need to reset this because it will store entries from previous runs
        project_definitions.clear()

        # Reimplementation of https://github.com/python-security/pyt/blob/master/pyt/__main__.py#L65
        # I did this because it calls sys.exit(1) on L152
        target_files = self.find_target_files(self.target)
        logger.debug(f"Target files: {target_files}")

        nosec_lines = defaultdict(set)

        cfg_list = []
        for path in target_files:
            logger.debug(f"Processing {path}")
            nosec_lines[path] = retrieve_nosec_lines(path)
            directory = os.path.dirname(path)
            project_modules = get_modules(directory, False)
            local_modules = get_directory_modules(directory)
            tree = generate_ast(path)

            cfg = make_cfg(
                tree, project_modules, local_modules, path, False  # allow_local_imports
            )
            cfg_list = [cfg]

            FrameworkAdaptor(
                cfg_list, project_modules, local_modules, is_flask_route_function
            )

        initialize_constraint_table(cfg_list)
        logger.debug(f"Analysing.")
        analyse(cfg_list)
        logger.debug("Finding vulnerabilities")
        vulnerabilities = find_vulnerabilities(
            cfg_list,
            self.get_blackbox_file_path(),  # args.blackbox_mapping_file
            self.get_definitions_file_path(),  # args.trigger_word_file
            False,  # args.interactive
            nosec_lines,  # Nosec lines
        )
        logger.debug("Checking sanitizers")
        vulnerabilities = list(
            filter(self.filter_sanitized_vulnerabilities, vulnerabilities)
        )
        logger.debug(f"Found vulnerabilities: {[v.as_dict() for v in vulnerabilities]}")

        self.already_ran_once = True

        return vulnerabilities
