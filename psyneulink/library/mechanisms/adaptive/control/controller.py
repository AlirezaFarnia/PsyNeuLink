# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# *************************************************  EVCControlMechanism ******************************************************

"""

Overview
--------

An EVCControlMechanism is a `ControlMechanism <ControlMechanism>` that regulates it `ControlSignals <ControlSignal>` in
order to optimize the performance of the System to which it belongs.  EVCControlMechanism is one of the most
powerful, but also one of the most complex components in PsyNeuLink.  It is designed to implement a form of the
Expected Value of Control (EVC) Theory described in `Shenhav et al. (2013)
<https://www.ncbi.nlm.nih.gov/pubmed/23889930>`_, which provides useful background concerning the purpose and
structure of the EVCControlMechanism.

An EVCControlMechanism is similar to a standard `ControlMechanism`, with the following exceptions:

  * it can only be assigned to a System as its `controller <System.controller>`, and not in any other capacity
    (see `ControlMechanism_System_Controller`);
  ..
  * it has several specialized functions that are used to search over the `allocations <ControlSignal.allocations>`\\s
    of its its `ControlSignals <ControlSignal>`, and evaluate the performance of its `system
    <EVCControlMechanism.composition>`; by default, it simulates its `system <EVCControlMechanism.composition>` and evaluates
    its performance under all combinations of ControlSignal values to find the one that optimizes the `Expected
    Value of Control <EVCControlMechanism_EVC>`, however its functions can be customized or replaced to implement
    other optimization procedures.
  ..
  * it creates a specialized set of `prediction Mechanisms` EVCControlMechanism_Prediction_Mechanisms` that are used to
    simulate the performnace of its `system <EVCControlMechanism.system>`.

.. _EVCControlMechanism_EVC:

*Expected Value of Control (EVC)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The EVCControlMechanism uses it `function <EVCControlMechanism.function>` to select an `allocation_policy` for its
`system <EVCControlMechanism.system>`.  In the `default configuration <EVCControlMechanism_Default_Configuration>`,
an EVCControlMechanism carries out an exhaustive evaluation of allocation policies, simulating its `system
<EVCControlMechanism.system>` under each, and using an `ObjectiveMechanism` and several `auxiliary functions
<EVCControlMechanism_Functions>` to calculate the **expected value of control (EVC)** for each `allocation_policy`:
a cost-benefit analysis that weighs the `cost <ControlSignal.cost> of the ControlSignals against the outcome of the
`system <EVCControlMechanism.system>` \\s performance for a given `allocation_policy`. The EVCControlMechanism
selects the `allocation_policy` that generates the maximum EVC, and implements that for the next `TRIAL`. Each step
of this procedure can be modified, or replaced entirely, by assigning custom functions to corresponding parameters of
the EVCControlMechanism, as described `below <EVCControlMechanism_Functions>`.

.. _EVCControlMechanism_Creation:

Creating an EVCControlMechanism
------------------------

An EVCControlMechanism can be created in any of the ways used to `create a ControlMechanism
<ControlMechanism_Creation>`; it is also created automatically when a `System` is created and the EVCControlMechanism
class is specified in the **controller** argument of the System's constructor (see `System_Creation`).  The
ObjectiveMechanism, the OutputStates it monitors and evaluates, and the parameters controlled by an
EVCControlMechanism can be specified in the standard way for a ControlMechanism (see
`ControlMechanism_ObjectiveMechanism` and `ControlMechanism_Control_Signals`, respectively).

.. note::
   Although an EVCControlMechanism can be created on its own, it can only be assigned to, and executed within a `System`
   as the System's `controller <System.controller>`.

When an EVCControlMechanism is assigned to, or created by a System, it is assigned the OutputStates to be monitored and
parameters to be controlled specified for that System (see `System_Control`), and a `prediction Mechanism
<EVCControlMechanism_Prediction_Mechanisms>` is created for each `ORIGIN` Mechanism in the `system
<EVCControlMechanism.system>`. The prediction Mechanisms are assigned to the EVCControlMechanism's
`prediction_mechanisms` attribute. The OutputStates used to determine an EVCControlMechanism’s allocation_policy and
the parameters it controls can be listed using its show method. The EVCControlMechanism and the Components
associated with it in its `system <EVCControlMechanism.system>` can be displayed using the System's
`System.show_graph` method with its **show_control** argument assigned as `True`

An EVCControlMechanism that has been constructed automatically can be customized by assigning values to its
attributes (e.g., those described above, or its `function <EVCControlMechanism.function>` as described under
`EVCControlMechanism_Default_Configuration `below).


.. _EVCControlMechanism_Structure:

Structure
---------

An EVCControlMechanism must belong to a `System` (identified in its `system <EVCControlMechanism.system>` attribute).
In addition to the standard Components of a `ControlMechanism`, has a specialized set of `prediction mechanisms
<EVCControlMechanism_Prediction_Mechanisms>` and `functions <EVCControlMechanism_Functions>` that it uses to simulate
and evaluate the performance of its `system <EVCControlMechanism.system>` under the influence of different values of
its `ControlSignals <EVCControlMechanism_ControlSignals>`.  Each of these specialized Components is described below.

.. _EVCControlMechanism_Input:

*Input*
~~~~~~~

.. _EVCControlMechanism_ObjectiveMechanism:

ObjectiveMechanism
^^^^^^^^^^^^^^^^^^

Like any ControlMechanism, an EVCControlMechanism receives its input from the *OUTCOME* `OutputState
<ObjectiveMechanism_Output>` of an `ObjectiveMechanism`, via a MappingProjection to its `primary InputState
<InputState_Primary>`.  The ObjectiveFunction is listed in the EVCControlMechanism's `objective_mechanism
<EVCControlMechanism.objective_mechanism>` attribute.  By default, the ObjectiveMechanism's function is a
`LinearCombination` function with its `operation <LinearCombination.operation>` attribute assigned as *PRODUCT*;
this takes the product of the `value <OutputState.value>`\\s of the OutputStates that it monitors (listed in its
`monitored_output_states <ObjectiveMechanism.monitored_output_states>` attribute.  However, this can be customized
in a variety of ways:

    * by specifying a different `function <ObjectiveMechanism.function>` for the ObjectiveMechanism
      (see `Objective Mechanism Examples <ObjectiveMechanism_Weights_and_Exponents_Example>` for an example);
    ..
    * using a list to specify the OutputStates to be monitored  (and the `tuples format
      <InputState_Tuple_Specification>` to specify weights and/or exponents for them) in the
      **objective_mechanism** argument of the EVCControlMechanism's constructor;
    ..
    * using the  **monitored_output_states** argument for an ObjectiveMechanism specified in the `objective_mechanism
      <EVCControlMechanism.objective_mechanism>` argument of the EVCControlMechanism's constructor;
    ..
    * specifying a different `ObjectiveMechanism` in the **objective_mechanism** argument of the EVCControlMechanism's
      constructor. The result of the `objective_mechanism <EVCControlMechanism.objective_mechanism>`'s `function
      <ObjectiveMechanism.function>` is used as the outcome in the calculations described below.

    .. _EVCControlMechanism_Objective_Mechanism_Function_Note:

    .. note::
       If a constructor for an `ObjectiveMechanism` is used for the **objective_mechanism** argument of the
       EVCControlMechanism's constructor, then the default values of its attributes override any used by the
       EVCControlMechanism for its `objective_mechanism <EVCControlMechanism.objective_mechanism>`.  In particular,
       whereas an EVCControlMechanism uses the same default `function <ObjectiveMechanism.function>` as an
       `ObjectiveMechanism` (`LinearCombination`), it uses *PRODUCT* rather than *SUM* as the default value of the
       `operation <LinearCombination.operation>` attribute of the function.  As a consequence, if the constructor for
       an ObjectiveMechanism is used to specify the EVCControlMechanism's **objective_mechanism** argument,
       and the **operation** argument is not specified, *SUM* rather than *PRODUCT* will be used for the
       ObjectiveMechanism's `function <ObjectiveMechanism.function>`.  To ensure that *PRODUCT* is used, it must be
       specified explicitly in the **operation** argument of the constructor for the ObjectiveMechanism (see 1st
       example under `System_Control_Examples`).

The result of the EVCControlMechanism's `objective_mechanism <EVCControlMechanism.objective_mechanism>` is used by
its `function <ObjectiveMechanism.function>` to evaluate the performance of its `system <EVCControlMechanism.system>`
when computing the `EVC <EVCControlMechanism_EVC>`.


.. _EVCControlMechanism_Prediction_Mechanisms:

Prediction Mechanisms
^^^^^^^^^^^^^^^^^^^^^

These are used to provide input to the `system <EVCControlMechanism.system>` if the EVCControlMechanism's
`function <EVCControlMechanism.function>` (`ControlSignalGridSearch2`) `simulates its execution
<EVCControlMechanism_Default_Configuration>` to evaluate the EVC for a given `allocation_policy`.  When an
EVCControlMechanism is created, a prediction Mechanism is created for each `ORIGIN` Mechanism in its `system
<EVCControlMechanism.system>`, and are listed in the EVCControlMechanism's `prediction_mechanisms
<EVCControlMechanism.prediction_mechanisms>` attribute in the same order as the `ORIGIN` Mechanisms are
listed in the `system <EVCControlMechanism.system>`\\'s `origin_mechanisms <System.origin_mechanisms>` attribute.
For each `Projection <Projection>` received by an `ORIGIN` Mechanism, a `MappingProjection` from the same source is
created that projects to the corresponding prediction Mechanism.  By default, the `PredictionMechanism` subclass  is
used for all prediction mechanisms, which calculates an exponentially weighted time-average of its input over (
non-simuated) trials, that is provided as input to the corresponding `ORIGIN` Mechanism on each simulated trial.
However, any other type of Mechanism can be used as a prediction mechanism, so long as it has the same number of
`InputStates <InputState>` as the `ORIGIN` Mechanism to which it corresponds, and an `OutputState` corresponding to
each.  The default type is a `PredictionMechanism`, that calculates an exponentially weighted time-average of its
input. The prediction mechanisms can be customized using the *prediction_mechanisms* argument of the
EVCControlMechanism's constructor, which can be specified using any of the following formats:

  * **Mechanism** -- convenience format for cases in which the EVCControlMechanism's `system
    <EVCControlMechanism.system>` has a single `ORIGIN` Mechanism;  the Mechanism must have the same number of
    `InputStates <InputState>` as the `system <EVCControlMechanism.system>`\\'s `ORIGIN` Mechanism, and
    an `OutputState` for each.
  ..
  * **Mechanism subclass** -- used as the class for all prediction mechanisms; a default instance of that class
    is created for each prediction mechanism, with a number of InputStates and OutputStates equal to the number of
    InputStates of the `ORIGIN` Mechanism to which it corresponds.
  ..
  * **dict** -- a `parameter specification dictionary <ParameterState_Specification>` specifying the parameters to be
    assigned to all prediction mechanisms, all of which are instances of a `PredictionMechanism` (thus, the parameters
    specified must be appropriate for a PredictionMechanism).
  ..
  * **2-item tuple:** *(Mechanism subclass, dict)* -- the Mechanism subclass, and parameters specified in
    the `parameter specification dictionary <ParameterState_Specification>`, are used for all prediction mechanisms.
  ..
  * **list** -- its length must equal the number of `ORIGIN` Mechanisms in the EVCControlMechanism's `system
    <EVCControlMechanism.system>` each item must be a Mechanism, a subclass of one, or a 2-item tuple (see above),
    that is used as the specification for the prediction Mechanism for the corresponding `ORIGIN` Mechanism listed in
    the System's `origin_mechanisms <System.origin_mechanisms>` attribute.

The prediction mechanisms for an EVCControlMechanism are listed in its `prediction_mechanisms` attribute.

.. _EVCControlMechanism_Functions:

*Function*
~~~~~~~~~~

By default, the primary `function <EVCControlMechanism.function>` is `ControlSignalGridSearch2` (see
`EVCControlMechanism_Default_Configuration`), that systematically evaluates the effects of its ControlSignals on the
performance of its `system <EVCControlMechanism.system>` to identify an `allocation_policy
<EVCControlMechanism.allocation_policy>` that yields the highest `EVC <EVCControlMechanism_EVC>`.  However,
any function can be used that returns an appropriate value (i.e., that specifies an `allocation_policy` for the
number of `ControlSignals <EVCControlMechanism_ControlSignals>` in the EVCControlMechanism's `control_signals`
attribute, using the correct format for the `allocation <ControlSignal.allocation>` value of each ControlSignal).
In addition to its primary `function <EVCControlMechanism.function>`, an EVCControlMechanism has several auxiliary
functions, that can be used by its `function <EVCControlMechanism.function>` to calculate the EVC to select an
`allocation_policy` with the maximum EVC among a range of policies specified by its ControlSignals.  The default
set of functions and their operation are described in the section that follows;  however, the EVCControlMechanism's
`function <EVCControlMechanism.function>` can call any other function to customize how the EVC is calcualted.

.. _EVCControlMechanism_Default_Configuration:

Default Configuration of EVC Function and its Auxiliary Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In its default configuration, an EVCControlMechanism simulates and evaluates the performance of its `system
<EVCControlMechanism.system>` under a set of allocation_policies determined by the `allocation_samples
<ControlSignal.allocation_samples>` attributes of its `ControlSignals <EVCControlMechanism_ControlSignals>`, and
implements (for the next `TRIAL` of execution) the one that generates the maximum `EVC <EVCControlMechanism_EVC>`.
This is carried out by the EVCControlMechanism's default `function <EVCControlMechanism.function>` and three
auxiliary functions, as described below.

The default `function <EVCControlMechanism.function>` of an EVCControlMechanism is `ControlSignalGridSearch2`. It
identifies the `allocation_policy` with the maximum `EVC <EVCControlMechanism_EVC>` by a conducting an exhaustive
search over every possible `allocation_policy`— that is, all combinations of `allocation <ControlSignal.allocation>`
values for its `ControlSignals <EVCControlMechanism_ControlSignals>`, where the `allocation
<ControlSignal.allocation>` values sampled for each ControlSignal are determined by its `allocation_samples`
attribute.  For each `allocation_policy`, the EVCControlMechanism executes the `system <EVCControlMechanism.system>`,
evaluates the `EVC <EVCControlMechanism_EVC>` for that policy, and returns the `allocation_policy` that yields the
greatest EVC value. The following steps are used to calculate the EVC for each `allocation_policy`:

  * **Implement the policy and simulate the System** - assign the `allocation <ControlSignal.allocation>` that the
    selected `allocation_policy` specifies for each ControlSignal, and then simulate the `system
    <EVCControlMechanism.composition>` using the corresponding parameter values by calling the System's `run_simulation
    <System.run_simulation>` method; this uses the `value <PredictionMechanism.value>` of eacah of the
    EVCControlMechanism's `prediction_mechanisms <EVCControlMechanism.prediction_mechanisms>` as input to the
    corresponding `ORIGIN` Mechanisms of its `system <EVCControlMechanism.composition>` (see `PredictionMechanism`).  The
    values of all :ref:`stateful attributes` of 'Components` in the System are :ref:`re-initialized` to the same value
    prior to each simulation, so that the results for each `allocation_policy <EVCControlMechanism.allocation_policy>`
    are based on the same initial conditions.  Each simulation includes execution of the EVCControlMechanism's
    `objective_mechanism`, which provides the result to the EVCControlMechanism.  If `system
    <EVCControlMechanism.composition>`\\.recordSimulationPref is `True`, the results of each simulation are appended to the
    `simulation_results <System.simulation_results>` attribute of `system <EVCControlMechanism.composition>`.
  |
  * **Evaluate the System's performance** - this is carried out by the EVCControlMechanism's `objective_mechanism
    <EVCControlMechanism.objective_mechanism>`, which is executed as part of the simulation of the System.  The
    `function <ObjectiveMechanism.function>` for a default ObjectiveMechanism is a `LinearCombination` Function that
    combines the `value <OutputState.value>`\\s of the OutputStates listed in the EVCControlMechanism's
    `monitored_output_states <EVCControlMechanism.monitored_output_states>` attribute (and the `objective_mechanism
    <EVCControlMechanism.objective_mechanism>`'s `monitored_output_states <ObjectiveMechanism.monitored_output_states>`
    attribute) by taking their elementwise (Hadamard) product.  However, this behavior can be customized in a variety
    of ways, as described `above <EVCControlMechanism_ObjectiveMechanism>`.
  |
  * **Calculate EVC** - call the EVCControlMechanism's `value_function <EVCControlMechanism.value_function>` passing it
    the outcome (received from the `objective_mechanism`) and a list of the `costs <ControlSignal.cost>` \\s of its
    `ControlSignals <EVCControlMechanism_ControlSignals>`.  The default `value_function
    <EVCControlMechanism.value_function>` calls two additional auxiliary functions, in the following order:
    |
    - `cost_function <EVCControlMechanism.cost_function>`, which sums the costs;  this can be configured to weight
      and/or exponentiate individual costs (see `cost_function <EVCControlMechanism.cost_function>` attribute);
    |
    - `combine_outcome_and_cost_function <EVCControlMechanism.combine_outcome_and_cost_function>`, which subtracts the
      sum of the costs from the outcome to generate the EVC;  this too can be configured (see
      `combine_outcome_and_cost_function <EVCControlMechanism.combine_outcome_and_cost_function>`).

In addition to modifying the default functions (as noted above), any or all of them can be replaced with a custom
function to modify how the `allocation_policy <EVCControlMechanism.allocation_policy>` is determined, so long as the
custom function accepts arguments and returns values that are compatible with any other functions that call that
function (see note below).

.. _EVCControlMechanism_Calling_and_Assigning_Functions:

    .. note::
       The `EVCControlMechanism auxiliary functions <EVCControlMechanism_Functions>` described above are all
       implemented as PsyNeuLink `Functions <Function>`.  Therefore, to call a function itself, it must be referenced
       as ``<EVCControlMechanism>.<function_attribute>.function``.  A custom function assigned to one of the auxiliary
       functions can be either a PsyNeuLink `Function <Function>`, or a generic python function or method (including
       a lambda function).  If it is one of the latter, it is automatically "wrapped" as a PsyNeuLink `Function
       <Function>` (specifically, it is assigned as the `function <UserDefinedFunction.function>` attribute of a
       `UserDefinedFunction` object), so that it can be referenced and called in the same manner as the default
       function assignment. Therefore, once assigned, it too must be referenced as
       ``<EVCControlMechanism>.<function_attribute>.function``.

.. _EVCControlMechanism_ControlSignals:

*ControlSignals*
~~~~~~~~~~~~~~~~

The OutputStates of an EVCControlMechanism (like any `ControlMechanism`) are a set of `ControlSignals
<ControlSignal>`, that are listed in its `control_signals <EVCControlMechanism.control_signals>` attribute (as well as
its `output_states <ControlMechanism.output_states>` attribute).  Each ControlSignal is assigned a  `ControlProjection`
that projects to the `ParameterState` for a parameter controlled by the EVCControlMechanism.  Each ControlSignal is
assigned an item of the EVCControlMechanism's `allocation_policy`, that determines its `allocation
<ControlSignal.allocation>` for a given `TRIAL` of execution.  The `allocation <ControlSignal.allocation>` is used by
a ControlSignal to determine its `intensity <ControlSignal.intensity>`, which is then assigned as the `value
<ControlProjection.value>` of the ControlSignal's ControlProjection.   The `value <ControlProjection>` of the
ControlProjection is used by the `ParameterState` to which it projects to modify the value of the parameter (see
`ControlSignal_Modulation` for description of how a ControlSignal modulates the value of a parameter it controls).
A ControlSignal also calculates a `cost <ControlSignal.cost>`, based on its `intensity <ControlSignal.intensity>`
and/or its time course. The `cost <ControlSignal.cost>` is included in the evaluation that the EVCControlMechanism
carries out for a given `allocation_policy`, and that it uses to adapt the ControlSignal's `allocation
<ControlSignal.allocation>` in the future.  When the EVCControlMechanism chooses an `allocation_policy` to evaluate,
it selects an allocation value from the ControlSignal's `allocation_samples <ControlSignal.allocation_samples>`
attribute.


.. _EVCControlMechanism_Execution:

Execution
---------

An EVCControlMechanism must be the `controller <System.controller>` of a System, and as a consequence it is always the
last `Mechanism <Mechanism>` to be executed in a `TRIAL` for its `system <EVCControlMechanism.composition>` (see `System
Control <System_Execution_Control>` and `Execution <System_Execution>`). When an EVCControlMechanism is executed,
it updates the value of its `prediction_mechanisms` and `objective_mechanism`, and then calls its `function
<EVCControlMechanism.function>`, which determines and implements the `allocation_policy` for the next `TRIAL` of its
`system <EVCControlMechanism.composition>`\\s execution.  The default `function <EVCControlMechanism.function>` executes
the following steps (described in greater detailed `above <EVCControlMechanism_Default_Configuration>`):

* Samples every allocation_policy (i.e., every combination of the `allocation` \\s specified for the
  EVCControlMechanism's ControlSignals specified by their `allocation_samples` attributes);  for each
  `allocation_policy`, it:

  * Runs a simulation of the EVCControlMechanism's `system <EVCControlMechanism.composition>` with the parameter values
    specified by that `allocation_policy`, by calling the system's  `run_simulation <System.run_simulation>` method;
    each simulation uses inputs provided by the EVCControlMechanism's `prediction_mechanisms
    <EVCControlMechanism.prediction_mechanisms>` and includes execution of its `objective_mechanism`, which provides
    its result to the EVCControlMechanism.

  * Calls the EVCControlMechanism's `value_function <EVCControlMechanism.value_function>`, which in turn calls
    EVCControlMechanism's `cost_function <EVCControlMechanism.cost_function>` and `combine_outcome_and_cost_function
    <EVCControlMechanism.combine_outcome_and_cost_function>` to evaluate the EVC for that `allocation_policy`.

* Selects and returns the `allocation_policy` that generates the maximum EVC value.

This procedure can be modified by specifying a custom function for any or all of the `functions
<EVCControlMechanism_Functions>` referred to above.


.. _EVCControlMechanism_Examples:

Example
-------

The following example implements a System with an EVCControlMechanism (and two processes not shown)::


    >>> import psyneulink as pnl                                                        #doctest: +SKIP
    >>> myRewardProcess = pnl.Process(...)                                              #doctest: +SKIP
    >>> myDecisionProcess = pnl.Process(...)                                            #doctest: +SKIP
    >>> mySystem = pnl.System(processes=[myRewardProcess, myDecisionProcess],           #doctest: +SKIP
    ...                       controller=pnl.EVCControlMechanism,                       #doctest: +SKIP
    ...                       monitor_for_control=[Reward,                              #doctest: +SKIP
    ...                                            pnl.DDM_OUTPUT.DECISION_VARIABLE,    #doctest: +SKIP
    ...                                            (pnl.RESPONSE_TIME, 1, -1)],         #doctest: +SKIP

It uses the System's **monitor_for_control** argument to assign three OutputStates to be monitored.  The first one
references the Reward Mechanism (not shown);  its `primary OutputState <OutputState_Primary>` will be used by default.
The second and third use keywords that are the names of outputStates of a  `DDM` Mechanism (also not shown).
The last one (RESPONSE_TIME) is assigned a weight of 1 and an exponent of -1. As a result, each calculation of the EVC
computation will multiply the value of the primary OutputState of the Reward Mechanism by the value of the
*DDM_DECISION_VARIABLE* OutputState of the DDM Mechanism, and then divide that by the value of the *RESPONSE_TIME*
OutputState of the DDM Mechanism.

See `ObjectiveMechanism <ObjectiveMechanism_Monitored_Output_States_Examples>` for additional examples of how to specify it's
**monitored_output_states** argument, `ControlMechanism <ControlMechanism_Examples>` for additional examples of how to
specify ControlMechanisms, and `System <System_Examples>` for how to specify the `controller <System.controller>`
of a System.

.. _EVCControlMechanism_Class_Reference:

Class Reference
---------------

"""

