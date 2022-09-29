from .test_activation import ActivationTester
from .test_add import AddTester
from .test_back_propagation import BackPropTester
from .test_cycle_until_stable import UpdateNodeTester
from .test_dot import DotTester
from .test_predict import PredictTester
from .test_sub import SubTester
from .test_train import TrainTester
from .test_update_node import UpdateNodeTester

testSuite = [ActivationTester, AddTester, BackPropTester, UpdateNodeTester, DotTester, PredictTester, SubTester, TrainTester, UpdateNodeTester]
title = 'A6 (Extra Credit)'
