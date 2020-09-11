# from PySide2.QtGui import QGuiApplication

from qmlbot import QMLBot


RUNNER = """app = QGuiApplication(sys.argv)
qmlbot = QMLBot()
qmlbot.run()
"""



def test_runner(qtbot, dir_test):
    qmlbot = QMLBot(dir_test)
    assert qmlbot.run() == 0