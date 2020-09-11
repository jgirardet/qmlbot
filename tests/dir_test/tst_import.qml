import PythonTestCase 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
//import "../fake_project/"

Item {
    id: item
    width: 600
    height: 400


    TestCase {

        function test_rien() {

        }

        function test_comp_next_to_testfile() {
            var comp = Qt.createComponent("CompNextToTest.qml");
            var obj = createTemporaryObject(comp, item);
        }

        function test_comp_from_relative_import() {
            var comp = Qt.createComponent("../fake_project/SimpleComp.qml");
            var obj = createTemporaryObject(comp, item);
        }

    }

}
