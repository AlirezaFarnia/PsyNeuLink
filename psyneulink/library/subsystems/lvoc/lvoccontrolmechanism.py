# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# *************************************************  LVOCControlMechanism ******************************************************

"""

Overview
--------

An LVOCControlMechanism is a `ControlMechanism <ControlMechanism>` that regulates it `ControlSignals <ControlSignal>` in
order to optimize the performance of the `Composition` to which it belongs.  It implements a form of the Learned Value
of Control model described in `Leider et al. <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi
.1006043&rev=2>`_, which learns to select the value for its `control_signals <LVOCControlMechanism.control_signals>`
(i.e., its `allocation_policy  <LVOCControlMechanism.allocation_policy>`) that maximzes its `EVC
<LVOCControlMechanism_EVC>` based on a set of `predictors <LVOCControlMechanism_Predictors>`.

.. _LVOCControlMechanism_EVC:

*Expected Value of Control (EVC)*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **expected value of control (EVC)** is the outcome of executing the `composition <EVCControlMechanism.composition>`
to which the LVOCControlMechanism belongs under a given `allocation_policy <LVOCControlMechanism.allocation_policy>`,
as determined by its `objective_mechanism <LVOCControlMechanism.objective_mechanism>`, discounted by the `cost
<ControlSignal.cost> of the `control_signals <LVOCControlMechanism.control_signals>` under that `allocation_policy
<LVOCControlMechanism.allocation_policy>`.

The LVOCControlMechanism's `function <LVOCControlMechanism.function>` learns to predict the outcome of its
`objective_mechanism <LVOCControlMechanism.objective_mechanism>` from a weighted sum of its `predictors
<LVOCControlMechanism.predictors>`, `control_signals <LVOCControlMechanism.control_signals>`, interactions among
these, and the costs of the `control_signals <LVOCControlMechanism.control_signals>`.  This is referred to as the
"learned value of control," or LVOC.

.. _LVOCControlMechanism_Creation:

Creating an LVOCControlMechanism
------------------------

 An LVOCControlMechanism can be created in the same was as any `ControlMechanism`, with the exception that it cannot
 be assigned as the `controller <Composition.controller>` of a Composition.  The following arguments of its
 constructor are specific to the LVOCControlMechanism:

  * **composition** -- specifies the `Composition` to which the LVOCControlMechanism is to be assigned.
  ..
  * **predictors** -- this takes the place of the standard **input_states** argument in the constructor for a
    Mechanism`, and specifies the inputs that it learns to use to determine its `allocation_policy
    <LVOCControlMechanism.allocation_policy>` in each `trial` of execution.  By default, the input to every `ORIGIN`
    Mechanism of the `Composition` to which the LVOCControlMechanism belongs is used as its `predictors
    <LVOCControlMechanism_Predictors>`.  However, it can be specified using any of the following, singly or combined
    in a list:

        * *InputState specification* -- this can be any legal form of `InputState specification
          <InputState_Specification>` that includes a specification of a `Mechanism` or `OutputState` to project to
          the InputState;  the `value <OutputState.value>` of the specified OutputState (or `primary OutputState
          <OutputState_Primary>` of the specified Mechanism) is used as a `predictor <LVOCControlMechanism.predictor>`.
        |
        * {*SHADOW_INPUTS*: <*ALL* or List[InputState(s) and/or Mechanism(s)>][,FUNCTION:<Function]} -- dictionary that
          specifies InputStates, the inputs to which are used as `predictors <LVOCControlMechanism_Predictors>`.  If
          *ALL* is specified, then every InputState of every *ORIGIN* Mechanism in the Composition is used;  all of
          the InputStates are used for any Mechanism(s) specified.  If the *FUNCTION* entry is included, the 'Function`
          specified in its value is assigned to each of the InputStates created on the LVOCControlMechanism to shadow
          the ones specified in the *SHADOW_INPUTS* entry (see `LVOC_Structure`).

    Predictors can also be added to an existing LVOCControlMechanism using its `add_predictors` method.


.. _LVOCControlMechanism_Structure:

Structure
---------

An LVOCControlMechanism must belong to a `Composition` (identified in its `composition
<LVOCControlMechanism.composition>` attribute).

.. _LVOCControlMechanism_Input:

*Input*
~~~~~~~

An LVOCControlMechanism has an `InputState` that receives a Projection from its `objective_mechanism
<LVOCControlMechanism.objective_mechanism>` (it primary InputState <InputState_Primary>`), and additional ones for
each of its predictors, as described below.

.. _LVOCControlMechanism_Predictors:

Predictors
^^^^^^^^^^

Predictors, together with the LVOCControlMechanism's `control_signals <LVOCControlMechanism.control_signals>`,
are used by its `function <LVOCControlMechanism.function>` to learn to predict the outcome of its
`objective_mechanism <LVOCControlMechanism.objective_mechanism>` and to determine its `allocation_policy
<LVOCControlMechanism.allocation_policy>`.

Predictors can be of two types:

* *Input Predictor* -- this is a value received as input by some other Mechanism in the Composition.
    These are typically specified in a *SHADOW_INPUTS* entry of a dict in the **predictors** argument of the
    LVOCControlMechanism's constructor (see `LVOCControlMechanism_Creation`), designating an InputState to be
    shadowed.  A Projection projects to the InputState of the LVOCControlMechanism for that predictor,
    from the same OutputState that projects to the InputState being "shadowed" (including an OutputState of the
    Composition's `InputCIM` if the input being shadowed belongs to an `ORIGIN` Mechanism of the Composition).

* *Output Predictor* -- this is the `value <OutputState.value>` of an OutputState of some other Mechanism in the
    Composition.  These too are specified in the **predictors** argument of the LVOCControlMechanism's constructor,
    (see `LVOCControlMechanism_Creation`), and each is assigned a Projection to the InputState of the
    LVOCControlMechanism for that predictor.

The current `values <InputState.value>` of the InputStates for the predictors are listed in the `predictor_values
<LVOCControlMechanism.predictor_values>` attribute.

.. _LVOCControlMechanism_ObjectiveMechanism:

ObjectiveMechanism
^^^^^^^^^^^^^^^^^^

Like any ControlMechanism, an LVOCControlMechanism receives its input from the *OUTCOME* `OutputState
<ObjectiveMechanism_Output>` of its `objective_mechanism <LVOCControlMechanism.objective_mechanism>`,
via a MappingProjection to its `primary InputState <InputState_Primary>`. By default, the ObjectiveMechanism's
function is a `LinearCombination` function with its `operation <LinearCombination.operation>` attribute assigned as
*PRODUCT*; this takes the product of the `value <OutputState.value>`\\s of the OutputStates that it monitors (listed
in its `monitored_output_states <ObjectiveMechanism.monitored_output_states>` attribute.  However, this can be
customized in a variety of ways:

    * by specifying a different `function <ObjectiveMechanism.function>` for the ObjectiveMechanism
      (see `Objective Mechanism Examples <ObjectiveMechanism_Weights_and_Exponents_Example>` for an example);
    ..
    * using a list to specify the OutputStates to be monitored  (and the `tuples format
      <InputState_Tuple_Specification>` to specify weights and/or exponents for them) in either the
      **monitor_for_control** or **objective_mechanism** arguments of the LVOCControlMechanism's constructor;
    ..
    * using the  **monitored_output_states** argument for an ObjectiveMechanism specified in the `objective_mechanism
      <LVOCControlMechanism.objective_mechanism>` argument of the LVOCControlMechanism's constructor;
    ..
    * specifying a different `ObjectiveMechanism` in the **objective_mechanism** argument of the LVOCControlMechanism's
      constructor.

    .. _LVOCControlMechanism_Objective_Mechanism_Function_Note:

    .. note::
       If a constructor for an `ObjectiveMechanism` is used for the **objective_mechanism** argument of the
       LVOCControlMechanism's constructor, then the default values of its attributes override any used by the
       LVOCControlMechanism for its `objective_mechanism <LVOCControlMechanism.objective_mechanism>`.  In particular,
       whereas an LVOCControlMechanism uses the same default `function <ObjectiveMechanism.function>` as an
       `ObjectiveMechanism` (`LinearCombination`), it uses *PRODUCT* rather than *SUM* as the default value of the
       `operation <LinearCombination.operation>` attribute of the function.  As a consequence, if the constructor for
       an ObjectiveMechanism is used to specify the LVOCControlMechanism's **objective_mechanism** argument,
       and the **operation** argument is not specified, *SUM* rather than *PRODUCT* will be used for the
       ObjectiveMechanism's `function <ObjectiveMechanism.function>`.  To ensure that *PRODUCT* is used, it must be
       specified explicitly in the **operation** argument of the constructor for the ObjectiveMechanism (see 1st
       example under `System_Control_Examples`).

The LVOCControlMechanism's `function <LVOCControlMechanism.function>` learns to predict the `value <OutputState.value>`
of the *OUTCOME* `OutputState` of the LVOCControlMechanism's `objective_mechanism
<LVOCControlMechanism.objective_mechanism>`, as described below.

.. _LVOCControlMechanism_Function:

*Function*
~~~~~~~~~~

The `function <LVOCControlMechanism.function>` of an LVOCControlMechanism learns how to weight its `predictors
<LVOCControlMechanism_Predictors>`, the `values <ControlSignal.value>` of its  `control_signals
<LVOCControlMechanism.control_signals>`, the interactions between these, and the `costs <ControlSignal.costs>` of the
`control_signals <LVOCControlMechanism.control_signals>`, to best predict the outcome of its `objective_mechanism
<LVOCControlMechanism.objective_mechanism>`.  Using those weights, and the current set of predictors, it then
searches for and returns the `allocation_policy <LVOCControlMechanism.allocation_policy>` that maximizes the `EVC
<LVOCControlMechanism_EVC>`.  By default, `function <LVOCControlMechanism.function>` is `BayesGLM`. However,
any function can be used that accepts a 2d array, the first item of which is an array of scalar values (the prediction
terms) and the second that is a scalar value (the outcome to be predicted), and returns an array with the same shape as
the LVOCControlMechanism's `allocation_policy <LVOCControlMechanism.allocation_policy>`.

.. _LVOCControlMechanism_ControlSignals:

*ControlSignals*
~~~~~~~~~~~~~~~~

The OutputStates of an LVOCControlMechanism (like any `ControlMechanism`) are a set of `ControlSignals
<ControlSignal>`, that are listed in its `control_signals <LVOCControlMechanism.control_signals>` attribute (as well as
its `output_states <ControlMechanism.output_states>` attribute).  Each ControlSignal is assigned a `ControlProjection`
that projects to the `ParameterState` for a parameter controlled by the LVOCControlMechanism.  Each ControlSignal is
assigned an item of the LVOCControlMechanism's `allocation_policy`, that determines its `allocation
<ControlSignal.allocation>` for a given `TRIAL` of execution.  The `allocation <ControlSignal.allocation>` is used by
a ControlSignal to determine its `intensity <ControlSignal.intensity>`, which is then assigned as the `value
<ControlProjection.value>` of the ControlSignal's ControlProjection.   The `value <ControlProjection>` of the
ControlProjection is used by the `ParameterState` to which it projects to modify the value of the parameter (see
`ControlSignal_Modulation` for description of how a ControlSignal modulates the value of a parameter it controls).
A ControlSignal also calculates a `cost <ControlSignal.cost>`, based on its `intensity <ControlSignal.intensity>`
and/or its time course. The `cost <ControlSignal.cost>` may be included in the evaluation carried out by the
LVOCControlMechanism's `function <LVOCControlMechanism.function>` for a given `allocation_policy`,
and that it uses to adapt the ControlSignal's `allocation <ControlSignal.allocation>` in the future.

.. _LVOCControlMechanism_Execution:

Execution
---------

When an LVOCControlMechanism is executed, it uses the values of its `predictors <LVOCControlMechanism_Predictors>`,
listed in its `predictor_values <LVOCControlMechanism.predictor_values>` attribute, to determines and implement the
`allocation_policy` for the current `trial` of execution of its `composition <LVOCControlMechanism.composition>`.
Specifically it executes the following steps:

  * Updates `prediction_vector <LVOCControlMechanism.prediction_vector>` with the current `predictors_values
    <LVOCControlMechanism.predictor_values>`, `control_signals <LVOCControlMechanism.control_signals>`,
    and their `costs <ControlSignal.cost>`.

  * Calls its `function <LVOCControlMechanism.function>` with the `prediction_vector
    <LVOCControlMechanism.prediction_vector>` and the outcome received from the
    LVOCControlMechanism's `objective_mechanism <LVOCControlMechanism.objective_mechanism>` to update its
    `prediction_weights <LVOCControlMechanism.prediction_weights>`.

  * Calls its `gradient_ascent <LVOCControlMechanism.gradient_ascent>` function with `prediction_vector
    <LVOCControlMechanism.prediction_vector>` and `prediction_weights <LVOCControlMechanism.prediction_weights>`
    to determine the `allocation_policy <LVOCControlMechanism.alocation_policy>` that yields the greatest `EVC
    <LVOCControlMechanism_EVC>`, and returns that `allocation_policy <LVOCControlMechanism.allocation_policy>`.

The values specified by the `allocation_policy <LVOCControlMechanism.allocation_policy>` returned by the
LVOCControlMechanism's `function <LVOCControlMechanism.function>` are assigned as the `values <ControlSignal.values>`
of its `control_signals <LVOCControlMechanism.control_signals>`.

COMMENT:
.. _LVOCControlMechanism_Examples:

Example
-------
COMMENT

.. _LVOCControlMechanism_Class_Reference:

Class Reference
---------------

"""
import warnings
from collections import Iterable

