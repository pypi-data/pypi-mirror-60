import ast
import logging
import sys
from flake8_flask.flask_taint_visitor import FlaskTaintVisitor, FakeNode
from pyt.vulnerabilities.vulnerability_helper import Vulnerability

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)


class TaintedSystemCommandVisitor(FlaskTaintVisitor):
    name = "r2c-flask-tainted-system-command"

    def __init__(self, target):
        super(TaintedSystemCommandVisitor, self).__init__(target)

    def is_call_dangerous_sink(self, call_node: ast.Call) -> bool:
        # Make sure that the method belongs to the right module
        # subprocess.call
        # subprocess.Popen
        # os.system
        if self.is_node_method_alias_of(call_node, "system", "os"):
            return True
        elif self.is_node_method_alias_of(call_node, "call", "subprocess"):
            return True
        elif self.is_node_method_alias_of(call_node, "Popen", "subprocess"):
            return True
        return False

    def violation_message(self, vuln: Vulnerability) -> str:
        return (
            super(TaintedSystemCommandVisitor, self).violation_message(vuln)
            + "; possible command injection."
        )

    def visit_Call(self, call_node: ast.Call):
        if self.is_call_dangerous_sink(call_node):
            logger.debug(f"Found potentially dangerous sink: {ast.dump(call_node)}")
            vulnerabilities = self.run_taint()

            for result in vulnerabilities:
                vuln = result.as_dict()
                self.report_nodes.append(
                    {
                        "node": FakeNode(vuln.get("sink", {}).get("line_number"), 0),
                        "message": self.violation_message(vuln),
                    }
                )