import numpy as np
import typecheck as tc

from psyneulink.components.component import Param, function_type
from psyneulink.components.functions.function import ModulationParam, _is_modulation_param, Buffer, ValueFunction2, \
    ControlSignalGridSearch2
from psyneulink.components.mechanisms.adaptive.control.controlmechanism import ControlMechanism
from psyneulink.components.mechanisms.mechanism import Mechanism
from psyneulink.components.mechanisms.processing.objectivemechanism import ObjectiveMechanism
from psyneulink.components.shellclasses import Function
from psyneulink.components.states.modulatorysignals.controlsignal import ControlSignalCosts
from psyneulink.components.states.outputstate import OutputState
from psyneulink.components.states.parameterstate import ParameterState
from psyneulink.globals.context import ContextFlags
from psyneulink.globals.keywords import CONTROL, CONTROLLER, COST_FUNCTION, EVC_MECHANISM,\
    INIT_FUNCTION_METHOD_ONLY, PARAMETER_STATES, PREDICTION_MECHANISM, PREDICTION_MECHANISMS, SUM
from psyneulink.globals.preferences.componentpreferenceset import is_pref_set
from psyneulink.globals.preferences.preferenceset import PreferenceLevel
from psyneulink.globals.utilities import ContentAddressableList, is_iterable
from psyneulink.library.subsystems.evc.evcauxiliary import PredictionMechanism