import numpy as np
import typecheck as tc

from psyneulink.components.functions.function import ModulationParam, _is_modulation_param, Buffer, Linear, BayesGLM, \
    EPSILON
from psyneulink.components.mechanisms.mechanism import Mechanism
from psyneulink.components.mechanisms.adaptive.control.controlmechanism import ControlMechanism
from psyneulink.components.mechanisms.processing.objectivemechanism import OUTCOME, ObjectiveMechanism
from psyneulink.components.states.inputstate import InputState
from psyneulink.components.states.outputstate import OutputState
from psyneulink.components.states.parameterstate import ParameterState
from psyneulink.components.states.modulatorysignals.controlsignal import ControlSignalCosts
from psyneulink.components.shellclasses import Composition_Base
from psyneulink.globals.context import ContextFlags
from psyneulink.globals.keywords import \
    ALL, FUNCTION, INIT_FUNCTION_METHOD_ONLY, INIT__EXECUTE__METHOD_ONLY,\
    LVOCCONTROLMECHANISM, NAME, PARAMETER_STATES, PROJECTIONS, VARIABLE
from psyneulink.globals.preferences.componentpreferenceset import is_pref_set
from psyneulink.globals.preferences.preferenceset import PreferenceLevel
from psyneulink.globals.defaults import defaultControlAllocation
from psyneulink.globals.utilities import ContentAddressableList, is_iterable, is_numeric
from psyneulink.library.subsystems.lvoc.lvocauxiliary import LearnAllocationPolicy

