import re
import shutil
import sys
from pathlib import Path
from string import Template
from typing import List, Dict

from PySide2.QtCore import QByteArray, QObject, Slot, Signal
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from colorama import init as colorama_init
from termcolor import colored, cprint


WINDOW_QML = Template(
    """import QtQuick 2.14
import QtQuick.Window 2.14
Window {
    title: "test"
    objectName: "mainWindow"
    width: 800
    height: 600
    visible: true
    
    
    Loader {
        id: loader
        Component.onCompleted: {
            setSource("${test_file}")
            
        }
    }
}
"""
)





class QMLBot(QObject):

    file_line_number = re.compile(r".+\@.+/(?P<module_name>.+\.qml):(?P<line_nb>\d+)")

    sourceChanged = Signal()
    startModule = Signal(str)

    def __init__(self, root=None):
        super().__init__()
        self.root = Path(root) if root else Path(__file__).parent
        self.modules = self._collect_test_modules()
        self.keys = list(self.modules.keys())

        self.engine: QQmlApplicationEngine  # self._setup_engine()
        self.currentModule: str = None
        self.results = {}
        self.test_count = 0
        self.fail_count = 0

    def run(self):
        """
        Run all the tests and generate a report
        :return: 0 if no error.
        """
        colorama_init()
        self.info("Starting qml test session")
        self._run_test_suite()
        self._do_report()
        return self.fail_count

    """
    This part is about general class setup
    """

    def _collect_test_modules(self) -> Dict[str, Path]:
        allfiles = sorted(list(self.root.glob("**/tst_*.qml")))
        return {p.name: p for p in allfiles}

    def _setup_engine(self):
        engine = QQmlApplicationEngine()
        engine.setImportPathList([str(Path(__file__).parent)] + engine.importPathList())
        engine.rootContext().setContextProperty("qmlbot", self)
        return engine

    def _run_module(self, module: str):
        content = WINDOW_QML.substitute(
            {"test_file": str(self.modules[module])}
        ).encode()
        self.currentModule = module
        self.engine.loadData(QByteArray(content))  # execute les tests

    def _run_test_suite(self):
        for module in self.modules:
            self._test_one_module(module)

    def _test_one_module(self, module: str):
        self.engine = self._setup_engine()
        self._run_module(module)
        self._destroy_module()

    def _destroy_module(self):
        del self.engine
        self.engine = self._setup_engine()

    """
    this part is about Reporting
    """

    def _do_report(self):
        report = self._createReport()
        self._show_report(report)

    def _createReport(self):
        text_report = []
        total_columns = shutil.get_terminal_size().columns
        for module, tests in self.results.items():
            for test, error in tests.items():
                self.test_count += 1
                if error:
                    text_report.append(
                        (
                            f" {module}:{test }".center(total_columns, "-"),
                            "blue",
                            ["bold"],
                        )
                    )
                    self.fail_count += 1

                    line = self._getErrorLineInStack(module, error["stack"])
                    context = self._pick_error_context(
                        module, test, line, error["message"]
                    )
                    # text_report.append(f"{error['message']}")
                    text_report.extend(context)
                    text_report.extend(
                        self._format_stack_trace(error["stack"], test, cut=True)
                    )
                    text_report.append(("", "white"))
        return text_report

    def _pick_error_context(self, module: str, test: str, line_no: int, msg: str):

        file = self.modules[module].read_text()
        res = []
        open_brace_count = 0
        close_brace_count = 0
        # print("boucle", test)
        line_index = None
        for n, line in enumerate(file.splitlines(keepends=False), start=1):
            if re.match(rf"\s*function {test}\(", line):
                if line_index is None:
                    line_index = n
            if line_index is not None:
                open_brace_count += line.count("{")
                close_brace_count += line.count("}")
                if open_brace_count == close_brace_count and open_brace_count > 0:
                    break
            if line_index is not None:
                if n == line_no:
                    res.append((f"{n}: " + line[:-1] + f" Error ===>  {msg}", "red"))
                    print((f"{n}: " + line[:-1] + f" Error ===>  {msg}").encode())
                else:
                    res.append((f"{n}: " + line, "yellow"))

        return res

    def _format_stack_trace(self, stack: str, test_name: str, cut=False):
        # print(stack)
        res = []
        for line in stack.splitlines(keepends=False):
            fn, path, line = re.search(r"(.+)\@(.+\.qml)?\:(.+)", line).groups()
            # print(fn, path, line)
            string = f"In file {path} at line {line} in function {fn}"
            res.append((string, "white"))
            if cut and fn == test_name:
                break
        # print(res)
        return res

    def _show_report(self, report: List[str]):
        # print(shutil.get_terminal_size())
        total_columns = shutil.get_terminal_size().columns
        report_color = "red" if self.fail_count else "green"
        cprint(
            " Tests Report ".center(total_columns, "="), report_color, attrs=["bold"],
        )
        print("\n")
        for line in report:
            cprint(line[0], line[1])

        failed = f"{self.fail_count} failed," if self.fail_count else ""
        passed = f"{self.test_count-self.fail_count} passed"
        cprint(
            f" QML Tests: {failed}{passed} ".center(total_columns, "="),
            report_color,
            attrs=["bold"],
        )

    def _getErrorLineInStack(self, module_name: str, stack: str):
        for line in self.file_line_number.finditer(stack):
            group = line.groupdict()
            try:
                if group["module_name"] == module_name:
                    return int(group["line_nb"])
            except KeyError:
                continue

        return

    """
    This part is about slots and properties
    """

    @Slot(str, "QVariantMap")
    def onModuleFinished(self, module: str, results: dict):
        self.results[module] = results

    @Slot()
    def onModuleReady(self):
        self.startModule.emit(self.currentModule)

    @Slot(str)
    def info(self, msg: str):
        cprint(msg, "blue")

    @Slot(str)
    def error(self, msg: str):
        cprint(msg, "red")

    @Slot(str)
    def ok(self, msg: str):
        cprint(msg, "green")


if __name__ == "__main__":

    app = QGuiApplication(sys.argv)
    #
    qmlbot = QMLBot(Path(__file__).parents[1])
    qmlbot.run()

    # sys.exit(app.exec_())
