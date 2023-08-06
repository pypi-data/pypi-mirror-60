# from test_junkie.decorators import Suite, test, beforeClass
#
#
# @Suite(retry=2)
# class MySuite:
#
#     @beforeClass()
#     def before_class(self):
#         raise Exception("Derp!")
#
#     @test()
#     def test_1(self):
#         pass
from test_junkie.meta import meta, Meta

from test_junkie.decorators import Suite, test, beforeClass
from tests.junkie_suites.TestListener import TestListener


@Suite(retry=2,
       listener=TestListener,
       priority=2, feature="Store", owner="Mike", parameters=[1, 2])
class NewProductsSuite:

    ATT = 1
    #
    # @beforeClass()
    # def before_class1(self):
    #     if NewProductsSuite.ATT <= 1:
    #         NewProductsSuite.ATT += 1
    #         raise Exception("Derp")
    #
    # @test(component="Admin", tags=["store_management"], parameters=[10, 20], parallelized_parameters=True)
    # def edit_product(self, parameter, suite_parameter):
    #     print("edit_product")
    #     print(Meta.get_meta(self))
    #     Meta.update(self, name="apple2", actual="maging2")
    #     if parameter == 10:
    #         raise Exception("yo")
    #     print(Meta.get_meta(self))

    @test(component="Admin", tags=["store_management"])
    def archive_product(self):
        print(Meta.get_meta(self))
        # Meta.update(self, name="apple", actual="maging")
        # print(Meta.get_meta(self))


if "__main__" == __name__:
    from test_junkie.runner import Runner
    from test_junkie.debugger import LogJunkie

    LogJunkie.enable_logging(10)
    runner = Runner([NewProductsSuite])
    runner.run(test_multithreading_limit=4)