__all__ = [
    'LVOCControlMechanism', 'LVOCError', 'SHADOW_INPUTS',
]

SHADOW_INPUTS = 'SHADOW_INPUTS'
PREDICTION_WEIGHTS = 'PREDICTION_WEIGHTS'

class LVOCError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)


class LVOCControlMechanism(ControlMechanism):
    """LVOCControlMechanism(                        \
    composition=None,                               \
    predictors=SHADOW_INPUTS,                       \
    objective_mechanism=None,                       \
    origin_objective_mechanism=False,               \
    terminal_objective_mechanism=False,             \
    function=BayesGLM,                              \
    control_signals=None,                           \
    modulation=ModulationParam.MULTIPLICATIVE,      \
    params=None,                                    \
    name=None,                                      \
    prefs=None)

    Subclass of `ControlMechanism <ControlMechanism>` that optimizes the `ControlSignals <ControlSignal>` for a
    `Composition`.

    Arguments
    ---------

    composition : Composition
        specifies the `Composition` to which the LVOCControlMechanism belongs.

    predictors : SHADOW_INPUTS, dict, InputState, OutputState, or Mechanism : SHADOW_INPUTS
        specifies the values that the LVOCControlMechanism learns to use for determining its `allocation_policy
        <LVOCControlMechanism.allocation_policy>` (see `LVOCControlMechanism_Creation` for details).

    objective_mechanism : ObjectiveMechanism or List[OutputState specification] : default None
        specifies either an `ObjectiveMechanism` to use for the LVOCControlMechanism, or a list of the `OutputState
        <OutputState>`\\s it should monitor; if a list of `OutputState specifications
        <ObjectiveMechanism_Monitored_Output_States>` is used, a default ObjectiveMechanism is created and the list
        is passed to its **monitored_output_states** argument.

    function : LearningFunction or callable : BayesGLM
        specifies the function used to learn to predict the outcome of `objective_mechanism
        <LVOCControlMechanism.objective_mechanism>` from the `prediction_vector
        <LVOCControlMechanism.prediction_vector>` (see `LVOCControlMechanism_Function` for details);

    control_signals : ControlSignal specification or List[ControlSignal specification, ...]
        specifies the parameters to be controlled by the LVOCControlMechanism
        (see `ControlSignal_Specification` for details of specification).

    params : Dict[param keyword: param value] : default None
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters for the
        Mechanism, its `function <LVOCControlMechanism.function>`, and/or a custom function and its parameters.  Values
        specified for parameters in the dictionary override any assigned to those parameters in arguments of the
        constructor.

    name : str : default see `name <LVOCControlMechanism.name>`
        specifies the name of the LVOCControlMechanism.

    prefs : PreferenceSet or specification dict : default Mechanism.classPreferences
        specifies the `PreferenceSet` for the LVOCControlMechanism; see `prefs <LVOCControlMechanism.prefs>` for details.

    Attributes
    ----------

    composition : Composition
        the `Composition` to which LVOCControlMechanism belongs.

    predictor_values : 1d ndarray
        the current `values <InputState.value>` of the InputStates used by `function <LVOCControlMechanism.function>`
        to determine `allocation_policy <LVOCControlMechanism.allocation_policy>` (see
        `LVOCControlMechanism_Predictors` for details about predictors).

    objective_mechanism : ObjectiveMechanism
        the 'ObjectiveMechanism' used by the LVOCControlMechanism to evaluate the performance of its `system
        <LVOCControlMechanism.system>`.  If a list of OutputStates is specified in the **objective_mechanism** argument
        of the LVOCControlMechanism's constructor, they are assigned as the `monitored_output_states
        <ObjectiveMechanism.monitored_output_states>` attribute for the `objective_mechanism
        <LVOCControlMechanism.objective_mechanism>` (see LVOCControlMechanism_ObjectiveMechanism for additional
        details).

    monitored_output_states : List[OutputState]
        list of the OutputStates monitored by `objective_mechanism <LVOCControlMechanism.objective_mechanism>`
        (and listed in its `monitored_output_states <ObjectiveMechanism.monitored_output_states>` attribute),
        and used to evaluate the performance of the LVOCControlMechanism's `system <LVOCControlMechanism.system>`.

    monitored_output_states_weights_and_exponents: List[Tuple[scalar, scalar]]
        a list of tuples, each of which contains the weight and exponent (in that order) for an OutputState in
        `monitored_outputStates`, listed in the same order as the outputStates are listed in `monitored_outputStates`.

    prediction_vector : 1d ndarray
        current values, respectively, of `predictors <LVOCControlMechanism_Predictors>`, interaction terms for
        predictors x control_signals, `control_signals <LVOCControlMechanism.control_signals>`, and `costs
        <ControlSignal.cost>` of control_signals.

    prediction_weights : 1d ndarray
        weights assigned to each term of `prediction_vector <LVOCControlMechanism.prediction_vectdor>`
        last returned by `function <LVOCControlMechanism.function>`.

    function : LearningFunction or callable
        takes `prediction_vector <LVOCControlMechanism.prediction_vector>` and outcome received from
        `objective_mechanism <LVOCControlMechanism.objective_mechanism>` and returns an updated set of
        `prediction_weights <LVOCControlMechanism.prediction_weights>` (see `LVOCControlMechanism_Function`
        for additional details).

    allocation_policy : 2d np.array : defaultControlAllocation
        determines the value assigned as the `variable <ControlSignal.variable>` for each `ControlSignal` and its
        associated `ControlProjection`.  Each item of the array must be a 1d array (usually containing a scalar)
        that specifies an `allocation` for the corresponding ControlSignal, and the number of items must equal the
        number of ControlSignals in the LVOCControlMechanism's `control_signals` attribute.

    control_signals : ContentAddressableList[ControlSignal]
        list of the LVOCControlMechanism's `ControlSignals <LVOCControlMechanism_ControlSignals>`, including any that it inherited
        from its `system <LVOCControlMechanism.system>` (same as the LVOCControlMechanism's `output_states
        <Mechanism_Base.output_states>` attribute); each sends a `ControlProjection` to the `ParameterState` for the
        parameter it controls

    name : str
        the name of the LVOCControlMechanism; if it is not specified in the **name** argument of the constructor, a
        default is assigned by MechanismRegistry (see `Naming` for conventions used for default and duplicate names).

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the LVOCControlMechanism; if it is not specified in the **prefs** argument of the
        constructor, a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet
        <LINK>` for details).

    """

    componentType = LVOCCONTROLMECHANISM
    # initMethod = INIT_FUNCTION_METHOD_ONLY
    # initMethod = INIT__EXECUTE__METHOD_ONLY


    classPreferenceLevel = PreferenceLevel.SUBTYPE
    # classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to Type automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'DefaultControlMechanismCustomClassPreferences',
    #     kp<pref>: <setting>...}

    class Params(ControlMechanism.Params):
        function = LearnAllocationPolicy

    from psyneulink.components.functions.function import LinearCombination
    paramClassDefaults = ControlMechanism.paramClassDefaults.copy()
    paramClassDefaults.update({PARAMETER_STATES: NotImplemented}) # This suppresses parameterStates

    @tc.typecheck
    def __init__(self,
                 composition:tc.optional(Composition_Base)=None,
                 predictors:tc.optional(tc.any(Iterable, Mechanism, OutputState, InputState))=SHADOW_INPUTS,
                 objective_mechanism:tc.optional(tc.any(ObjectiveMechanism, list))=None,
                 origin_objective_mechanism=False,
                 terminal_objective_mechanism=False,
                 function=BayesGLM,
                 control_signals:tc.optional(tc.any(is_iterable, ParameterState))=None,
                 modulation:tc.optional(_is_modulation_param)=ModulationParam.MULTIPLICATIVE,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None):

        predictors = self._parse_predictor_specs(composition, predictors)
        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(composition=composition,
                                                  input_states=predictors,
                                                  origin_objective_mechanism=origin_objective_mechanism,
                                                  terminal_objective_mechanism=terminal_objective_mechanism,
                                                  params=params)


        super().__init__(system=None,
                         objective_mechanism=objective_mechanism,
                         function=function,
                         control_signals=control_signals,
                         modulation=modulation,
                         params=params,
                         name=name,
                         prefs=prefs)

    def _instantiate_input_states(self, context=None):
        """Instantiate input_states for Projections from predictors and objective_mechanism.

        The input_states are specified in the **predictor** argument of the LVOCControlMechanism's constructor.

        input_states can be any legal InputState specification, which will generate a Projection from the
           source specified (FIX: WHAT IF NONE IS SPECIFIED??);
           this allows the output of any Mechanism in the Composition to be used as a predictor.
        input_states can also include a dict with an entry that has the keyword *SHADOW_INPUTS* as its key,
            and either the keyword *ALL* or a list of Mechanisms and/or InputStates as its value.  This creates
            one or more InputStates on the LVOCControlMechanism, each of which "shadows" -- that is, receives a
            Projection from the same source as — the InputState(s) specified in the value of the entry, as follows:
            - *ALL*: InputStates and Projections are created that shadow every InputState of every ORIGIN Mechanism of
                the Composition -- these receive a Projection from the Input CIM OutputState associated with the
                InputState of the ORIGIN Mechanism to the InputState created for it on the LVOCControlMechanism.
            - List of Mechanisms and/or InputStates:  An InputState and Projection is created that shadows the each
                InputState listed, and all of the InputStates of any Mechanism listed.
            The dict can also contain an entry using the keyword *FUNCTION* as its key and a Function as its value; that
                Function will be used as the function of all of the InputStates created for the LVOCControlMechanism.

        An InputState is also created for the Projection from the LVOCControlMechanism's objective_mechanism;  this is
              inserted as the first (primary) InputState in input_states.

        """

        # If input_states has SHADOW_INPUTS in any of its specifications, parse into input_states specifications
        # if any(SHADOW_INPUTS in spec for spec in self.input_states):
        #     self.input_states = self._parse_predictor_specs(composition=self.composition,
        #                                                     predictors=self.input_states,
        #                                                     context=context)

        # Insert primary InputState for outcome from ObjectiveMechanism; assumes this will be a single scalar value
        self.input_states.insert(0, OUTCOME),

        # Configure default_variable to comport with full set of input_states
        self.instance_defaults.variable, ignore = self._handle_arg_input_states(self.input_states)

        super()._instantiate_input_states(context=context)

    tc.typecheck
    def add_predictors(self, predictors, composition:tc.optional(Composition_Base)=None):
        '''Add InputStates and Projections to LVOCControlMechanism for predictors used to predict outcome

        **predictors** argument can use any of the forms of specification allowed
            for the **input_states** argument of the LVOCMechanism,
            as well as the keyword SHADOW_INPUTS, either alone or as the keyword for an entry in a dictionary,
            the value of which must a list of InputStates.
        '''

        if self.composition is None:
            self.composition = composition
        else:
            if not composition is self.composition:
                raise LVOCError("Specified composition ({}) conflicts with one to which {} is already assigned ({})".
                                format(composition.name, self.name, self.composition.name))
        predictors = self._parse_predictor_specs(composition=composition,
                                                 predictors=predictors,
                                                 context=ContextFlags.COMMAND_LINE)
        self.add_states(InputState, predictors)

    @tc.typecheck
    def _parse_predictor_specs(self, composition:Composition_Base,
                               predictors:tc.any(str,list)=SHADOW_INPUTS, context=None):
        """Parse entries of _input_states list that specify shadowing of Mechanisms' or Composition's inputs

        Generate an InputState specification dictionary for each predictor specified in predictors argument
        If it is InputState specification, use as is
        If it is a SHADOW_INPUT entry, generate a Projection from the OutputState that projects to the specified item

        Returns list of InputState specifications
        """

        composition = composition or self.composition
        if not composition:
            raise LVOCError("PROGRAM ERROR: A Composition must be specified in call to _instantiate_inputs")

        parsed_predictors = []

        for spec in predictors:
            if SHADOW_INPUTS in spec:
                # If spec is SHADOW_INPUTS keyword on its own, assume inputs to all ORIGIN Mechanisms
                if isinstance(spec, str):
                    spec = {SHADOW_INPUTS:ALL}
                spec = self._parse_shadow_input_spec(spec)
            else:
                spec = [spec] # (so that extend can be used below)
            parsed_predictors.extend(spec)

        return parsed_predictors

    @tc.typecheck
    def _parse_shadow_input_spec(self, spec:dict):
        ''' Return a list of InputState specifications for the inputs specified in value of dict

        If ALL is specified, specify an InputState for each ORIGIN Mechanism in the Composition
            with Projection from the OutputState of the Compoisitions Input CIM for that ORIGIN Mechanism
        For any other specification, specify an InputState with a Projection from the sender of any Projections
            that project to the specified item
        If FUNCTION entry, assign as Function for all InputStates
        '''

        input_state_specs = []

        shadow_spec = spec[SHADOW_INPUTS]

        if shadow_spec is ALL:
            # Generate list of InputState specification dictionaries,
            #    one for each input to the Composition
            # for composition_input in self.composition.input_CIM.output_states:
            #     input_state_specs.append(composition_input)
            input_state_specs.extend([{NAME:'INPUT OF ' + c.efferents[0].receiver.name +
                                            ' of ' + c.efferents[0].receiver.owner.name,
                                       PROJECTIONS:c}
                                      for c in self.composition.input_CIM.output_states])
        elif isinstance(shadow_spec, list):
            for item in shadow_spec:
                if isinstance(item, Mechanism):
                    # Shadow all of the InputStates for the Mechanism
                    input_states = item.input_states
                if isinstance(item, InputState):
                    # Place in a list for consistency of handling below
                    input_states = [item]
                # Shadow all of the Projections to each specified InputState
                input_state_specs.extend([{NAME:i.name + 'of' + i.owner.name,
                                           VARIABLE: i.variable,
                                           PROJECTIONS: i.path_afferents}
                                          for i in input_states])

        if FUNCTION in spec:
            for i in input_state_specs:
                i.update({FUNCTION:spec[FUNCTION]})

        return input_state_specs

    def _instantiate_attributes_after_function(self, context=None):
        '''Validate cost function, instantiate Projections to ObjectiveMechanism, and construct
        control_signal_search_space.

        Instantiate Projections to ObjectiveMechansm for worth and current weights

        Construct control_signal_search_space (from allocation_samples of each item in control_signals):
            * get `allocation_samples` for each ControlSignal in `control_signals`
            * construct `control_signal_search_space`: a 2D np.array of control allocation policies, each policy of
              which is a different combination of values, one from the `allocation_samples` of each ControlSignal.
        '''

        super()._instantiate_attributes_after_function(context=context)

        if self.composition is None:
            return

        # # Validate cost function
        # cost_Function = self.cost_function
        # if isinstance(cost_Function, Function):
        #     # Insure that length of the weights and/or exponents arguments for the cost_function
        #     #    matches the number of control signals
        #     num_control_projections = len(self.control_projections)
        #     if cost_Function.weights is not None:
        #         num_cost_weights = len(cost_Function.weights)
        #         if  num_cost_weights != num_control_projections:
        #             raise LVOCError("The length of the weights argument {} for the {} of {} "
        #                            "must equal the number of its control signals {}".
        #                            format(num_cost_weights,
        #                                   COST_FUNCTION,
        #                                   self.name,
        #                                   num_control_projections))
        #     if cost_Function.exponents is not None:
        #         num_cost_exponents = len(cost_Function.exponents)
        #         if  num_cost_exponents != num_control_projections:
        #             raise LVOCError("The length of the exponents argument {} for the {} of {} "
        #                            "must equal the number of its control signals {}".
        #                            format(num_cost_exponents,
        #                                   COST_FUNCTION,
        #                                   self.name,
        #                                   num_control_projections))
        #
        # # Construct control_signal_search_space
        # control_signal_sample_lists = []
        # control_signals = self.control_signals
        # # Get allocation_samples for all ControlSignals
        # num_control_signals = len(control_signals)
        #
        # for control_signal in self.control_signals:
        #     control_signal_sample_lists.append(control_signal.allocation_samples)
        #
        # # Construct control_signal_search_space:  set of all permutations of ControlProjection allocations
        # #                                     (one sample from the allocationSample of each ControlProjection)
        # # Reference for implementation below:
        # # http://stackoverflow.com/questions/1208118/using-numpy-to-build-an-array-of-all-combinations-of-two-arrays
        # self.control_signal_search_space = \
        #     np.array(np.meshgrid(*control_signal_sample_lists)).T.reshape(-1,num_control_signals)

    def _instantiate_control_signal(self, control_signal, context=None):
        '''Implement ControlSignalCosts.DEFAULTS as default for cost_option of ControlSignals
        EVCControlMechanism requires use of at least one of the cost options
        '''
        control_signal = super()._instantiate_control_signal(control_signal, context)

        if control_signal.cost_options is None:
            control_signal.cost_options = ControlSignalCosts.DEFAULTS
            control_signal._instantiate_cost_attributes()
        return control_signal

    def _execute(self, variable=None, runtime_params=None, context=None):
        """Determine `allocation_policy <LVOCControlMechanism.allocation_policy>` for current run of Composition

        # OLD: -----------------------------------------------------------------------------------------------

        Call self.function -- default: LearnAllocationPolicy:
            does gradient descent based on `predictor_values <LVOCControlMechanism.predictor_values>`, and outcome
            received from the `objective_mechanism <LVOCControlMechanism.objective_mechanism>` to determine the
            `allocation_policy <LVOCControlMechanism.allocation_policy>`.
        Return an allocation_policy

        # NEW: -----------------------------------------------------------------------------------------------
        Update prediction_weights to better predct outcome of `LVOCControlMechanism's <LVOCControlMechanism>`
        `objective_mechanism <LVOCControlMechanism.objective_mechanism>` from prediction_vector, then optimize
        `allocation_policy <LVOCControlMechanism>` given new prediction_weights.

        variable should have two items:  current prediction_vector and outcome
        Call `learning_function <LearnAllocationPolicy.learning_function>` to update prediction_weights.
        Call `gradient_ascent` to optimize `allocation_policy <LVOCControlMechahism.allocation_policy>` given new
        prediction_weights.
        # -----------------------------------------------------------------------------------------------
        """

        if (self.context.initialization_status == ContextFlags.INITIALIZING or
                self.owner.context.initialization_status == ContextFlags.INITIALIZING):
            return defaultControlAllocation

        # Get sample of weights
        # IMPLEMENTATION NOTE: skip ControlMechanism._execute since it is a stub method that returns input_values
        self.prediction_weights = super(ControlMechanism, self)._execute(controller=self,
                                                                         variable=variable,
                                                                         runtime_params=runtime_params,
                                                                         context=context
                                                                         )

        # Compute allocation_policy using gradient_ascent
        allocation_policy = self.gradient_ascent(self.control_signals,
                                                 self.prediction_vector,
                                                 self.prediction_weights)

        return allocation_policy.reshape((len(allocation_policy),1))

    def _parse_function_variable(self, variable, context=None):
        '''Update prediction_vector and return along with outcome from `objective_mechanism
        <LVOCControlMechanism.objective_mechanism>` '''

        # This the value received from the ObjectiveMechanism:
        outcome = np.atleast_2d(variable[0])

        # This is the current values of the predictors
        self.predictor_values = np.array(variable[1:]).reshape(-1)

        # Initialize attributes
        if context is ContextFlags.INSTANTIATE:
            # Numbers of terms in prediction_vector
            self.num_predictors = len(self.predictor_values)
            self.num_control_signals = self.num_costs = len(self.control_signals)
            self.num_interactions = self.num_predictors * self.num_control_signals
            len_prediction_vector = \
                self.num_predictors + self.num_interactions + self.num_control_signals + self.num_costs

            # Indices for fields of prediction_vector
            self.pred = slice(0, self.num_predictors)
            self.intrxn= slice(self.num_predictors, self.num_predictors+self.num_interactions)
            self.ctl = slice(self.intrxn.stop, self.intrxn.stop + self.num_control_signals)
            self.cst = slice(self.ctl.stop, len_prediction_vector)

            self.prediction_vector = np.zeros(len_prediction_vector)

        else:
            # Populate fields (subvectors) of prediction_vector
            self.prediction_vector[self.pred] = self.predictor_values
            self.prediction_vector[self.ctl] = np.array([c.value for c in self.control_signals]).reshape(-1)
            self.prediction_vector[self.intrxn]= \
                np.array(self.prediction_vector[self.pred] *
                         self.prediction_vector[self.ctl].reshape(self.num_control_signals,1)).reshape(-1)
            self.prediction_vector[self.cst] = \
                np.array([0 if c.cost is None else c.cost for c in self.control_signals]).reshape(-1) * -1

        # return [np.atleast_2d(self.prediction_vector), np.atleast_2d(outcome)]
        return [self.prediction_vector, outcome]

    def gradient_ascent(self, control_signals, prediction_vector, prediction_weights):
        '''Determine the `allocation_policy <LVOCControlMechanism.allocation_policy>` that maximizes the `EVC
        <LVOCControlMechanism_EVC>`.

        Iterate over prediction_vector; for each iteration: \n
        - compute gradients based on current control_signal values and their costs (in prediction_vector);
        - compute new control_signal values based on gradients;
        - update prediction_vector with new control_signal values and the interaction terms and costs based on those;
        - use prediction_weights and updated prediction_vector to compute new `EVC <LVOCControlMechanism_EVC>`.

        Continue to iterate until difference between new and old EVC is less than `convergence_criterion
        <LearnAllocationPolicy.convergence_criterion>` or number of iterations exceeds `max_iterations
        <LearnAllocationPolicy.max_iterations>`.

        Return control_signals field of prediction_vector (used by LVOCControlMechanism as its `allocation_vector
        <LVOCControlMechanism.allocation_policy>`).

        '''

        convergence_metric = self.convergence_criterion + EPSILON
        previous_lvoc = np.finfo(np.float128).max

        predictors = prediction_vector[0:self.num_predictors]

        # Get interaction weights and reshape so that there is one row per control_signal
        #    containing the terms for the interaction of that control_signal with each of the predictors
        interaction_weights = prediction_weights[self.intrxn].reshape(self.num_control_signals,self.num_predictors)
        # multiply interactions terms by predictors (since those don't change during the gradient ascent)
        interaction_weights_x_predictors = interaction_weights * predictors

        control_signal_values = prediction_vector[self.ctl]
        control_signal_weights = prediction_weights[self.ctl]

        gradient_constants = np.zeros(self.num_control_signals)
        for i in range(self.num_control_signals):
            gradient_constants[i] = control_signal_weights[i]
            gradient_constants[i] += np.sum(interaction_weights_x_predictors[i])

        costs = prediction_vector[self.cst]
        cost_weights = prediction_weights[self.cst]

        # TEST PRINT:
        # print('\n\npredictors: ', predictors,
        #       '\ncontrol_signals: ', control_signal_values,
        #       '\ncontrol_costs: ', costs,
        #       '\nprediction_weights: ', prediction_weights)
        # TEST PRINT END:

        # Perform gradient ascent until convergence criterion is reached
        j=0
        while convergence_metric > self.convergence_criterion:
            # initialize gradient arrray (one gradient for each control signal)
            gradient = np.copy(gradient_constants)
            cost_gradient = np.zeros(self.num_costs)

            for i, control_signal_value in enumerate(control_signal_values):

                # Recompute costs and add to gradient
                cost_function_derivative = control_signals[i].intensity_cost_function.__self__.derivative
                cost_gradient[i] = -(cost_function_derivative(control_signal_value) * cost_weights[i])
                gradient[i] += cost_gradient[i]

                # Update control_signal_value with gradient
                control_signal_values[i] = control_signal_value + self.udpate_rate * gradient[i]

                # Update cost based on new control_signal_value
                costs[i] = -(control_signals[i].intensity_cost_function(control_signal_value))

            # Assign new values of interaction terms, control_signals and costs to prediction_vector
            prediction_vector[self.intrxn]= np.array(prediction_vector[self.pred] *
                                                     prediction_vector[self.ctl].reshape(self.num_control_signals,1)).\
                                                     reshape(-1)
            prediction_vector[self.ctl] = control_signal_values
            prediction_vector[self.cst] = costs

            # Compute current LVOC using current features, weights and new control signals
            current_lvoc = self.compute_lvoc(prediction_vector, prediction_weights)

            # Compute convergence metric with updated control signals
            convergence_metric = np.abs(current_lvoc - previous_lvoc)

            # TEST PRINT:
            # print('\niteration ', j,
            #       '\nprevious_lvoc: ', previous_lvoc,
            #       '\ncurrent_lvoc: ',current_lvoc ,
            #       '\nconvergence_metric: ',convergence_metric,
            #       '\npredictors: ', predictors,
            #       '\ncontrol_signal_values: ', control_signal_values,
            #       '\ninteractions: ', interaction_weights_x_predictors,
            #       '\ncosts: ', costs)
            # TEST PRINT END

            j+=1
            if j > self.max_iterations:
                warnings.warn("{} failed to converge after {} iterations".format(self.name, self.max_iterations))
                break

            previous_lvoc = current_lvoc

        return control_signal_values

    def compute_lvoc(self, v, w):
        return np.sum(v * w)
