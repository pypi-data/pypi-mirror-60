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


class TaintedTemplateStringVisitor(FlaskTaintVisitor):
    name = "r2c-flask-tainted-template-string"

    def __init__(self, target):
        super(TaintedTemplateStringVisitor, self).__init__(target)

    def is_call_dangerous_sink(self, call_node: ast.Call) -> bool:
        logger.debug(ast.dump(call_node))
        if self.is_node_method_alias_of(call_node, "render_template_string", "flask"):
            return True
        return False

    def violation_message(self, vuln: Vulnerability) -> str:
        return (
            super(TaintedTemplateStringVisitor, self).violation_message(vuln)
            + "; possible server-side template injection (SSTI) or cross-site scripting (XSS)."
        )

    def condition_template_modified(
        self, template_variable_name: str, vuln: Vulnerability
    ) -> bool:
        # We only want to look for situations in which the template itself has been altered.
        # Tainted variables into context variables are autoescaped.
        return template_variable_name in vuln.get("source", {}).get("label") or any(
            [
                template_variable_name in re_node.get("label", "")
                for re_node in vuln.get("reassignment_nodes", [])
            ]
        )

    def visit_Call(self, call_node: ast.Call):
        if self.is_call_dangerous_sink(call_node):
            logger.debug(f"Found potentially dangerous sink: {ast.dump(call_node)}")
            vulnerabilities = self.run_taint()

            report_condition = (
                lambda vuln: False
            )  # Query: Should I assume True or False?

            arg0 = call_node.args[0]
            if isinstance(arg0, ast.Name):
                template_variable_name = arg0.id
                report_condition = lambda vuln: self.condition_template_modified(
                    template_variable_name, vuln
                )
            elif isinstance(arg0, ast.BinOp):  # Old-style format strings
                report_condition = lambda vuln: True
            elif isinstance(
                arg0, ast.Call
            ):  # Middle-style format strings, e.g., "hi{}".format(x)
                if isinstance(arg0.func, ast.Attribute):
                    if arg0.func.attr == "format":
                        report_condition = lambda vuln: True
            elif isinstance(arg0, ast.Str):
                logger.debug(
                    "Template is a static string; can only be injected with context variables, and render_template_string escapes by default. Will not report this node."
                )
                return

            for result in vulnerabilities:
                vuln = result.as_dict()
                if report_condition(vuln):
                    self.report_nodes.append(
                        {
                            "node": FakeNode(
                                vuln.get("sink", {}).get("line_number"), 0
                            ),
                            "message": self.violation_message(vuln),
                        }
                    )
