from py4j.java_gateway import JavaGateway
import code
gateway = JavaGateway()
test_class = gateway.entry_point.getTestClass()
print(test_class.getNArgs())
test_class.printArgs()
code.interact(local=locals())
