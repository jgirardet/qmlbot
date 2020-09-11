import PythonTestCase 1.0
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: item

    width: 600
    height: 400

    TestCase {

        function test_subdir1_B() {
            compare("a", "a");
        }

    }

}
