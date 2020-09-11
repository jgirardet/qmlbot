import QtQuick 2.14
import QtQuick.Controls 2.14

Item {
    id: root
    property string moduleName
    property var temporaryObjects: []
    signal moduleFinished(string moduleName, var report)
    signal moduleReady()


    function compare(lhs, rhs) {
      let res = (lhs === rhs)
      if (!res) {
        let msg = `${lhs} != ${rhs}`
        let err = new Error(msg)
        throw err
      }
    }

    function createTemporaryObject(component, parent, properties={})  {
      if (component.status != 1) {
        let err = new Error(`${component.errorString()}`)
        throw err
      }
      let obj = component.createObject(parent, properties)

      temporaryObjects.push(obj)
      return obj
    }

    function collectTests() {
        let collected = new Map()
        for (const [key, value] of Object.entries(root)){
          if (key.startsWith("test_"))
            {
            collected.set(key, value)
            }

        }
        return collected
    }

    function runTests(collected) {
         let results = {}
          let err
        for (const [testName, fn] of collected)
          {
            err  = runOneTest(testName, fn)
            if (err) {
              results[testName] =  {"name": err.name, "message": err.message, "stack":err.stack}
            } else {
              results[testName] = {}
            }
          }
          return results
    }

    function init() {
    }

    function cleanup() {

    }

    function cleanTemporaryObjects() {
       for (const obj of temporaryObjects) {
          obj.destroy()
       }
        temporaryObjects = []


    }

    function runOneTest(testName, fn) {
        let res
        try {
          init()
          fn()
          }
        catch (err){
          res = err
        }
        cleanTemporaryObjects()
        showOneLineResult(testName, (res ? false : true))
        return res
    }

    function showOneLineResult(testName, success) {
      if (success) {
        qmlbot.ok(root.moduleName+":"+testName + ": ok")
      } else {
        qmlbot.error(root.moduleName+":"+testName + ": fail")
      }
    }

    function startFileSession(filename) {
      root.moduleName = filename
      let collected = collectTests()
      let results = runTests(collected)
      moduleFinished(root.moduleName, results)

    }
    Component.onCompleted: {
      root.moduleFinished.connect(qmlbot.onModuleFinished)
      root.moduleReady.connect(qmlbot.onModuleReady)
      qmlbot.startModule.connect(startFileSession)
      root.moduleReady()

    }


}
