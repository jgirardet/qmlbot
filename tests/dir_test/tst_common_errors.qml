import PythonTestCase 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15
import "../fake_project"

Item {
    id: item

    width: 600
    height: 400

    Rectangle {
        id: rec

        color: "blue"
        anchors.fill: parent
    }

    TestCase {

        property var obj

        function test_simple_comp_pass() {
            compare("a", "a");
        }

//        function test_error_in_test() {
//            //            print("debut 2");
//            obj.text = "FEZEFEZF zeFZ";
//            let a = 1;
//            obj.text = "FEZEFEZF zeFZ";
//            obj.text = "FEZEFEZF zeFZ";
//        }
//
//        function test_error_in_code() {
//        }
//
//        function test_A2() {
//            //            print("debut 2");
//            obj.text = "FEZEFEZF zeFZ";
//            compare("a", "a");
//        }
//
//        function test_A3_faile() {
//            //            print("debut 2");
//            obj.text = "FEZEFEZF zeFZ";
//        }



    }

}