__all__ = [
    'Controller', 'EVCError',
]


class EVCError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class Controller(ControlMechanism):
    """EVCControlMechanism(                                            \
    system=True,                                                       \
    objective_mechanism=None,                                          \
    prediction_mechanisms=PredictionMechanism,                         \
    function=ControlSignalGridSearch2                                   \
    value_function=ValueFunction2,                                      \
    cost_function=LinearCombination(operation=SUM),                    \
    combine_outcome_and_cost_function=LinearCombination(operation=SUM) \
    save_all_values_and_policies=:keyword:`False`,                     \
    control_signals=None,                                              \
    params=None,                                                       \
    name=None,                                                         \
    prefs=None)

    Subclass of `ControlMechanism <ControlMechanism>` that optimizes the `ControlSignals <ControlSignal>` for a
    `System`.

    COMMENT:
        Class attributes:
            + componentType (str): System Default Mechanism
            + paramClassDefaults (dict):
                + SYSTEM (System)
                + MONITORED_OUTPUT_STATES (list of Mechanisms and/or OutputStates)

        Class methods:
            None

       **********************************************************************************************

       PUT SOME OF THIS STUFF IN ATTRIBUTES, BUT USE DEFAULTS HERE

        # - specification of System:  required param: SYSTEM
        # - kwDefaultController:  True =>
        #         takes over all unassigned ControlProjections (i.e., without a sender) in its System;
        #         does not take monitored states (those are created de-novo)
        # TBI: - CONTROL_PROJECTIONS:
        #         list of projections to add (and for which outputStates should be added)

        # - input_states: one for each performance/environment variable monitored

        ControlProjection Specification:
        #    - wherever a ControlProjection is specified, using kwEVC instead of CONTROL_PROJECTION
        #     this should override the default sender SYSTEM_DEFAULT_CONTROLLER in ControlProjection._instantiate_sender
        #    ? expclitly, in call to "EVC.monitor(input_state, parameter_state=NotImplemented) method

        # - specification of function: default is default allocation policy (BADGER/GUMBY)
        #   constraint:  if specified, number of items in variable must match number of input_states in INPUT_STATES
        #                  and names in list in kwMonitor must match those in INPUT_STATES

       **********************************************************************************************

       NOT CURRENTLY IN USE:

        system : System
            System for which the EVCControlMechanism is the controller;  this is a required parameter.

        default_variable : Optional[number, list or np.ndarray] : `defaultControlAllocation <LINK]>`

    COMMENT


    Arguments
    ---------

    system : System : default None
        specifies the `System` for which the EVCControlMechanism should serve as a `controller <System.controller>`;
        the EVCControlMechanism will inherit any `OutputStates <OutputState>` specified in the **monitor_for_control**
        argument of the `system <EVCControlMechanism.composition>`'s constructor, and any `ControlSignals <ControlSignal>`
        specified in its **control_signals** argument.

    objective_mechanism : ObjectiveMechanism, List[OutputState or Tuple[OutputState, list or 1d np.array, list or 1d
    np.array]] : \
    default MonitoredOutputStatesOptions.PRIMARY_OUTPUT_STATES
        specifies either an `ObjectiveMechanism` to use for the EVCControlMechanism or a list of the OutputStates it should
        monitor; if a list of `OutputState specifications <ObjectiveMechanism_Monitored_Output_States>` is used,
        a default ObjectiveMechanism is created and the list is passed to its **monitored_output_states** argument.

    prediction_mechanisms : Mechanism, Mechanism subclass, dict, (Mechanism subclass, dict) or list: \
    default PredictionMechanism
        the `Mechanism(s) <Mechanism>` or class(es) of Mechanisms  used for `prediction Mechanism(s)
        <EVCControlMechanism_Prediction_Mechanisms>` and, optionally, their parameters (specified in a `parameter
        specification dictionary <ParameterState_Specification>`);  see `EVCControlMechanism_Prediction_Mechanisms`
        for details.

        COMMENT:
        the `Mechanism(s) <Mechanism>` or class(es) of Mechanisms  used for `prediction Mechanism(s)
        <EVCControlMechanism_Prediction_Mechanisms>`.  If a class, dict, or tuple is specified, it is used as the
        specification for all prediction Mechanisms.  A dict specified on its own is assumed to be a `parameter
        specification dictionary <ParameterState_Specification>` for a `PredictionMechanism`; a dict specified
        in a tuple must be a `parameter specification dictionary <ParameterState_Specification>` appropriate for the
        type of Mechanism specified as the first item of the tuple.  If a list is specified, its length must equal
        the number of `ORIGIN` Mechanisms in the System for which the EVCControlMechanism is the `controller
        <System.controller>`;  each item must be a Mechanism, subclass of one, or a tuple specifying a subclass and
        parameter specification dictionary, that is used as the specification for the prediction Mechanism for the
        corresponding item in list of Systems in `ORIGIN` Mechanism in its `origin_mechanisms
        <System.origin_mechanisms>` attribute.

        ..note::
            Specifying a single instantiated Mechanism (i.e., outside of a list) is a convenience notation, that assumes
            the System for which the EVCControlMechanism is the `controller <System.controller>` has a single `ORIGIN`
            Mechanism; this will cause an if the System has more than one `ORIGIN` Mechanism;  in that case, one of the
            other forms of specification must be used.
        COMMENT

    function : function or method : ControlSignalGridSearch2
        specifies the function used to determine the `allocation_policy` for the next execution of the
        EVCControlMechanism's `system <EVCControlMechanism.composition>` (see `function <EVCControlMechanism.function>` for details).

    value_function : function or method : value_function
        specifies the function used to calculate the `EVC <EVCControlMechanism_EVC>` for the current `allocation_policy`
        (see `value_function <EVCControlMechanism.value_function>` for details).

    cost_function : function or method : LinearCombination(operation=SUM)
        specifies the function used to calculate the cost associated with the current `allocation_policy`
        (see `cost_function <EVCControlMechanism.cost_function>` for details).

    combine_outcome_and_cost_function : function or method : LinearCombination(operation=SUM)
        specifies the function used to combine the outcome and cost associated with the current `allocation_policy`,
        to determine its value (see `combine_outcome_and_cost_function` for details).

    save_all_values_and_policies : bool : default False
        specifes whether to save every `allocation_policy` tested in `EVC_policies` and their values in `EVC_values`.

    control_signals : ControlSignal specification or List[ControlSignal specification, ...]
        specifies the parameters to be controlled by the EVCControlMechanism
        (see `ControlSignal_Specification` for details of specification).

    params : Dict[param keyword: param value] : default None
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters for the
        Mechanism, its `function <EVCControlMechanism.function>`, and/or a custom function and its parameters.  Values
        specified for parameters in the dictionary override any assigned to those parameters in arguments of the
        constructor.

    name : str : default see `name <EVCControlMechanism.name>`
        specifies the name of the EVCControlMechanism.

    prefs : PreferenceSet or specification dict : default Mechanism.classPreferences
        specifies the `PreferenceSet` for the EVCControlMechanism; see `prefs <EVCControlMechanism.prefs>` for details.

    Attributes
    ----------

    system : System
        the `System` for which EVCControlMechanism is the `controller <System.controller>`;
        the EVCControlMechanism inherits any `OutputStates <OutputState>` specified in the **monitor_for_control**
        argument of the `system <EVCControlMechanism.composition>`'s constructor, and any `ControlSignals <ControlSignal>`
        specified in its **control_signals** argument.

    prediction_mechanisms : List[ProcessingMechanism]
        list of `predictions mechanisms <EVCControlMechanism_Prediction_Mechanisms>` generated for the
        EVCControlMechanism's `system <EVCControlMechanism.composition>` when the EVCControlMechanism is created,
        one for each `ORIGIN` Mechanism in the `system <EVCControlMechanism.composition>`.  Each prediction Mechanism is
        named using the name of the ` ORIGIN` Mechanism + "PREDICTION_MECHANISM" and assigned an `OutputState` with
        a name based on the same.

    origin_prediction_mechanisms : Dict[ProcessingMechanism, ProcessingMechanism]
        dictionary of `prediction mechanisms <EVCControlMechanism_Prediction_Mechanisms>` added to the EVCControlMechanism's
        `system <EVCControlMechanism.composition>`, one for each of its `ORIGIN` Mechanisms.  The key for each
        entry is an `ORIGIN` Mechanism of the System, and the value is the corresponding prediction Mechanism.

    predicted_input : Dict[ProcessingMechanism, value]
        dictionary with the `value <Mechanism_Base.value>` of each `prediction Mechanism
        <EVCControlMechanism_Prediction_Mechanisms>` listed in `prediction_mechanisms` corresponding to each `ORIGIN`
        Mechanism of the System. The key for each entry is the name of an `ORIGIN` Mechanism, and its
        value the `value <Mechanism_Base.value>` of the corresponding prediction Mechanism.

    objective_mechanism : ObjectiveMechanism
        the 'ObjectiveMechanism' used by the EVCControlMechanism to evaluate the performance of its `system
        <EVCControlMechanism.composition>`.  If a list of OutputStates is specified in the **objective_mechanism** argument of the
        EVCControlMechanism's constructor, they are assigned as the `monitored_output_states <ObjectiveMechanism.monitored_output_states>`
        attribute for the `objective_mechanism <EVCControlMechanism.objective_mechanism>`.

    monitored_output_states : List[OutputState]
        list of the OutputStates monitored by `objective_mechanism <EVCControlMechanism.objective_mechanism>` (and listed in
        its `monitored_output_states <ObjectiveMechanism.monitored_output_states>` attribute), and used to evaluate the
        performance of the EVCControlMechanism's `system <EVCControlMechanism.composition>`.

    COMMENT:
    [TBI]
        monitored_output_states : 3D np.array
            an array of values of the outputStates in `monitored_output_states` (equivalent to the values of
            the EVCControlMechanism's `input_states <EVCControlMechanism.input_states>`).
    COMMENT

    monitored_output_states_weights_and_exponents: List[Tuple[scalar, scalar]]
        a list of tuples, each of which contains the weight and exponent (in that order) for an OutputState in
        `monitored_outputStates`, listed in the same order as the outputStates are listed in `monitored_outputStates`.

    function : function : default ControlSignalGridSearch2
        determines the `allocation_policy` to use for the next round of the System's
        execution. The default function, `ControlSignalGridSearch2`, conducts an exhaustive (*grid*) search of all
        combinations of the `allocation_samples` of its ControlSignals (and contained in its
        `control_signal_search_space` attribute), by executing the System (using `run_simulation`) for each
        combination, evaluating the result using `value_function`, and returning the `allocation_policy` that yielded
        the greatest `EVC <EVCControlMechanism_EVC>` value (see `EVCControlMechanism_Default_Configuration` for additional details).
        If a custom function is specified, it must accommodate a **controller** argument that specifies an EVCControlMechanism
        (and provides access to its attributes, including `control_signal_search_space`), and must return an array with
        the same format (number and type of elements) as the EVCControlMechanism's `allocation_policy` attribute.

    COMMENT:
        NOTES ON API FOR CUSTOM VERSIONS:
            Gets controller as argument (along with any standard params specified in call)
            Must include **kwargs to receive standard args (variable, params, and context)
            Must return an allocation policy compatible with controller.allocation_policy:
                2d np.array with one array for each allocation value

            Following attributes are available:
            controller._get_simulation_system_inputs gets inputs for a simulated run (using predictionMechanisms)
            controller._assign_simulation_inputs assigns value of prediction_mechanisms to inputs of `ORIGIN` Mechanisms
            controller.run will execute a specified number of trials with the simulation inputs
            controller.monitored_states is a list of the Mechanism OutputStates being monitored for outcome
            controller.input_value is a list of current outcome values (values for monitored_states)
            controller.monitored_output_states_weights_and_exponents is a list of parameterizations for OutputStates
            controller.control_signals is a list of control_signal objects
            controller.control_signal_search_space is a list of all allocationPolicies specifed by allocation_samples
            control_signal.allocation_samples is the set of samples specified for that control_signal
            [TBI:] control_signal.allocation_range is the range that the control_signal value can take
            controller.allocation_policy - holds current allocation_policy
            controller.output_values is a list of current control_signal values
            controller.value_function - calls the three following functions (done explicitly, so each can be specified)
            controller.cost_function - aggregate costs of control signals
            controller.combine_outcome_and_cost_function - combines outcomes and costs
    COMMENT

    value_function : function : default ValueFunction2
        calculates the `EVC <EVCControlMechanism_EVC>` for a given `allocation_policy`.  It takes as its arguments an
        `EVCControlMechanism`, an **outcome** value and a list or ndarray of **costs**, uses these to calculate an EVC,
        and returns a three item tuple with the calculated EVC, and the outcome value and aggregated value of costs
        used to calculate the EVC.  The default, `ValueFunction2`,  calls the EVCControlMechanism's `cost_function
        <EVCControlMechanism.cost_function>` to aggregate the value of the costs, and then calls its
        `combine_outcome_and_costs <EVCControlMechanism.combine_outcome_and_costs>` to calculate the EVC from the outcome
        and aggregated cost (see `EVCControlMechanism_Default_Configuration` for additional details).  A custom
        function can be assigned to `value_function` so long as it returns a tuple with three items: the calculated
        EVC (which must be a scalar value), and the outcome and cost from which it was calculated (these can be scalar
        values or `None`). If used with the EVCControlMechanism's default `function <EVCControlMechanism.function>`, a custom
        `value_function` must accommodate three arguments (passed by name): a **controller** argument that is the
        EVCControlMechanism for which it is carrying out the calculation; an **outcome** argument that is a value; and a
        `costs` argument that is a list or ndarray.  A custom function assigned to `value_function` can also call any
        of the `helper functions <EVCControlMechanism_Functions>` that it calls (however, see `note
        <EVCControlMechanism_Calling_and_Assigning_Functions>` above).

    cost_function : function : default LinearCombination(operation=SUM)
        calculates the cost of the `ControlSignals <ControlSignal>` for the current `allocation_policy`.  The default
        function sums the `cost <ControlSignal.cost>` of each of the EVCControlMechanism's `ControlSignals
        <EVCControlMechanism_ControlSignals>`.  The `weights <LinearCombination.weights>` and/or `exponents
        <LinearCombination.exponents>` parameters of the function can be used, respectively, to scale and/or
        exponentiate the contribution of each ControlSignal cost to the combined cost.  These must be specified as
        1d arrays in a *WEIGHTS* and/or *EXPONENTS* entry of a `parameter dictionary <ParameterState_Specification>`
        assigned to the **params** argument of the constructor of a `LinearCombination` function; the length of
        each array must equal the number of (and the values listed in the same order as) the ControlSignals in the
        EVCControlMechanism's `control_signals <EVCControlMechanism.control_signals>` attribute. The default function can also be
        replaced with any `custom function <EVCControlMechanism_Calling_and_Assigning_Functions>` that takes an array as
        input and returns a scalar value.  If used with the EVCControlMechanism's default `value_function
        <EVCControlMechanism.value_function>`, a custom `cost_function <EVCControlMechanism.cost_function>` must accommodate two
        arguments (passed by name): a **controller** argument that is the EVCControlMechanism itself;  and a **costs**
        argument that is a 1d array of scalar values specifying the `cost <ControlSignal.cost>` for each ControlSignal
        listed in the `control_signals` attribute of the ControlMechanism specified in the **controller** argument.

    combine_outcome_and_cost_function : function : default LinearCombination(operation=SUM)
        combines the outcome and cost for given `allocation_policy` to determine its `EVC <EVCControlMechanisms_EVC>`. The
        default function subtracts the cost from the outcome, and returns the difference.  This can be modified using
        the `weights <LinearCombination.weights>` and/or `exponents <LinearCombination.exponents>` parameters of the
        function, as described for the `cost_function <EVCControlMechanisms.cost_function>`.  The default function can also be
        replaced with any `custom function <EVCControlMechanism_Calling_and_Assigning_Functions>` that returns a scalar value.  If used with the EVCControlMechanism's default `value_function`, a custom
        If used with the EVCControlMechanism's default `value_function`, a custom combine_outcome_and_cost_function must
        accomoudate three arguments (passed by name): a **controller** argument that is the EVCControlMechanism itself; an
        **outcome** argument that is a 1d array with the outcome of the current `allocation_policy`; and a **cost**
        argument that is 1d array with the cost of the current `allocation_policy`.

    control_signal_search_space : 2d np.array
        an array each item of which is an `allocation_policy`.  By default, it is assigned the set of all possible
        allocation policies, using np.meshgrid to construct all permutations of `ControlSignal` values from the set
        specified for each by its `allocation_samples <EVCControlMechanism.allocation_samples>` attribute.

    EVC_max : 1d np.array with single value
        the maximum `EVC <EVCControlMechanism_EVC>` value over all allocation policies in `control_signal_search_space`.

    EVC_max_state_values : 2d np.array
        an array of the values for the OutputStates in `monitored_output_states` using the `allocation_policy` that
        generated `EVC_max`.

    EVC_max_policy : 1d np.array
        an array of the ControlSignal `intensity <ControlSignal.intensity> values for the allocation policy that
        generated `EVC_max`.

    save_all_values_and_policies : bool : default False
        specifies whether or not to save every `allocation_policy and associated EVC value (in addition to the max).
        If it is specified, each `allocation_policy` tested in the `control_signal_search_space` is saved in
        `EVC_policies`, and their values are saved in `EVC_values`.

    EVC_policies : 2d np.array
        array with every `allocation_policy` tested in `control_signal_search_space`.  The `EVC <EVCControlMechanism_EVC>`
        value of each is stored in `EVC_values`.

    EVC_values :  1d np.array
        array of `EVC <EVCControlMechanism_EVC>` values, each of which corresponds to an `allocation_policy` in `EVC_policies`;

    allocation_policy : 2d np.array : defaultControlAllocation
        determines the value assigned as the `variable <ControlSignal.variable>` for each `ControlSignal` and its
        associated `ControlProjection`.  Each item of the array must be a 1d array (usually containing a scalar)
        that specifies an `allocation` for the corresponding ControlSignal, and the number of items must equal the
        number of ControlSignals in the EVCControlMechanism's `control_signals` attribute.

    control_signals : ContentAddressableList[ControlSignal]
        list of the EVCControlMechanism's `ControlSignals <EVCControlMechanism_ControlSignals>`, including any that it inherited
        from its `system <EVCControlMechanism.composition>` (same as the EVCControlMechanism's `output_states
        <Mechanism_Base.output_states>` attribute); each sends a `ControlProjection` to the `ParameterState` for the
        parameter it controls

    name : str
        the name of the EVCControlMechanism; if it is not specified in the **name** argument of the constructor, a
        default is assigned by MechanismRegistry (see `Naming` for conventions used for default and duplicate names).

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the EVCControlMechanism; if it is not specified in the **prefs** argument of the
        constructor, a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet
        <LINK>` for details).

    """

    componentType = EVC_MECHANISM
    initMethod = INIT_FUNCTION_METHOD_ONLY


    classPreferenceLevel = PreferenceLevel.SUBTYPE
    # classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to Type automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'DefaultControlMechanismCustomClassPreferences',
    #     kp<pref>: <setting>...}
        
    class Params(ControlMechanism.Params):
        function = Param(ControlSignalGridSearch2, stateful=False, loggable=False)
        # simulation_ids = Param(list, user=False)

    from psyneulink.components.functions.function import LinearCombination
    # from Components.__init__ import DefaultSystem
    paramClassDefaults = ControlMechanism.paramClassDefaults.copy()
    paramClassDefaults.update({PARAMETER_STATES: NotImplemented}) # This suppresses parameterStates

    @tc.typecheck
    def __init__(self,
                 composition=None,
                 prediction_mechanisms:tc.any(is_iterable, Mechanism, type)=PredictionMechanism,
                 objective_mechanism:tc.optional(tc.any(ObjectiveMechanism, list))=None,
                 monitor_for_control:tc.optional(tc.any(is_iterable, Mechanism, OutputState))=None,
                 function=ControlSignalGridSearch2,
                 value_function=ValueFunction2,
                 save_all_values_and_policies:bool=False,
                 control_signals:tc.optional(tc.any(is_iterable, ParameterState))=None,
                 modulation:tc.optional(_is_modulation_param)=ModulationParam.MULTIPLICATIVE,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None):

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(composition=composition,
                                                  prediction_mechanisms=prediction_mechanisms,
                                                  value_function=value_function,
                                                  save_all_values_and_policies=save_all_values_and_policies,
                                                  params=params)

        super().__init__(system=composition,
                         objective_mechanism=objective_mechanism,
                         monitor_for_control=monitor_for_control,
                         function=function,
                         control_signals=control_signals,
                         modulation=modulation,
                         params=params,
                         name=name,
                         prefs=prefs)

    def _validate_params(self, request_set, target_set=None, context=None):
        '''Validate prediction_mechanisms'''

        super()._validate_params(request_set=request_set, target_set=target_set, context=context)

        if PREDICTION_MECHANISMS in target_set:
            prediction_mechanisms = target_set[PREDICTION_MECHANISMS]
            if isinstance(prediction_mechanisms, type) and not issubclass(prediction_mechanisms, Mechanism):
                raise EVCError("Class used to specify {} argument of {} ({}) must be a type of {}".
                               format(self.name,repr(PREDICTION_MECHANISMS),prediction_mechanisms,Mechanism.__name__))
            elif isinstance(prediction_mechanisms, list):
                for pm in prediction_mechanisms:
                    if not (isinstance(pm,Mechanism) or
                            (isinstance(pm,type) and issubclass(pm,Mechanism)) or
                            (isinstance(pm,tuple) and issubclass(pm[0],Mechanism) and isinstance(pm[1],dict))):
                        raise EVCError("Unrecognized item ({}) in the list specified for {} arg of constructor for {}; "
                                       "must be a Mechanism, a class of Mechanism, or a tuple with a Mechanism class "
                                       "and parameter specification dictionary".
                                       format(pm, repr(PREDICTION_MECHANISMS), self.name))

    def _instantiate_input_states(self, context=None):
        """Instantiate PredictionMechanisms
        """
        if self.composition is not None:
            self._instantiate_prediction_mechanisms(system=self.composition, context=context)
        super()._instantiate_input_states(context=context)

    def apply_control_signal_values(self, control_signal_values, runtime_params, context):
        for i in range(len(control_signal_values)):
            if self.value is None:
                self.value = self.instance_defaults.value
            self.value[i] = np.atleast_1d(control_signal_values[i])

        self._update_output_states(self.value, runtime_params=runtime_params, context=ContextFlags.COMPOSITION)

    def _instantiate_attributes_after_function(self, context=None):
        '''Validate cost function'''

        super()._instantiate_attributes_after_function(context=context)

        if self.composition is None or not self.composition.enable_controller:
            return

    def _instantiate_control_signal(self, control_signal, context=None):
        '''Implement ControlSignalCosts.DEFAULTS as default for cost_option of ControlSignals
        '''
        control_signal = super()._instantiate_control_signal(control_signal, context)
        if control_signal.cost_options is None:
            control_signal.cost_options = ControlSignalCosts.DEFAULTS
        return control_signal

    costs = []
    def run_simulation(self,
                       allocation_policy=None,
                       num_trials=1,
                       reinitialize_values=None,
                       predicted_input=None,
                       call_after_simulation=None,
                       runtime_params=None,
                       context=None):

        if allocation_policy:
            self.apply_control_signal_values(allocation_policy, runtime_params=runtime_params, context=context)

        execution_id = self.composition._get_unique_id()

        allocation_policy_outcomes = []
        other_simulation_data = []
        for i in range(num_trials):
            inputs = {}
            for node in predicted_input:
                inputs[node] = predicted_input[node][i]

            self.composition.context.execution_phase = ContextFlags.SIMULATION
            for output_state in self.output_states:
                for proj in output_state.efferents:
                    proj.context.execution_phase = ContextFlags.PROCESSING

            self.composition.run(inputs=inputs,
                                 reinitialize_values=reinitialize_values,
                                 execution_id=execution_id,
                                 runtime_params=runtime_params,
                                 context=context)

            self.composition.simulation_results.append(self.composition.output_CIM.output_values)

            call_after_simulation_data = None

            if call_after_simulation:
                call_after_simulation_data = call_after_simulation()

            monitored_states = self.objective_mechanism.output_values

            self.composition.context.execution_phase = ContextFlags.PROCESSING
            allocation_policy_outcomes.append(monitored_states)
            other_simulation_data.append(other_simulation_data)

        return allocation_policy_outcomes, other_simulation_data

    def run_simulations(self, allocation_policies, call_after_simulation=None, runtime_params=None, context=None):

        predicted_input, num_trials, reinitialize_values, node_values = self.composition.before_simulations()

        outcome_list = []

        for allocation_policy in allocation_policies:
            allocation_policy_outcomes, simulation_data = self.run_simulation(allocation_policy=allocation_policy,
                                                                              num_trials=num_trials,
                                                                              reinitialize_values=reinitialize_values,
                                                                              predicted_input=predicted_input,
                                                                              call_after_simulation=call_after_simulation,
                                                                              runtime_params=runtime_params,
                                                                              context=context)

            outcome_list.append((allocation_policy, allocation_policy_outcomes, simulation_data))

        self.composition.after_simulations(reinitialize_values, node_values)

        return outcome_list


    @tc.typecheck
    def assign_as_controller(self, system, context=ContextFlags.COMMAND_LINE):
        self._instantiate_prediction_mechanisms(system=system, context=context)
        super().assign_as_controller(system=system, context=context)

    def get_allocation_policies(self):
        # grid search -- all possible combinations of control signal
        control_signal_sample_lists = []
        control_signals = self.control_signals

        # Get allocation_samples for all ControlSignals
        num_control_signals = len(control_signals)

        for control_signal in self.control_signals:
            control_signal_sample_lists.append(control_signal.allocation_samples)

        # Construct control_signal_search_space:  set of all permutations of ControlProjection allocations
        #                                     (one sample from the allocationSample of each ControlProjection)
        # Reference for implementation below:
        # http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
        return np.array(np.meshgrid(*control_signal_sample_lists)).T.reshape(-1,num_control_signals)

    def _execute(
        self,
        variable=None,
        runtime_params=None,
        context=None
    ):
        """Determine `allocation_policy <EVCControlMechanism.allocation_policy>` for next run of System

        Update prediction mechanisms
        Construct control_signal_search_space (from allocation_samples of each item in control_signals):
            * get `allocation_samples` for each ControlSignal in `control_signals`
            * construct `control_signal_search_space`: a 2D np.array of control allocation policies, each policy of
              which is a different combination of values, one from the `allocation_samples` of each ControlSignal.
        Call self.function -- default is ControlSignalGridSearch2
        Return an allocation_policy
        """

        # Get all allocation policies to try
        self.control_signal_search_space = self.get_allocation_policies()

        # for each allocation policy:
        # (1) apply allocation policy, (2) get a new execution id, (3) run simulation, (4) store results
        simulation_data = self.run_simulations(allocation_policies=self.control_signal_search_space,
                                               runtime_params=runtime_params,
                                               context=context)

        allocation_policy = self.function(self=self,
                                          simulation_data=simulation_data,
                                          context=context)
        # for i in range(len(outcomes)):
        #     allocation_policy_outcomes = outcomes[i]
        #     allocation_policy = self.control_signal_search_space[i]
        #     allocation_policy_evc_list = []
        #     num_trials = len(allocation_policy_outcomes)
        #
        #     for j in range(num_trials):
        #         outcome = allocation_policy_outcomes[0][j]
        #         value = self.function(self=self,
        #                               outcome=outcome,
        #                               context=context)
        #         allocation_policy_evc_list.append(value)
        #         EVC_avg = list(map(lambda x: (sum(x)) / num_trials, zip(*allocation_policy_evc_list)))
        #         EVC, outcome, cost = EVC_avg
        #
        #         EVC_max = max(EVC, EVC_max)
        #         if self.paramsCurrent[SAVE_ALL_VALUES_AND_POLICIES]:
        #             # FIX:  ASSIGN BY INDEX (MORE EFFICIENT)
        #             EVC_values = np.append(EVC_values, np.atleast_1d(EVC), axis=0)
        #             # Save policy associated with EVC for each process, as order of chunks
        #             #     might not correspond to order of policies in control_signal_search_space
        #             if len(EVC_policies[0]) == 0:
        #                 EVC_policies = np.atleast_2d(allocation_policy)
        #             else:
        #                 EVC_policies = np.append(EVC_policies, np.atleast_2d(allocation_policy), axis=0)
        #         if EVC == EVC_max:
        #             # Keep track of state values and allocation policy associated with EVC max
        #             # EVC_max_state_values = self.input_value.copy()
        #             # EVC_max_policy = allocation_vector.copy()
        #             EVC_max_state_values = self.input_values
        #             EVC_max_policy = allocation_policy
        #             max_value_state_policy_tuple = (EVC_max, EVC_max_state_values, EVC_max_policy)
        #         self.EVC_max = EVC_max
        #         self.EVC_max_state_values = EVC_max_state_values
        #         self.EVC_max_policy = EVC_max_policy
        #         if self.paramsCurrent[SAVE_ALL_VALUES_AND_POLICIES]:
        #             self.EVC_values = EVC_values
        #             self.EVC_policies = EVC_policies

        return allocation_policy

        # IMPLEMENTATION NOTE:  skip ControlMechanism._execute since it is a stub method that returns input_values
        # allocation_policy = super(ControlMechanism, self)._execute(
        #         controller=self,
        #         variable=variable,
        #         runtime_params=runtime_params,
        #         context=context
        # )
    @property
    def value_function(self):
        return self._value_function

    @value_function.setter
    def value_function(self, assignment):
        if isinstance(assignment, function_type):
            self._value_function = ValueFunction2(assignment)
        elif assignment is ValueFunction2:
            self._value_function = ValueFunction2()
        else:
            self._value_function = assignment

    @property
    def combine_outcome_and_cost_function(self):
        return self._combine_outcome_and_cost_function

    @combine_outcome_and_cost_function.setter
    def combine_outcome_and_cost_function(self, value):
        from psyneulink.components.functions.function import UserDefinedFunction
        if isinstance(value, function_type):
            udf = UserDefinedFunction(function=value)
            self._combine_outcome_and_cost_function = udf
        else:
            self._combine_outcome_and_cost_function = value