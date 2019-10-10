# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# **************************************  ControlMechanism ************************************************

"""
Sections
--------

  * `ControlMechanism_Overview`
  * `ControlMechanism_Composition_Controller`
  * `ControlMechanism_Creation`
      - `ControlMechanism_Monitor_for_Control`
      - `ControlMechanism_ObjectiveMechanism`
      - `ControlMechanism_Control_Signals`
  * `ControlMechanism_Structure`
      - `ControlMechanism_Input`
      - `ControlMechanism_Function`
      - 'ControlMechanism_Output`
      - `ControlMechanism_Costs_NetOutcome`
  * `ControlMechanism_Execution`
  * `ControlMechanism_Examples`
  * `ControlMechanism_Class_Reference`

.. _ControlMechanism_Overview:

Overview
--------

A ControlMechanism is a `ModulatoryMechanism` that `modulates the value(s) <ModulatorySignal_Modulation>` of one or
more `States <State>` of other Mechanisms in the `Composition` to which it belongs. In general, a ControlMechanism is
used to modulate the `ParameterState(s) <ParameterState>` of one or more Mechanisms, that determine the value(s) of
the parameter(s) of the `function(s) <Mechanism_Base.function>` of those Mechanism(s). However, a ControlMechanism
can also be used to modulate the function of `InputStates <InputState>` and/or `OutputState <OutputStates>`,
much like a `GatingMechanism`.  A ControlMechanism's `function <ControlMechanism.function>` calculates a
`control_allocation <ControlMechanism.control_allocation>`: a list of values provided to each of its `control_signals
<ControlMechanism.control_signals>`.  Its control_signals are `ControlSignal` OutputStates that are used to modulate
the parameters of other Mechanisms' `function <Mechanism_Base.function>` (see `ControlSignal_Modulation` for a more
detailed description of how modulation operates).  A ControlMechanism can be configured to monitor the outputs of
other Mechanisms in order to determine its `control_allocation <ControlMechanism.control_allocation>`, by specifying
these in the **monitor_for_control** `argument <ControlMechanism_Monitor_for_Control_Argument>` of its constructor,
or in the **monitor** `argument <ObjectiveMechanism_Monitor>` of an ObjectiveMechanism` assigned to its
**objective_mechanism** `argument <ControlMechanism_Objective_Mechanism_Argument>` (see `ControlMechanism_Creation`
below).  A ControlMechanism can also be assigned as the `controller <Composition.controller>` of a `Composition`,
which has a special relation to that Composition: it generally executes either before or after all of the other
Mechanisms in that Composition (see `Composition_Controller_Execution`).  The OutputStates monitored by the
ControlMechanism or its `objective_mechanism <ControlMechanism.objective_mechanism>`, and the parameters it modulates
can be listed using its `show <ControlMechanism.show>` method.

.. _ControlMechanism_Composition_Controller:

*ControlMechanisms and a Composition*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ControlMechanism can be assigned to a `Composition` and executed just like any other Mechanism. It can also be
assigned as the `controller <Composition.controller>` of a `Composition`, that has a special relation
to the Composition: it is used to control all of the parameters that have been `specified for control
<ControlMechanism_Control_Signals>` in that Composition.  A ControlMechanism can be the `controller
<Composition.controller>` for only one Composition, and a Composition can have only one `controller
<Composition.controller>`.  When a ControlMechanism is assigned as the `controller <Composition.controller>` of a
Composition (either in the Composition's constructor, or using its `add_controller <Composition.add_controller>`
method, the ControlMechanism assumes control over all of the parameters that have been `specified for control
<ControlMechanism_Control_Signals>` for Components in the Composition.  The Composition's `controller
<Composition.controller>` is executed either before or after all of the other Components in the Composition are
executed, including any other ControlMechanisms that belong to it (see `Composition_Controller_Execution`).  A
ControlMechanism can be assigned as the `controller <Composition.controller>` for a Composition by specifying it in
the **controller** argument of the Composition's constructor, or by using the Composition's `add_controller
<Composition.add_controller>` method.  A Composition's `controller <Composition.controller>` and its associated
Components can be displayed using the Composition's `show_graph <Composition.show_graph>` method with its
**show_control** argument assigned as `True`.


.. _ControlMechanism_Creation:

Creating a ControlMechanism
---------------------------

A ControlMechanism is created by calling its constructor.  When a ControlMechanism is created, the OutputStates it
monitors and the States it modulates can be specified in the **montior_for_control** and **objective_mechanism**
arguments of its constructor, respectively.  Each can be specified in several ways, as described below. If neither of
those arguments is specified, then only the ControlMechanism is constructed, and its inputs and the parameters it
modulates must be specified in some other way.

.. _ControlMechanism_Monitor_for_Control:

*Specifying OutputStates to be monitored*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ControlMechanism can be configured to monitor the output of other Mechanisms directly (by receiving direct
Projections from their OutputStates), or by way of an `ObjectiveMechanism` that evaluates those outputs and passes the
result to the ControlMechanism (see `below <ControlMechanism_ObjectiveMechanism>` for more detailed description).
The following figures show an example of each:

+-------------------------------------------------------------------------+----------------------------------------------------------------------+
| .. figure:: _static/ControlMechanism_without_ObjectiveMechanism_fig.svg | .. figure:: _static/ControlMechanism_with_ObjectiveMechanism_fig.svg |
+-------------------------------------------------------------------------+----------------------------------------------------------------------+

COMMENT:
FIX: USE THIS IF MOVED TO SECTION AT END THAT CONSOLIDATES EXAMPLES
**ControlMechanism with and without ObjectiveMechanism**

+-------------------------------------------------------------------------+-------------------------------------------------------------------------+
| >>> mech_A = ProcessingMechanism(name='ProcessingMechanism A')          | .. figure:: _static/ControlMechanism_without_ObjectiveMechanism_fig.svg |
| >>> mech_B = ProcessingMechanism(name='ProcessingMechanism B')          |                                                                         |
| >>> ctl_mech = ControlMechanism(name='ControlMechanism',                |                                                                         |
| ...                             monitor_for_control=[mech_A,            |                                                                         |
| ...                                                  mech_B],           |                                                                         |
| ...                             control_signals=[(SLOPE,mech_A),        |                                                                         |
| ...                                              (SLOPE,mech_B)])       |                                                                         |
| >>> comp = Composition()                                                |                                                                         |
| >>> comp.add_linear_processing_pathway([mech_A,mech_B, ctl_mech])       |                                                                         |
| >>> comp.show_graph()                                                   |                                                                         |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------+
| >>> mech_A = ProcessingMechanism(name='ProcessingMechanism A')          | .. figure:: _static/ControlMechanism_with_ObjectiveMechanism_fig.svg    |
| >>> mech_B = ProcessingMechanism(name='ProcessingMechanism B')          |                                                                         |
| >>> ctl_mech = ControlMechanism(name='ControlMechanism',                |                                                                         |
| ...                             monitor_for_control=[mech_A,            |                                                                         |
| ...                                                  mech_B],           |                                                                         |
| ...                             objective_mechanism=True,               |                                                                         |
| ...                             control_signals=[(SLOPE,mech_A),        |                                                                         |
| ...                                              (SLOPE,mech_B)])       |                                                                         |
| >>> comp = Composition()                                                |                                                                         |
| >>> comp.add_linear_processing_pathway([mech_A,mech_B, ctl_mech])       |                                                                         |
| >>> comp.show_graph()                                                   |                                                                         |
+-------------------------------------------------------------------------+-------------------------------------------------------------------------+
COMMENT

Note that, in the figures above, the `ControlProjections <ControlProjection>` are designated with square "arrowheads",
and the ControlMechanisms are shown as septagons to indicate that their ControlProjections create a feedback loop
(see `Composition_Initial_Values_and_Feedback`;  also, see `below <ControlMechanism_Add_Linear_Processing_Pathway>`
regarding specification of a ControlMechanism and associated ObjectiveMechanism in a Composition's
`add_linear_processing_pathway <Composition.add_linear_processing_pathway>` method).

Which configuration is used is determined by how the following arguments of the ControlMechanism's constructor are
specified (also see `ControlMechanism_Examples`):

  .. _ControlMechanism_Monitor_for_Control_Argument:

  * **monitor_for_control** -- a list of `OutputState specifications <OutputState_Specification>`.  If the
    **objective_mechanism** argument is not specified (or is *False* or *None*) then, when the ControlMechanism is
    added to a `Composition`, a `MappingProjection` is created for each OutputState specified to the ControlMechanism's
    *OUTCOME* `input_state <ControlMechanism_Input>`.  If the **objective_mechanism** `argument
    <ControlMechanism_Objective_Mechanism_Argument>` is specified, then the OutputStates specified in
    **monitor_for_control** are assigned to the `ObjectiveMechanism` rather than the ControlMechanism itself (see
    `ControlMechanism_ObjectiveMechanism` for details).

  .. _ControlMechanism_Objective_Mechanism_Argument:

  * **objective_mechanism** -- if this is specfied in any way other than **False** or **None** (the default),
    then an ObjectiveMechanism is created that projects to the ControlMechanism and, when added to a `Composition`,
    is assigned Projections from all of the OutputStates specified either in the  **monitor_for_control** argument of
    the ControlMechanism's constructor, or the **monitor** `argument <ObjectiveMechanism_Monitor>` of the
    ObjectiveMechanism's constructor (see `ControlMechanism_ObjectiveMechanism` for details).  The
    **objective_mechanism** argument can be specified in any of the following ways:

    - *False or None* -- no ObjectiveMechanism is created and, when the ControlMechanism is added to a
      `Composition`, Projections from the OutputStates specified in the ControlMechanism's **monitor_for_control**
      argument are sent directly to ControlMechanism (see specification of **monitor_for_control** `argument
      <ControlMechanism_Monitor_for_Control_Argument>`).

    - *True* -- an `ObjectiveMechanism` is created that projects to the ControlMechanism, and any OutputStates
      specified in the ControlMechanism's **monitor_for_control** argument are assigned to ObjectiveMechanism's
      **monitor** `argument <ObjectiveMechanism_Monitor>` instead (see `ControlMechanism_ObjectiveMechanism` for
      additional details).

    - *a list of* `OutputState specifications <ObjectiveMechanism_Monitor>`; an ObjectiveMechanism is created that
      projects to the ControlMechanism, and the list of OutputStates specified, together with any specified in the
      ControlMechanism's **monitor_for_control** `argument <ControlMechanism_Monitor_for_Control_Argument>`, are
      assigned to the ObjectiveMechanism's **monitor** `argument <ObjectiveMechanism_Monitor>` (see
      `ControlMechanism_ObjectiveMechanism` for additional details).

    - *a constructor for an* `ObjectiveMechanism` -- the specified ObjectiveMechanism is created, adding any
      OutputStates specified in the ControlMechanism's **monitor_for_control** `argument
      <ControlMechanism_Monitor_for_Control_Argument>` to any specified in the ObjectiveMechanism's **monitor**
      `argument <ObjectiveMechanism_Monitor>` .  This can be used to specify the `function
      <ObjectiveMechanism.function>` used by the ObjectiveMechanism to evaluate the OutputStates monitored as well as
      how it weights those OutputStates when they are evaluated  (see `below
      <ControlMechanism_ObjectiveMechanism_Function>` for additional details).

    - *an existing* `ObjectiveMechanism` -- for any OutputStates specified in the ControlMechanism's
      **monitor_for_control** `argument <ControlMechanism_Monitor_for_Control_Argument>`, an InputState is added to the
      ObjectiveMechanism, along with `MappingProjection` to it from the specified OutputState.    This can be used to
      specify an ObjectiveMechanism with a custom `function <ObjectiveMechanism.function>` and weighting of the
      OutputStates monitored (see `below <ControlMechanism_ObjectiveMechanism_Function>` for additional details).

The OutputStates monitored by a ControlMechanism or its `objective_mechanism <ControlMechanism.objective_mechanism>`
are listed in the ControlMechanism's `monitor_for_control <ControlMechanism.monitor_for_control>` attribute
(and are the same as those listed in the `monitor <ObjectiveMechanism.monitor>` attribute of the
`objective_mechanism <ControlMechanism.objective_mechanism>`, if specified).

.. _ControlMechanism_Add_Linear_Processing_Pathway:

Note that the MappingProjections created by specification of a ControlMechanism's **monitor_for_control** `argument
<ControlMechanism_Monitor_for_Control_Argument>` or the **monitor** argument in the constructor for an
ObjectiveMechanism in the ControlMechanism's **objective_mechanism** `argument
<ControlMechanism_Objective_Mechanism_Argument>` supercede any MappingProjections that would otherwise be created for
them when included in the **pathway** argument of a Composition's `add_linear_processing_pathway
<Composition.add_linear_processing_pathway>` method.

.. _ControlMechanism_ObjectiveMechanism:

Objective Mechanism
^^^^^^^^^^^^^^^^^^^

COMMENT:
TBI FOR COMPOSITION
If the ControlMechanism is created automatically by a System (as its `controller <System.controller>`), then the
specification of OutputStates to be monitored and parameters to be controlled are made on the System and/or the
Components themselves (see `System_Control_Specification`).  In either case, the Components needed to monitor the
specified OutputStates (an `ObjectiveMechanism` and `Projections <Projection>` to it) and to control the specified
parameters (`ControlSignals <ControlSignal>` and corresponding `ControlProjections <ControlProjection>`) are created
automatically, as described below.
COMMENT

If an `ObjectiveMechanism` is specified for a ControlMechanism (in the **objective_mechanism** `argument
<ControlMechanism_Objective_Mechanism_Argument>` of its constructor; also see `ControlMechanism_Examples`),
it is assigned to the ControlMechanism's `objective_mechanism <ControlMechanism.objective_mechanism>` attribute,
and a `MappingProjection` is created automatically that projects from the ObjectiveMechanism's *OUTCOME*
`output_state <ObjectiveMechanism_Output>` to the *OUTCOME* `input_state <ControlMechanism_Input>` of the
ControlMechanism.

The `objective_mechanism <ControlMechanism.objective_mechanism>` is used to monitor the OutputStates
specified in the **monitor_for_control** `argument <ControlMechanism_Monitor_for_Control_Argument>` of the
ControlMechanism's constructor, as well as any specified in the **monitor** `argument <ObjectiveMechanism_Monitor>` of
the ObjectiveMechanism's constructor.  Specifically, for each OutputState specified in either place, an `input_state
<ObjectiveMechanism.input_states>` is added to the ObjectiveMechanism.  OutputStates to be monitored (and
corresponding `input_states <ObjectiveMechanism.input_states>`) can be added to the `objective_mechanism
<ControlMechanism.objective_mechanism>` later, by using its `add_to_monitor <ObjectiveMechanism.add_to_monitor>` method.
The set of OutputStates monitored by the `objective_mechanism <ControlMechanism.objective_mechanism>` are listed in
its `monitor <ObjectiveMechanism>` attribute, as well as in the ControlMechanism's `monitor_for_control
<ControlMechanism.monitor_for_control>` attribute.

When the ControlMechanism is added to a `Composition`, the `objective_mechanism <ControlMechanism.objective_mechanism>`
is also automatically added, and MappingProjectons are created from each of the OutputStates that it monitors to
its corresponding `input_states <ObjectiveMechanism.input_states>`.  When the Composition is run, the `value
<OutputState.value>`\\(s) of the OutputState(s) monitored are evaluated using the `objective_mechanism`\\'s `function
<ObjectiveMechanism.function>`, and the result is assigned to its *OUTCOME* `output_state
<ObjectiveMechanism_Output>`.  That `value <ObjectiveMechanism.value>` is then passed to the ControlMechanism's
*OUTCOME* `input_state <ControlMechanism_Input>`, which is used by the ControlMechanism's `function
<ControlMechanism.function>` to determine its `control_allocation <ControlMechanism.control_allocation>`.

.. _ControlMechanism_ObjectiveMechanism_Function:

If a default ObjectiveMechanism is created by the ControlMechanism (i.e., when *True* or a list of OutputStates is
specified for the **objective_mechanism** `argument <ControlMechanism_Objective_Mechanism_Argument>` of the
constructor), then the ObjectiveMechanism is created with its standard default `function <ObjectiveMechanism.function>`
(`LinearCombination`), but using *PRODUCT* (rather than the default, *SUM*) as the value of the function's `operation
<LinearCombination.operation>` parameter. The result is that the `objective_mechanism
<ControlMechanism.objective_mechanism>` multiplies the `value <OutputState.value>`\\s of the OutputStates that it
monitors, which it passes to the ControlMechanism.  However, if the **objective_mechanism** is specified using either
a constructor for, or an existing ObjectiveMechanism, then the defaults for the `ObjectiveMechanism` class -- and any
attributes explicitly specified in its construction -- are used.  In that case, if the `LinearCombination` with
*PRODUCT* as its `operation <LinearCombination.operation>` parameter are still desired, this must be explicitly
specified.  This is illustrated in the following examples.

The following example specifies a `ControlMechanism` that automatically constructs its `objective_mechanism
<ControlMechanism.objective_mechanism>`::

    >>> from psyneulink import *
    >>> my_ctl_mech = ControlMechanism(objective_mechanism=True)
    >>> assert isinstance(my_ctl_mech.objective_mechanism.function, LinearCombination)
    >>> assert my_ctl_mech.objective_mechanism.function.operation == PRODUCT

Notice that `LinearCombination` was assigned as the `function <ObjectiveMechanism.function>` of the `objective_mechanism
<ControlMechanism.objective_mechanism>`, and *PRODUCT* as its `operation <LinearCombination.operation>` parameter.

By contrast, the following example explicitly specifies the **objective_mechanism** argument using a constructor for
an ObjectiveMechanism::

    >>> my_ctl_mech = ControlMechanism(objective_mechanism=ObjectiveMechanism())
    >>> assert isinstance(my_ctl_mech.objective_mechanism.function, LinearCombination)
    >>> assert my_ctl_mech.objective_mechanism.function.operation == SUM

In this case, the defaults for the ObjectiveMechanism's class are used for its `function <ObjectiveMechanism.function>`,
which is a `LinearCombination` function with *SUM* as its `operation <LinearCombination.operation>` parameter.

Specifying the ControlMechanism's `objective_mechanism <ControlMechanism.objective_mechanism>` with a constructor
also provides greater control over how ObjectiveMechanism evaluates the OutputStates it monitors.  In addition to
specifying its `function <ObjectiveMechanism.function>`, the **monitor_weights_and_exponents** `argument
<ObjectiveMechanism_Monitor_Weights_and_Exponents>` can be used to parameterize the relative contribution made by the
monitored OutputStates when they are evaluated by that `function <ObjectiveMechanism.function>` (see
`ControlMechanism_Examples`).

COMMENT:
TBI FOR COMPOSITION
When a ControlMechanism is created for or assigned as the `controller <Composition.controller>` of a `Composition` (see
`ControlMechanism_Composition_Controller`), any OutputStates specified to be monitored by the System are assigned as
inputs to the ObjectiveMechanism.  This includes any specified in the **monitor_for_control** argument of the
System's constructor, as well as any specified in a MONITOR_FOR_CONTROL entry of a Mechanism `parameter specification
dictionary <ParameterState_Specification>` (see `Mechanism_Constructor_Arguments` and `System_Control_Specification`).

FOR DEVELOPERS:
    If the ObjectiveMechanism has not yet been created, these are added to the **monitored_output_states** of its
    constructor called by ControlMechanism._instantiate_objective_mechanmism;  otherwise, they are created using the
    ObjectiveMechanism.add_to_monitor method.
COMMENT

.. _ControlMechanism_Control_Signals:

*Specifying Parameters to Control*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can be specified in either of two ways:

*On a ControlMechanism itself*

The parameters controlled by a ControlMechanism can be specified in the **control_signals** argument of its constructor;
the argument must be a `specification for one more ControlSignals <ControlSignal_Specification>`.  The parameter to
be controlled must belong to a Component in the same `Composition` as the ControlMechanism when it is added to the
Composition, or an error will occur.

*On a Parameter to be controlled by the `controller <Composition.controller>` of a `Composition`*

Control can also be specified for a parameter where the `parameter itself is specified <ParameterState_Specification>`,
in the constructor for the Component to which it belongs, by including a `ControlProjection`, `ControlSignal` or
the keyword `CONTROL` in a `tuple specification <ParameterState_Tuple_Specification>` for the parameter.  In this
case, the specified parameter will be assigned for control by the `controller <controller.Composition>` of any
`Composition` to which its Component belongs, when the Component is executed in that Composition (see
`ControlMechanism_Composition_Controller`).  Conversely, when a ControlMechanism is assigned as the `controller
<Composition.controller>` of a Composition, a `ControlSignal` is created and assigned to the ControlMechanism
for every parameter of any `Component <Component>` in the Composition that has been `specified for control
<ParameterState_Modulatory_Specification>`.

In general, a `ControlSignal` is created for each parameter specified to be controlled by a ControlMechanism.  These
are a type of `OutputState` that send a `ControlProjection` to the `ParameterState` of the parameter to be
controlled. All of the ControlSignals for a ControlMechanism are listed in its `control_signals
<ControlMechanism.control_signals>` attribute, and all of its ControlProjections are listed in
its`control_projections <ControlMechanism.control_projections>` attribute. Additional parameters to be controlled can
be added to a ControlMechanism by using its `assign_params` method to add a `ControlSignal` for each additional
parameter.  See `ControlMechanism_Examples`.

.. _ControlMechanism_Structure:

Structure
---------

.. _ControlMechanism_Input:

*Input*
~~~~~~~

By default, a ControlMechanism has a single (`primary <InputState_Primary>`) `input_state
<ControlMechanism.input_state>` that is named *OUTCOME*.  If the ControlMechanism has an `objective_mechanism
<ControlMechanism.objective_mechanism>`, then the *OUTCOME* `input_state <ControlMechanism.input_state>` receives a
single `MappingProjection` from the `objective_mechanism <ControlMechanism.objective_mechanism>`\\'s *OUTCOME*
OutputState (see `ControlMechanism_ObjectiveMechanism` for additional details). Otherwise, when the ControlMechanism is
added to a `Composition`, MappingProjections are created that project to the ControlMechanism's *OUTCOME* `input_state
<ControlMechanism.input_state>` from each of the OutputStates specified in the **monitor_for_control** `argument
<ControlMechanism_Monitor_for_Control_Argument>` of its constructor.  The `value <InputState.value>` of the
ControlMechanism's *OUTCOME* InputState is assigned to its `outcome <ControlMechanism.outcome>` attribute),
and is used as the input to the ControlMechanism's `function <ControlMechanism.function>` to determine its
`control_allocation <ControlMechanism.control_allocation>`.

.. _ControlMechanism_Function:

*Function*
~~~~~~~~~~

A ControlMechanism's `function <ControlMechanism.function>` uses its `outcome <ControlMechanism.outcome>`
attribute (the `value <InputState.value>` of its *OUTCOME* `InputState`) to generate a `control_allocation
<ControlMechanism.control_allocation>`.  By default, its `function <ControlMechanism.function>` is assigned
the `DefaultAllocationFunction`, which takes a single value as its input, and assigns that as the value of
each item of `control_allocation <ControlMechanism.control_allocation>`.  Each of these items is assigned as
the allocation for the corresponding  `ControlSignal` in `control_signals <ControlMechanism.control_signals>`. This
distributes the ControlMechanism's input as the allocation to each of its `control_signals
<ControlMechanism.control_signals>`.  This same behavior also applies to any custom function assigned to a
ControlMechanism that returns a 2d array with a single item in its outer dimension (axis 0).  If a function is
assigned that returns a 2d array with more than one item, and it has the same number of `control_signals
<ControlMechanism.control_signals>`, then each ControlSignal is assigned to the corresponding item of the function's
value.  However, these default behaviors can be modified by specifying that individual ControlSignals reference
different items in `control_allocation` as their `variable <ControlSignal.variable>`
(see `OutputState_Variable`).

.. _ControlMechanism_Output:

*Output*
~~~~~~~~

The OutputStates of a ControlMechanism are `ControlSignals <ControlSignal>` (listed in its `control_signals
<ControlMechanism.control_signals>` attribute). It has a `ControlSignal` for each parameter specified in the
**control_signals** argument of its constructor, that sends a `ControlProjection` to the `ParameterState` for the
corresponding parameter.  The ControlSignals are listed in the `control_signals <ControlMechanism.control_signals>`
attribute;  since they are a type of `OutputState`, they are also listed in the ControlMechanism's `output_states
<ControlMechanism.output_states>` attribute. The parameters modulated by a ControlMechanism's ControlSignals can be
displayed using its `show <ControlMechanism.show>` method. By default, each `ControlSignal` is assigned as its
`allocation <ControlSignal.allocation>` the value of the  corresponding item of the ControlMechanism's
`control_allocation <ControlMechanism.control_allocation>`;  however, subtypes of ControlMechanism may assign
allocations differently. The `default_allocation  <ControlMechanism.default_allocation>` attribute can be used to
specify a  default allocation for ControlSignals that have not been assigned their own `default_allocation
<ControlSignal.default_allocation>`. The `allocation <ControlSignal.allocation>` is used by each ControlSignal to
determine its `intensity <ControlSignal.intensity>`, which is then assigned to the `value <ControlProjection.value>`
of the ControlSignal's `ControlProjection`.   The `value <ControlProjection.value>` of the ControlProjection is used
by the `ParameterState` to which it projects to modify the value of the parameter it controls (see
`ControlSignal_Modulation` for description of how a ControlSignal modulates the value of a parameter).

.. _ControlMechanism_Costs_NetOutcome:

*Costs and Net Outcome*
~~~~~~~~~~~~~~~~~~~~~~~

A ControlMechanism's `control_signals <ControlMechanism.control_signals>` are each associated with a set of `costs
<ControlSignal_Costs>`, that are computed individually by each `ControlSignal` when they are `executed
<ControlSignal_Execution>` by the ControlMechanism.  The costs last computed by the `control_signals
<ControlMechanism>` are assigned to the ControlMechanism's `costs <ControlSignal.costs>` attribute.  A ControlMechanism
also has a set of methods -- `combine_costs <ControlMechanism.combine_costs>`, `compute_reconfiguration_cost
<ControlMechanism.compute_reconfiguration_cost>`, and `compute_net_outcome <ControlMechanism.compute_net_outcome>` --
that can be used to compute the `combined costs <ControlMechanism.combined_costs>` of its `control_signals
<ControlMechanism.control_signals>`, a `reconfiguration_cost <ControlSignal.reconfiguration_cost>` based on their change
in value, and a `net_outcome <ControlMechanism.net_outcome>` (the `value <InputState.value>` of the ControlMechanism's
*OUTCOME* `input_state <ControlMechanism_Input>` minus its `combined costs <ControlMechanism.combined_costs>`),
respectively (see `ControlMechanism_Costs_Computation` below for additional details). These methods are used by some
subclasses of ControlMechanism (e.g., `OptimizationControlMechanism`) to compute their `control_allocation
<ControlMechanism.control_allocation>`.  Each method is assigned a default function, but can be assigned a custom
functions in a corrsponding argument of the ControlMechanism's constructor (see links to attributes for details).

.. _ControlMechanism_Reconfiguration_Cost:

*Reconfiguration Cost*

A ControlMechanism's `reconfiguration_cost <ControlMechanism.reconfiguration_cost>` is distinct from the
costs of the ControlMechanism's `ControlSignals <ControlSignal>`, and in particular it is not the same as their
`adjustment_cost <ControlSignal.adjustment_cost>`.  The latter, if specified by a ControlSignal, is computed
individually by that ControlSignal using its `adjustment_cost_function <ControlSignal.adjustment_cost_function>`, based
on the change in its `intensity <ControlSignal.intensity>` from its last execution. In contrast, a ControlMechanism's
`reconfiguration_cost  <ControlMechanism.reconfiguration_cost>` is computed by its `compute_reconfiguration_cost
<ControlMechanism.compute_reconfiguration_cost>` function, based on the change in its `control_allocation
ControlMechanism.control_allocation>` from the last execution, that will be applied to *all* of its
`control_signals <ControlMechanism.control_signals>`. By default, `compute_reconfiguration_cost
<ControlMechanism.compute_reconfiguration_cost>` is assigned as the `Distance` function with the `EUCLIDEAN` metric).

.. _ControlMechanism_Execution:

Execution
---------

If a ControlMechanism is assigned as the `controller` of a `Composition`, then it is executed either before or after
all of the other  `Mechanisms <Mechanism_Base>` executed in a `TRIAL` for that Composition, depending on the
value assigned to the Composition's `controller_mode <Composition.controller_mode>` attribute (see
`Composition_Controller_Execution`).  If a ControlMechanism is added to a Composition for which it is not a
`controller <Composition.controller>`, then it executes in the same way as a `ProcessingMechanism
<ProcessingMechanism>`, based on its place in the Composition's `graph <Composition.graph>`.  Because
`ControlProjections <ControlProjection>` are likely to introduce cycles (recurrent connection loops) in the graph,
the effects of a ControlMechanism and its projections will generally not be applied in the first `TRIAL` (see
COMMENT:
FIX 8/27/19 [JDC]:
`Composition_Initial_Values_and_Feedback` and
COMMENT
**feedback** argument for the `add_projection <Composition.add_projection>` method of `Composition` for a
description of how to configure the initialization of feedback loops in a Composition; also see `Scheduler` for a
description of detailed ways in which a GatingMechanism and its dependents can be scheduled to execute).

The ControlMechanism's `function <ControlMechanism.function>` takes as its input the `value <InputState.value>` of
its *OUTCOME* `input_state <ControlMechanism.input_state>` (also contained in `outcome <ControlSignal.outcome>`).
It uses that to determine the `control_allocation <ControlMechanism.control_allocation>`, which specifies the value
assigned to the `allocation <ControlSignal.allocation>` of each of its `ControlSignals <ControlSignal>`.  Each
ControlSignal uses that value to calculate its `intensity <ControlSignal.intensity>`, as well as its `cost
<ControlSignal.cost>.  The `intensity <ControlSignal.intensity>`is used by its `ControlProjection(s)
<ControlProjection>` to modulate the value of the ParameterState(s) for the parameter(s) it controls, which are then
used in the subsequent `TRIAL` of execution.

.. note::
   `States <State>` that receive a `ControlProjection` does not update its value until its owner Mechanism
   executes (see `Lazy Evaluation <LINK>` for an explanation of "lazy" updating).  This means that even if a
   ControlMechanism has executed, a parameter that it controls will not assume its new value until the Mechanism
   to which it belongs has executed.

.. _ControlMechanism_Costs_Computation:

*Computation of Costs and Net_Outcome*

Once the ControlMechanism's `function <ControlMechanism.function>` has executed, if `compute_reconfiguration_cost
<ControlMechanism.compute_reconfiguration_cost>` has been specified, then it is used to compute the
`reconfiguration_cost <ControlMechanism.reconfiguration_cost>` for its `control_allocation
<ControlMechanism.control_allocation>` (see `above <ControlMechanism_Reconfiguration_Cost>`. After that, each
of the ControlMechanism's `control_signals <ControlMechanism.control_signals>` calculates its `cost
<ControlSignal.cost>`, based on its `intensity  <ControlSignal/intensity>`.  The ControlMechanism then combines these
with the `reconfiguration_cost <ControlMechanism.reconfiguration_cost>` using its `combine_costs
<ControlMechanism.combine_costs>` function, and the result is assigned to the `costs <ControlMechanism.costs>`
attribute.  Finally, the ControlMechanism uses this, together with its `outcome <ControlMechanism.outcome>` attribute,
to compute a `net_outcome <ControlMechanism.net_outcome>` using its `compute_net_outcome
<ControlMechanism.compute_net_outcome>` function.  This is used by some subclasses of ControlMechanism
(e.g., `OptimizationControlMechanism`) to  compute its `control_allocation <ControlMechanism.control_allocation>`
for the next `TRIAL` of execution.

.. _ControlMechanism_Examples:

Examples
--------

The following example creates a ControlMechanism by specifying its **objective_mechanism** using a constructor
that specifies the OutputStates to be monitored by its `objective_mechanism <ControlMechanism.objective_mechanism>`
and the function used to evaluated these::

    >>> my_mech_A = ProcessingMechanism(name="Mech A")
    >>> my_DDM = DDM(name="My DDM")
    >>> my_mech_B = ProcessingMechanism(function=Logistic,
    ...                                            name="Mech B")

    >>> my_control_mech = ControlMechanism(
    ...                          objective_mechanism=ObjectiveMechanism(monitor=[(my_mech_A, 2, 1),
    ...                                                                           my_DDM.output_states[RESPONSE_TIME]],
    ...                                                                     name="Objective Mechanism"),
    ...                          function=LinearCombination(operation=PRODUCT),
    ...                          control_signals=[(THRESHOLD, my_DDM),
    ...                                           (GAIN, my_mech_B)],
    ...                          name="My Control Mech")

This creates an ObjectiveMechanism for the ControlMechanism that monitors the `primary OutputState
<OutputState_Primary>` of ``my_mech_A`` and the *RESPONSE_TIME* OutputState of ``my_DDM``;  its function
first multiplies the former by 2 before, then takes product of their values and passes the result as the input to the
ControlMechanism.  The ControlMechanism's `function <ControlMechanism.function>` uses this value to determine
the allocation for its ControlSignals, that control the value of the `threshold <DDM.threshold>` parameter of
``my_DDM`` and the  `gain <Logistic.gain>` parameter of the `Logistic` Function for ``my_transfer_mech_B``.

The following example specifies the same set of OutputStates for the ObjectiveMechanism, by assigning them directly
to the **objective_mechanism** argument::

    >>> my_control_mech = ControlMechanism(
    ...                             objective_mechanism=[(my_mech_A, 2, 1),
    ...                                                  my_DDM.output_states[RESPONSE_TIME]],
    ...                             control_signals=[(THRESHOLD, my_DDM),
    ...                                              (GAIN, my_mech_B)])

Note that, while this form is more succinct, it precludes specifying the ObjectiveMechanism's function.  Therefore,
the values of the monitored OutputStates will be added (the default) rather than multiplied.

The ObjectiveMechanism can also be created on its own, and then referenced in the constructor for the ControlMechanism::

    >>> my_obj_mech = ObjectiveMechanism(monitored_output_states=[(my_mech_A, 2, 1),
    ...                                                            my_DDM.output_states[RESPONSE_TIME]],
    ...                                      function=LinearCombination(operation=PRODUCT))

    >>> my_control_mech = ControlMechanism(
    ...                        objective_mechanism=my_obj_mech,
    ...                        control_signals=[(THRESHOLD, my_DDM),
    ...                                         (GAIN, my_mech_B)])

Here, as in the first example, the constructor for the ObjectiveMechanism can be used to specify its function, as well
as the OutputState that it monitors.

COMMENT:
FIX 8/27/19 [JDC]:  ADD TO COMPOSITION
See `System_Control_Examples` for examples of how a ControlMechanism, the OutputStates its
`objective_mechanism <ControlSignal.objective_mechanism>`, and its `control_signals <ControlMechanism.control_signals>`
can be specified for a System.
COMMENT

.. _ControlMechanism_Class_Reference:

Class Reference
---------------

"""

import copy
import itertools
import numpy as np
import threading
import typecheck as tc
import warnings

from psyneulink.core import llvm as pnlvm
from psyneulink.core.components.functions.function import Function_Base, is_function_type
from psyneulink.core.components.functions.combinationfunctions import LinearCombination
from psyneulink.core.components.mechanisms.modulatory.modulatorymechanism import ModulatoryMechanism_Base
from psyneulink.core.components.mechanisms.mechanism import Mechanism, Mechanism_Base
from psyneulink.core.components.shellclasses import Composition_Base, System_Base
from psyneulink.core.components.states.state import State, _parse_state_spec
from psyneulink.core.components.states.modulatorysignals.controlsignal import ControlSignal
from psyneulink.core.components.states.inputstate import InputState
from psyneulink.core.components.states.outputstate import OutputState
from psyneulink.core.components.states.parameterstate import ParameterState
from psyneulink.core.globals.context import ContextFlags, handle_external_context
from psyneulink.core.globals.defaults import defaultControlAllocation
from psyneulink.core.globals.keywords import \
    AUTO_ASSIGN_MATRIX, CONTROL, CONTROL_PROJECTION, CONTROL_PROJECTIONS, CONTROL_SIGNAL, CONTROL_SIGNALS, \
    EID_SIMULATION, GATING_SIGNAL, INIT_EXECUTE_METHOD_ONLY, \
    MODULATORY_SIGNALS, MONITOR_FOR_CONTROL, MONITOR_FOR_MODULATION, MULTIPLICATIVE, \
    OBJECTIVE_MECHANISM, OUTCOME, OWNER_VALUE, PRODUCT, PROJECTION_TYPE, PROJECTIONS, STATE_TYPE, SYSTEM
from psyneulink.core.globals.parameters import Parameter
from psyneulink.core.globals.preferences.basepreferenceset import is_pref_set
from psyneulink.core.globals.preferences.preferenceset import PreferenceLevel
from psyneulink.core.globals.utilities import ContentAddressableList, is_iterable, convert_to_list

__all__ = [
    'CONTROL_ALLOCATION', 'GATING_ALLOCATION', 'ControlMechanism', 'ControlMechanismError', 'ControlMechanismRegistry',
    'DefaultAllocationFunction'
]

CONTROL_ALLOCATION = 'control_allocation'
GATING_ALLOCATION = 'gating_allocation'

ControlMechanismRegistry = {}

def _is_control_spec(spec):
    from psyneulink.core.components.projections.modulatory.controlprojection import ControlProjection
    if isinstance(spec, tuple):
        return any(_is_control_spec(item) for item in spec)
    if isinstance(spec, dict) and PROJECTION_TYPE in spec:
        return _is_control_spec(spec[PROJECTION_TYPE])
    elif isinstance(spec, (ControlMechanism,
                           ControlSignal,
                           ControlProjection)):
        return True
    elif isinstance(spec, type) and issubclass(spec, (ControlMechanism,
                                                      ControlSignal,
                                                      ControlProjection)):
        return True
    elif isinstance(spec, str) and spec in {CONTROL, CONTROL_PROJECTION, CONTROL_SIGNAL}:
        return True
    else:
        return False

class ControlMechanismError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value


def _control_mechanism_costs_getter(owning_component=None, context=None):
    # NOTE: In cases where there is a reconfiguration_cost, that cost is not returned by this method
    try:
        costs = [c.compute_costs(c.parameters.value._get(context), context=context)
                 for c in owning_component.control_signals
                 if hasattr(c, 'compute_costs')] # GatingSignals don't have cost fcts
        return costs

    except TypeError:
        return None

def _outcome_getter(owning_component=None, context=None):
    try:
        return owning_component.parameters.variable._get(context)[0]
    except TypeError:
        return None

def _net_outcome_getter(owning_component=None, context=None):
    # NOTE: In cases where there is a reconfiguration_cost, that cost is not included in the net_outcome
    try:
        c = owning_component
        return c.compute_net_outcome(c.parameters.outcome._get(context),
                                     c.combine_costs(c.parameters.costs._get(context)))
    except TypeError:
        return [0]

class DefaultAllocationFunction(Function_Base):
    """Take a single 1d item and return a 2d array with n identical items
    Takes the default input (a single value in the *OUTCOME* InputState of the ControlMechanism),
    and returns the same allocation for each of its `control_signals <ControlMechanism.control_signals>`.
    """
    componentName = 'Default Control Function'
    class Parameters(Function_Base.Parameters):
        """
            Attributes
            ----------

                num_control_signals
                    see `num_control_signals <DefaultAllocationFunction.num_control_signals>`

                    :default value: 1
                    :type: int

        """
        num_control_signals = Parameter(1, stateful=False)

    @tc.typecheck
    def __init__(self,
                 default_variable=None,
                 params=None,
                 owner=None
                 ):
        # Assign args to params and functionParams dicts
        params = self._assign_args_to_param_dicts(params=params)
        super().__init__(default_variable=default_variable,
                         params=params,
                         owner=owner,
                         )

    def _function(self,
                 variable=None,
                 context=None,
                 params=None,
                 ):
        num_ctl_sigs = self.get_current_function_param('num_control_signals')
        result = np.array([variable[0]] * num_ctl_sigs)
        return self.convert_output_type(result)

    def _gen_llvm_function_body(self, ctx, builder, _1, _2, arg_in, arg_out):
        val_ptr = builder.gep(arg_in, [ctx.int32_ty(0), ctx.int32_ty(0)])
        val = builder.load(val_ptr)
        with pnlvm.helpers.array_ptr_loop(builder, arg_out, "alloc_loop") as (b, idx):
            out_ptr = builder.gep(arg_out, [ctx.int32_ty(0), idx])
            builder.store(val, out_ptr)
        return builder


class ControlMechanism(ModulatoryMechanism_Base):
    """
    ControlMechanism(                               \
        system=None,                                \
        monitor_for_control=None,                   \
        objective_mechanism=None,                   \
        function=Linear,                            \
        default_allocation=None,                    \
        control_signals=None,                       \
        modulation=MULTIPLICATIVE,                  \
        combine_costs=np.sum,                       \
        compute_reconfiguration_cost=None,          \
        compute_net_outcome=lambda x,y:x-y,         \
        params=None,                                \
        name=None,                                  \
        prefs=None)

    Subclass of `ModulatoryMechanism <ModulatoryMechanism>` that modulates the parameter(s)
    of one or more `Component(s) <Component>`.


    COMMENT:
    .. note::
       ControlMechanism is an abstract class and should NEVER be instantiated by a direct call to its constructor.
       It should be instantiated using the constructor for a `subclass <ControlMechanism_Subtypes>`.

        Description:
            Protocol for instantiating unassigned ControlProjections (i.e., w/o a sender specified):
               If sender is not specified for a ControlProjection (e.g., in a parameter specification tuple)
                   it is flagged for deferred_init() in its __init__ method
               If ControlMechanism is instantiated or assigned as the controller for a System:
                   the System calls its _get_monitored_output_states() method which returns all of the OutputStates
                       within the System that have been specified to be MONITORED_FOR_CONTROL, and then assigns
                       them (along with any specified in the **monitored_for_control** arg of the System's constructor)
                       to the `objective_mechanism` argument of the ControlMechanism's constructor;
                   the System calls its _get_control_signals_for_system() method which returns all of the parameters
                       that have been specified for control within the System, assigns them a ControlSignal
                       (with a ControlProjection to the ParameterState for the parameter), and assigns the
                       ControlSignals (alogn with any specified in the **control_signals** argument of the System's
                       constructor) to the **control_signals** argument of the ControlMechanism's constructor

            OBJECTIVE_MECHANISM param determines which States will be monitored.
                specifies the OutputStates of the terminal Mechanisms in the System to be monitored by ControlMechanism
                this specification overrides any in System.params[], but can be overridden by Mechanism.params[]
                ?? if MonitoredOutputStates appears alone, it will be used to determine how States are assigned from
                    System.execution_graph by default
                if MonitoredOutputStatesOption is used, it applies to any Mechanisms specified in the list for which
                    no OutputStates are listed; it is overridden for any Mechanism for which OutputStates are
                    explicitly listed
                TBI: if it appears in a tuple with a Mechanism, or in the Mechamism's params list, it applies to
                    just that Mechanism

        Class attributes:
            + componentType (str): System Default Mechanism
            + paramClassDefaults (dict):
                + FUNCTION: Linear
                + FUNCTION_PARAMS:{SLOPE:1, INTERCEPT:0}
                + OBJECTIVE_MECHANISM: List[]
    COMMENT

    Arguments
    ---------

    system : System or bool : default None
        specifies the `System` to which the ControlMechanism should be assigned as its `controller
        <System.controller>`.

    monitor_for_control : List[OutputState or Mechanism] : default None
        specifies the `OutputStates <OutputState>` to be monitored by the `ObjectiveMechanism`, if specified in the
        **objective_mechanism** argument (see `ControlMechanism_ObjectiveMechanism`), or directly by the
        ControlMechanism itself if an **objective_mechanism** is not specified.  If any specification is a Mechanism
        (rather than its OutputState), its `primary OutputState <OutputState_Primary>` is used (see
        `ControlMechanism_Monitor_for_Control` for additional details).

    objective_mechanism : ObjectiveMechanism or List[OutputState specification] : default None
        specifies either an `ObjectiveMechanism` to use for the ControlMechanism, or a list of the OutputStates it
        should monitor; if a list of `OutputState specifications <ObjectiveMechanism_Monitor>` is used,
        a default ObjectiveMechanism is created and the list is passed to its **monitor** argument, along with any
        OutputStates specified in the ControlMechanism's **monitor_for_control** `argument
        <ControlMechanism_Monitor_for_Control_Argument>`.

    function : TransferFunction : default Linear(slope=1, intercept=0)
        specifies function used to combine values of monitored OutputStates.

    default_allocation : number, list or 1d array : None
        specifies the default_allocation of any `control_signals <ControlMechanism.control.signals>` for
        which the **default_allocation** was not specified in its constructor (see default_allocation
        <ControlMechanism.default_allocation>` for additional details).

    control_signals : ControlSignal specification or List[ControlSignal specification, ...]
        specifies the parameters to be controlled by the ControlMechanism; a `ControlSignal` is created for each
        (see `ControlSignal_Specification` for details of specification).

    modulation : ModulationParam : MULTIPLICATIVE
        specifies the default form of modulation used by the ControlMechanism's `ControlSignals <ControlSignal>`,
        unless they are `individually specified <ControlSignal_Specification>`.

    combine_costs : Function, function or method : default np.sum
        specifies function used to combine the `cost <ControlSignal.cost>` of the ControlMechanism's `control_signals
        <ControlMechanism.control_signals>`;  must take a list or 1d array of scalar values as its argument and
        return a list or array with a single scalar value.

    compute_reconfiguration_cost : Function, function or method : default None
        specifies function used to compute the ControlMechanism's `reconfiguration_cost
        <ControlMechanism.reconfiguration_cost>`; must take a list or 2d array containing two lists or 1d arrays,
        both with the same shape as the ControlMechanism's control_allocation attribute, and return a scalar value.

    compute_net_outcome : Function, function or method : default lambda outcome, cost: outcome-cost
        function used to combine the values of its `outcome <ControlMechanism.outcome>` and `costs
        <ControlMechanism.costs>` attributes;  must take two 1d arrays (outcome and cost) with scalar values as its
        arguments and return an array with a single scalar value.

    params : Dict[param keyword: param value] : default None
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters
        for the Mechanism, parameters for its function, and/or a custom function and its parameters. Values
        specified for parameters in the dictionary override any assigned to those parameters in arguments of the
        constructor.

    name : str : default see `name <ControlMechanism.name>`
        specifies the name of the ControlMechanism.

    prefs : PreferenceSet or specification dict : default Mechanism.classPreferences
        specifies the `PreferenceSet` for the ControlMechanism; see `prefs <ControlMechanism.prefs>` for details.

    Attributes
    ----------

    system : System_Base
        The `System` for which the ControlMechanism is a `controller <System>`.  Note that this is distinct from
        a Mechanism's `systems <Mechanism_Base.systems>` attribute, which lists all of the Systems to which a
        `Mechanism` belongs -- a ControlMechanism can belong to but not be the `controller of a System
        <ControlMechanism_Composition_Controller>`.

    objective_mechanism : ObjectiveMechanism
        `ObjectiveMechanism` that monitors and evaluates the values specified in the ControlMechanism's
        **objective_mechanism** argument, and transmits the result to the ControlMechanism's *OUTCOME*
        `input_state <Mechanism_Base.input_state>`.

    monitor_for_control : List[OutputState]
        each item is an `OutputState` monitored by the ControlMechanism or its `objective_mechanism
        <ControlMechanism.objective_mechanism>` if that is specified (see `ControlMechanism_Monitor_for_Control`);
        in the latter case, the list returned is ObjectiveMechanism's `monitor <ObjectiveMechanism.monitor>` attribute.

    monitored_output_states_weights_and_exponents : List[Tuple(float, float)]
        each tuple in the list contains the weight and exponent associated with a corresponding OutputState specified
        in `monitor_for_control <ControlMechanism.monitor_for_control>`; if `objective_mechanism
        <ControlMechanism.objective_mechanism>` is specified, these are the same as those in the ObjectiveMechanism's
        `monitored_output_states_weights_and_exponents
        <ObjectiveMechanism.monitored_output_states_weights_and_exponents>` attribute, and are used by the
        ObjectiveMechanism's `function <ObjectiveMechanism.function>` to parametrize the contribution made to its
        output by each of the values that it monitors (see `ObjectiveMechanism Function <ObjectiveMechanism_Function>`).

    input_state : InputState
        the ControlMechanism's `primary InputState <InputState_Primary>`, named *OUTCOME*;  this receives a
        `MappingProjection` from the *OUTCOME* `OutputState <ObjectiveMechanism_Output>` of `objective_mechanism
        <ControlMechanism.objective_mechanism>` if that is specified; otherwise, it receives MappingProjections
        from each of the OutputStates specifed in `monitor_for_control <ControlMechanism.monitor_for_control>`
        (see `_ControlMechanism_Input` for additional details).

    outcome : 1d array
        the `value <InputState.value>` of the ControlMechanism's *OUTCOME* `input_state <ControlMechanism.input_state>`.

    function : TransferFunction : default Linear(slope=1, intercept=0)
        determines how the `value <OuputState.value>` \\s of the `OutputStates <OutputState>` specified in the
        **monitor_for_control** `argument <ControlMechanism_Monitor_for_Control_Argument>` of the ControlMechanism's
        constructor are used to generate its `control_allocation <ControlMechanism.control_allocation>`.

    default_allocation : number, list or 1d array
        determines the default_allocation of any `control_signals <ControlMechanism.control.signals>` for
        which the **default_allocation** was not specified in its constructor;  if it is None (not specified)
        then the ControlSignal's parameters.allocation.default_value is used. See documentation for
        **default_allocation** argument of ControlSignal constructor for additional details.

    control_allocation : 2d array
        each item is the value assigned as the `allocation <ControlSignal.allocation>` for the corresponding
        ControlSignal listed in the `control_signals` attribute;  the control_allocation is the same as the
        ControlMechanism's `value <Mechanism_Base.value>` attribute).

    control_signals : ContentAddressableList[ControlSignal]
        list of the `ControlSignals <ControlSignals>` for the ControlMechanism, including any inherited from a
        `Composition` for which it is a `controller <Composition.controller>` (same as ControlMechanism's
        `output_states <Mechanism_Base.output_states>` attribute); each sends a `ControlProjection`
        to the `ParameterState` for the parameter it controls

    compute_reconfiguration_cost : Function, function or method
        function used to compute the ControlMechanism's `reconfiguration_cost  <ControlMechanism.reconfiguration_cost>`;
        result is a scalar value representing the difference — defined by the function — between the values of the
        ControlMechanism's current and last `control_alloction <ControlMechanism.control_allocation>`, that can be
        accessed by `reconfiguration_cost <ControlMechanism.reconfiguration_cost>` attribute.

    reconfiguration_cost : scalar
        result of `compute_reconfiguration_cost <ControlMechanism.compute_reconfiguration_cost>` function, that
        computes the difference between the values of the ControlMechanism's current and last `control_alloction
        <ControlMechanism.control_allocation>`; value is None and is ignored if `compute_reconfiguration_cost
        <ControlMechanism.compute_reconfiguration_cost>` has not been specified.

        .. note::
        A ControlMechanism's reconfiguration_cost is not the same as the `adjustment_cost
        <ControlSignal.adjustment_cost>` of its ControlSignals (see `Reconfiguration Cost
        <ControlMechanism_Reconfiguration_Cost>` for additional details).

    costs : list
        current costs for the ControlMechanism's `control_signals <ControlMechanism.control_signals>`, computed
        for each using its `compute_costs <ControlSignals.compute_costs>` method.

    combine_costs : Function, function or method
        function used to combine the `cost <ControlSignal.cost>` of its `control_signals
        <ControlMechanism.control_signals>`; result is an array with a scalar value that can be accessed by
        `combined_costs <ControlMechanism.combined_costs>`.

        .. note::
          This function is distinct from the `combine_costs_function <ControlSignal.combine_costs_function>` of a
          `ControlSignal`.  The latter combines the different `costs <ControlSignal_Costs>` for an individual
          ControlSignal to yield its overall `cost <ControlSignal.cost>`; the ControlMechanism's
          `combine_costs <ControlMechanism.combine_costs>` function combines those `cost <ControlSignal.cost>`\\s
          for its `control_signals <ControlMechanism.control_signals>`.

    combined_costs : 1d array
        result of the ControlMechanism's `combine_costs <ControlMechanism.combine_costs>` function.

    compute_net_outcome : Function, function or method
        function used to combine the values of its `outcome <ControlMechanism.outcome>` and `costs
        <ControlMechanism.costs>` attributes;  result is an array with a scalar value that can be accessed
        by the the `net_outcome <ControlMechanism.net_outcome>` attribute.

    net_outcome : 1d array
        result of the ControlMechanism's `compute_net_outcome <ControlMechanism.compute_net_outcome>` function.

    control_projections : List[ControlProjection]
        list of `ControlProjections <ControlProjection>`, one for each `ControlSignal` in `control_signals`.

    modulation : ModulationParam
        the default form of modulation used by the ControlMechanism's `ControlSignals <GatingSignal>`,
        unless they are `individually specified <ControlSignal_Specification>`.

    name : str
        the name of the ControlMechanism; if it is not specified in the **name** argument of the constructor, a
        default is assigned by MechanismRegistry (see `Naming` for conventions used for default and duplicate names).

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the ControlMechanism; if it is not specified in the **prefs** argument of the
        constructor, a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet
        <LINK>` for details).
    """

    componentType = "ControlMechanism"

    initMethod = INIT_EXECUTE_METHOD_ONLY

    outputStateTypes = ControlSignal
    stateListAttr = Mechanism_Base.stateListAttr.copy()
    stateListAttr.update({ControlSignal:CONTROL_SIGNALS})

    classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TYPE_DEFAULT_PREFERENCES
    # Note: only need to specify setting;  level will be assigned to TYPE automatically
    # classPreferences = {
    #     PREFERENCE_SET_NAME: 'ControlMechanismClassPreferences',
    #     PREFERENCE_KEYWORD<pref>: <setting>...}

    class Parameters(ModulatoryMechanism_Base.Parameters):
        """
            Attributes
            ----------

                variable
                    see `variable <ControlMechanism.variable>`

                    :default value: numpy.array([[1.]])
                    :type: numpy.ndarray

                value
                    see `value <ControlMechanism.value>`

                    :default value: numpy.array([[1.]])
                    :type: numpy.ndarray

                combine_costs
                    see `combine_costs <ControlMechanism.combine_costs>`

                    :default value: numpy.core.fromnumeric.sum
                    :type: <class 'function'>

                compute_net_outcome
                    see `compute_net_outcome <ControlMechanism.compute_net_outcome>`

                    :default value: lambda outcome, cost: outcome - cost
                    :type: <class 'function'>

                compute_reconfiguration_cost
                    see `compute_reconfiguration_cost <ControlMechanism.compute_reconfiguration_cost>`

                    :default value: None
                    :type:

                control_allocation
                    see `control_allocation <ControlMechanism.control_allocation>`

                    :default value: numpy.array([1.])
                    :type: numpy.ndarray
                    :read only: True

                control_signal_costs
                    see `control_signal_costs <ControlMechanism.control_signal_costs>`

                    :default value: None
                    :type:
                    :read only: True

                costs
                    see `costs <ControlMechanism.costs>`

                    :default value: None
                    :type:
                    :read only: True

                default_allocation
                    see `default_allocation <ControlMechanism.default_allocation>`

                    :default value: (None,)
                    :type: <class 'tuple'>

                gating_allocation
                    see `gating_allocation <ControlMechanism.gating_allocation>`

                    :default value: numpy.array([0.5])
                    :type: numpy.ndarray
                    :read only: True

                modulation
                    see `modulation <ControlMechanism.modulation>`

                    :default value: MULTIPLICATIVE
                    :type: `ModulationParam`

                net_outcome
                    see `net_outcome <ControlMechanism.net_outcome>`

                    :default value: None
                    :type:
                    :read only: True

                outcome
                    see `outcome <ControlMechanism.outcome>`

                    :default value: None
                    :type:
                    :read only: True

                reconfiguration_cost
                    see `reconfiguration_cost <ControlMechanism.reconfiguration_cost>`

                    :default value: None
                    :type:
                    :read only: True

        """
        # This must be a list, as there may be more than one (e.g., one per control_signal)
        variable = np.array([[defaultControlAllocation]])
        value = Parameter(np.array([[defaultControlAllocation]]), aliases='control_allocation')
        default_allocation = None,

        combine_costs = Parameter(np.sum, stateful=False, loggable=False)
        costs = Parameter(None, read_only=True, getter=_control_mechanism_costs_getter)
        control_signal_costs = Parameter(None, read_only=True)
        compute_reconfiguration_cost = Parameter(None, stateful=False, loggable=False)
        reconfiguration_cost = Parameter(None, read_only=True)
        outcome = Parameter(None, read_only=True, getter=_outcome_getter)
        compute_net_outcome = Parameter(lambda outcome, cost: outcome - cost, stateful=False, loggable=False)
        net_outcome = Parameter(None, read_only=True,
                                getter=_net_outcome_getter)
        simulation_ids = Parameter([], user=False)
        modulation = MULTIPLICATIVE

        objective_mechanism = Parameter(None, stateful=False, loggable=False)

    paramClassDefaults = Mechanism_Base.paramClassDefaults.copy()
    paramClassDefaults.update({
        OBJECTIVE_MECHANISM: None,
        CONTROL_PROJECTIONS: None})

    @tc.typecheck
    def __init__(self,
                 default_variable=None,
                 size=None,
                 system:tc.optional(tc.any(System_Base, Composition_Base))=None,
                 monitor_for_control:tc.optional(tc.any(is_iterable, Mechanism, OutputState))=None,
                 objective_mechanism=None,
                 function=None,
                 default_allocation:tc.optional(tc.any(int, float, list, np.ndarray))=None,
                 control:tc.optional(tc.any(is_iterable,
                                            ParameterState,
                                            InputState,
                                            OutputState,
                                            ControlSignal))=None,
                 modulation:tc.optional(str)=MULTIPLICATIVE,
                 combine_costs:is_function_type=np.sum,
                 compute_reconfiguration_cost:tc.optional(is_function_type)=None,
                 compute_net_outcome:is_function_type=lambda outcome, cost : outcome - cost,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 **kwargs
                 ):

        monitor_for_control = convert_to_list(monitor_for_control) or []
        control = convert_to_list(control) or []

        # For backward compatibility:
        if kwargs:
            if MONITOR_FOR_MODULATION in kwargs:
                args = kwargs.pop(MONITOR_FOR_MODULATION)
                if args:
                    monitor_for_control.extend(convert_to_list(args))
            if MODULATORY_SIGNALS in kwargs:
                args = kwargs.pop(MODULATORY_SIGNALS)
                if args:
                    control.extend(convert_to_list(args))
            if CONTROL_SIGNALS in kwargs:
                args = kwargs.pop(CONTROL_SIGNALS)
                if args:
                    control.extend(convert_to_list(args))

        function = function or DefaultAllocationFunction
        self.combine_costs = combine_costs
        self.compute_net_outcome = compute_net_outcome
        self.compute_reconfiguration_cost = compute_reconfiguration_cost

        # Assign args to params and functionParams dicts
        params = self._assign_args_to_param_dicts(system=system,
                                                  monitor_for_control=monitor_for_control,
                                                  objective_mechanism=objective_mechanism,
                                                  function=function,
                                                  default_allocation=default_allocation,
                                                  control=control,
                                                  modulation=modulation,
                                                  params=params)
        self._sim_counts = {}

        super(ControlMechanism, self).__init__(default_variable=default_variable,
                                                  size=size,
                                                  modulation=modulation,
                                                  params=params,
                                                  name=name,
                                                  function=function,
                                                  prefs=prefs,
                                                  **kwargs)

        if system is not None:
            self._activate_projections_for_compositions(system)

    def _validate_params(self, request_set, target_set=None, context=None):
        """Validate SYSTEM, monitor_for_control, CONTROL_SIGNALS and GATING_SIGNALS

        If System is specified, validate it
        Check that all items in monitor_for_control are Mechanisms or OutputStates for Mechanisms in self.system
        Check that all items in CONTROL_SIGNALS are parameters or ParameterStates for Mechanisms in self.system
        Check that all items in GATING_SIGNALS are States for Mechanisms in self.system
        """
        from psyneulink.core.components.system import MonitoredOutputStateTuple
        from psyneulink.core.components.mechanisms.processing.objectivemechanism import ObjectiveMechanism
        from psyneulink.core.components.states.inputstate import InputState

        super(ControlMechanism, self)._validate_params(request_set=request_set,
                                                       target_set=target_set,
                                                       context=context)

        def validate_monitored_state_spec(spec_list):
            for spec in spec_list:
                if isinstance(spec, MonitoredOutputStateTuple):
                    spec = spec.output_state
                elif isinstance(spec, tuple):
                    spec = spec[0]
                elif isinstance(spec, dict):
                    # If it is a dict, parse to validate that it is an InputState specification dict
                    #    (for InputState of ObjectiveMechanism to be assigned to the monitored_output_state)
                    spec = _parse_state_spec(owner=self,
                                             state_type=InputState,
                                             state_spec=spec,
                                             context=context)
                    # Get the OutputState, to validate that it is in the ControlMechanism's Composition (below);
                    #    presumes that the monitored_output_state is the first in the list of projection_specs
                    #    in the InputState state specification dictionary returned from the parse,
                    #    and that it is specified as a projection_spec (parsed into that in the call
                    #    to _parse_connection_specs by _parse_state_spec)

                    spec = spec[PROJECTIONS][0][0]

                if not isinstance(spec, (OutputState, Mechanism)):
                    if isinstance(spec, type) and issubclass(spec, Mechanism):
                        raise ControlMechanismError(
                                f"Mechanism class ({spec.__name__}) specified in '{MONITOR_FOR_CONTROL}' arg "
                                f"of {self.name}; it must be an instantiated {Mechanism.__name__} or "
                                f"{OutputState.__name__} of one.")
                    elif isinstance(spec, State):
                        raise ControlMechanismError(
                                f"{spec.__class__.__name__} specified in '{MONITOR_FOR_CONTROL}' arg of {self.name} "
                                f"({spec.name} of {spec.owner.name}); "
                                f"it must be an {OutputState.__name__} or {Mechanism.__name__}.")
                    else:
                        raise ControlMechanismError(
                                f"Erroneous specification of '{MONITOR_FOR_CONTROL}' arg for {self.name} ({spec}); "
                                f"it must be an {OutputState.__name__} or a {Mechanism.__name__}.")
                # If ControlMechanism has been assigned to a System, check that
                #    all the items in the list used to specify objective_mechanism are in the same System
                # FIX: TBI FOR COMPOSITION
                if self.system:
                    if not isinstance(spec, (list, ContentAddressableList)):
                        spec = [spec]
                    self.system._validate_monitored_states_in_system(spec, context=context)

        if SYSTEM in target_set:
            if not isinstance(target_set[SYSTEM], System_Base):
                raise KeyError
            else:
                self.paramClassDefaults[SYSTEM] = request_set[SYSTEM]

        if MONITOR_FOR_CONTROL in target_set and target_set[MONITOR_FOR_CONTROL] is not None:
            spec = target_set[MONITOR_FOR_CONTROL]
            if not isinstance(spec, (list, ContentAddressableList)):
                spec = [spec]
            validate_monitored_state_spec(spec)

        if OBJECTIVE_MECHANISM in target_set and \
                target_set[OBJECTIVE_MECHANISM] is not None and\
                target_set[OBJECTIVE_MECHANISM] is not False:

            if isinstance(target_set[OBJECTIVE_MECHANISM], list):

                obj_mech_spec_list = target_set[OBJECTIVE_MECHANISM]

                # Check if there is any ObjectiveMechanism is in the list;
                #    incorrect but possibly forgivable mis-specification --
                #    if an ObjectiveMechanism is specified, it should be "exposed" (i.e., not in a list)
                if any(isinstance(spec, ObjectiveMechanism) for spec in obj_mech_spec_list):
                    # If an ObjectiveMechanism is the *only* item in the list, forgive the mis-spsecification and use it
                    if len(obj_mech_spec_list)==1 and isinstance(obj_mech_spec_list[0], ObjectiveMechanism):
                        if self.verbosePref:
                            warnings.warn("Specification of {} arg for {} is an {} in a list; it will be used, "
                                                        "but, for future reference, it should not be in a list".
                                                        format(OBJECTIVE_MECHANISM,
                                                               ObjectiveMechanism.__name__,
                                                               self.name))
                        target_set[OBJECTIVE_MECHANISM] = target_set[OBJECTIVE_MECHANISM][0]
                    else:
                        raise ControlMechanismError("Ambigusous specification of {} arg for {}; "
                                                    " it is in a list with other items ({})".
                                                    format(OBJECTIVE_MECHANISM, self.name, obj_mech_spec_list))
                else:
                    validate_monitored_state_spec(obj_mech_spec_list)

            if not isinstance(target_set[OBJECTIVE_MECHANISM], (ObjectiveMechanism, list, bool)):
                raise ControlMechanismError("Specification of {} arg for {} ({}) must be an {}"
                                            "or a list of Mechanisms and/or OutputStates to be monitored for control".
                                            format(OBJECTIVE_MECHANISM,
                                                   self.name, target_set[OBJECTIVE_MECHANISM],
                                                   ObjectiveMechanism.componentName))

        if CONTROL in target_set and target_set[CONTROL]:
            control = target_set[CONTROL]
            assert isinstance(control, list), \
                f"PROGRAM ERROR: control arg {control} of {self.name} should have been converted to a list."
            # # MODIFIED 9/26/19 OLD:
            # from psyneulink.core.components.projections.projection import ProjectionError
            # for ctl_spec in control:
            #     # _parse_state_spec(state_type=ControlSignal, owner=self, state_spec=control_signal)
            #     try:
            #         _parse_state_spec(state_type=ControlSignal, owner=self, state_spec=ctl_spec)
            #     except ProjectionError:
            #         _parse_state_spec(state_type=GatingSignal, owner=self, state_spec=ctl_spec)
            # MODIFIED 9/26/19 NEW:
            for ctl_spec in control:
                ctl_spec = _parse_state_spec(state_type=ControlSignal, owner=self, state_spec=ctl_spec)
                if not (isinstance(ctl_spec, ControlSignal)
                        or (isinstance(ctl_spec, dict) and ctl_spec[STATE_TYPE]==ControlSignal.__name__)):
                    raise ControlMechanismError(f"Invalid specification for '{CONTROL}' argument of {self.name}:"
                                                f"({ctl_spec})")
            # MODIFIED 9/26/19 END

    # IMPLEMENTATION NOTE:  THIS SHOULD BE MOVED TO COMPOSITION ONCE THAT IS IMPLEMENTED
    def _instantiate_objective_mechanism(self, context=None):
        """
        # FIX: ??THIS SHOULD BE IN OR MOVED TO ObjectiveMechanism
        Assign InputState to ObjectiveMechanism for each OutputState to be monitored;
            uses _instantiate_monitoring_input_state and _instantiate_control_mechanism_input_state to do so.
            For each item in self.monitored_output_states:
            - if it is a OutputState, call _instantiate_monitoring_input_state()
            - if it is a Mechanism, call _instantiate_monitoring_input_state for relevant Mechanism.output_states
                (determined by whether it is a `TERMINAL` Mechanism and/or MonitoredOutputStatesOption specification)
            - each InputState is assigned a name with the following format:
                '<name of Mechanism that owns the monitoredOutputState>_<name of monitoredOutputState>_Monitor'

        Notes:
        * self.monitored_output_states is a list, each item of which is a Mechanism.output_state from which a
          Projection will be instantiated to a corresponding InputState of the ControlMechanism
        * self.input_states is the usual ordered dict of states,
            each of which receives a Projection from a corresponding OutputState in self.monitored_output_states
        """
        from psyneulink.core.components.system import MonitoredOutputStateTuple
        from psyneulink.core.components.projections.pathway.mappingprojection import MappingProjection
        from psyneulink.core.components.mechanisms.processing.objectivemechanism import ObjectiveMechanism, ObjectiveMechanismError
        from psyneulink.core.components.states.inputstate import EXPONENT_INDEX, WEIGHT_INDEX
        from psyneulink.core.components.functions.function import FunctionError

        # GET OutputStates to Monitor (to specify as or add to ObjectiveMechanism's monitored_output_states attribute

        monitored_output_states = []

        # If the ControlMechanism has already been assigned to a System
        #    get OutputStates in System specified as monitor_for_control or already being monitored:
        #        do this by calling _get_monitored_output_states_for_system(),
        #        which also gets any OutputStates already being monitored by the ControlMechanism
        if self.system:
            monitored_output_states.extend(self.system._get_monitored_output_states_for_system(self,context=context))

        self.monitor_for_control = self.monitor_for_control or []
        if not isinstance(self.monitor_for_control, list):
            self.monitor_for_control = [self.monitor_for_control]

        # If objective_mechanism is used to specify OutputStates to be monitored (legacy feature)
        #    move them to monitor_for_control
        if isinstance(self.objective_mechanism, list):
            self.monitor_for_control.extend(self.objective_mechanism)

        # Add items in monitor_for_control to monitored_output_states
        for i, item in enumerate(self.monitor_for_control):
            # If it is already in the list received from System, ignore
            if item in monitored_output_states:
                # NOTE: this can happen if ControlMechanisms is being constructed by System
                #       which passed its monitor_for_control specification
                continue
            monitored_output_states.extend([item])

        # INSTANTIATE ObjectiveMechanism

        # If *objective_mechanism* argument is an ObjectiveMechanism, add monitored_output_states to it
        if isinstance(self.objective_mechanism, ObjectiveMechanism):
            if monitored_output_states:
                self.objective_mechanism.add_to_monitor(monitor_specs=monitored_output_states,
                                                        context=context)
        # Otherwise, instantiate ObjectiveMechanism with list of states in monitored_output_states
        else:
            try:
                self.objective_mechanism = ObjectiveMechanism(monitor=monitored_output_states,
                                                               function=LinearCombination(operation=PRODUCT),
                                                               name=self.name + '_ObjectiveMechanism')
            except (ObjectiveMechanismError, FunctionError) as e:
                raise ObjectiveMechanismError(f"Error creating {OBJECTIVE_MECHANISM} for {self.name}: {e}")

        # Print monitored_output_states
        if self.prefs.verbosePref:
            print("{0} monitoring:".format(self.name))
            for state in self.monitored_output_states:
                weight = self.monitored_output_states_weights_and_exponents[
                                                         self.monitored_output_states.index(state)][WEIGHT_INDEX]
                exponent = self.monitored_output_states_weights_and_exponents[
                                                         self.monitored_output_states.index(state)][EXPONENT_INDEX]
                print(f"\t{weight} (exp: {weight}; wt: {exponent})")

        # Assign ObjectiveMechanism's role as CONTROL
        self.objective_mechanism._role = CONTROL

        # Instantiate MappingProjection from ObjectiveMechanism to ControlMechanism
        projection_from_objective = MappingProjection(sender=self.objective_mechanism,
                                                      receiver=self,
                                                      matrix=AUTO_ASSIGN_MATRIX,
                                                      context=context)

        # CONFIGURE FOR ASSIGNMENT TO COMPOSITION

        # Insure that ObjectiveMechanism's input_states are not assigned projections from a Composition's input_CIM
        for input_state in self.objective_mechanism.input_states:
            input_state.internal_only = True
        # Flag ObjectiveMechanism and its Projection to ControlMechanism for inclusion in Composition
        self.aux_components.append(self.objective_mechanism)
        self.aux_components.append(projection_from_objective)

        # ASSIGN ATTRIBUTES

        self._objective_projection = projection_from_objective
        self.monitor_for_control = self.monitored_output_states

    def _instantiate_input_states(self, context=None):

        super()._instantiate_input_states(context=context)
        self.input_state.name = OUTCOME
        self.input_state.name = OUTCOME

        # If objective_mechanism is specified, instantiate it,
        #     including Projections to it from monitor_for_control
        if self.objective_mechanism:
            self._instantiate_objective_mechanism(context=context)

        # Otherwise, instantiate Projections from monitor_for_control to ControlMechanism
        elif self.monitor_for_control:
            from psyneulink.core.components.projections.pathway.mappingprojection import MappingProjection
            for sender in convert_to_list(self.monitor_for_control):
                self.aux_components.append(MappingProjection(sender=sender, receiver=self.input_states[OUTCOME]))

    def _instantiate_output_states(self, context=None):

    # ---------------------------------------------------
    # FIX 5/23/17: PROJECTIONS AND PARAMS SHOULD BE PASSED BY ASSIGNING TO STATE SPECIFICATION DICT
    # FIX          UPDATE parse_state_spec TO ACCOMODATE (param, ControlSignal) TUPLE
    # FIX          TRACK DOWN WHERE PARAMS ARE BEING HANDED OFF TO ControlProjection
    # FIX                   AND MAKE SURE THEY ARE NOW ADDED TO ControlSignal SPECIFICATION DICT
    # ---------------------------------------------------

        self._register_control_signal_type(context=None)

        if self.control:
            self._instantiate_control_signals(context=context)

        super()._instantiate_output_states(context=context)

        # # Reassign control_signals, control_signals and gating_signals to backing fields of corresponding params
        # # to capture any user_defined ControlSignals and/or GatingSignals instantiated in call to super
        # # and assign to ContentAddressableLists
        # self._control_signals = ContentAddressableList(component_type=ControlSignal,
        #                                                list=[state for state in self.output_states
        #                                                      if isinstance(state, (ControlSignal, GatingSignal))])

    def _register_control_signal_type(self, context=None):
        from psyneulink.core.globals.registry import register_category
        from psyneulink.core.components.states.state import State_Base

        # Create registry for ControlSignals (to manage names)
        register_category(entry=ControlSignal,
                          base_class=State_Base,
                          registry=self._stateRegistry,
                          context=context)

    def _instantiate_control_signals(self, context):
        """Subclassess can override for class-specific implementation (see OptimiziationControlMechanism for example)"""
        for i, control_signal in enumerate(self.control):
            self.control[i] = self._instantiate_control_signal(control_signal, context=context)
        num_control_signals = i+1

        # For DefaultAllocationFunction, set defaults.value to have number of items equal to num control_signals
        if isinstance(self.function, DefaultAllocationFunction):
            self.defaults.value = np.tile(self.function.value, (num_control_signals, 1))
            self.parameters.control_allocation._set(copy.deepcopy(self.defaults.value), context)
            self.function.num_control_signals = num_control_signals

        # For other functions, assume that if its value has:
        # - one item, all control_signals should get it (i.e., the default: (OWNER_VALUE, 0));
        # - same number of items as the number of control_signals;
        #     assign each control_signal to the corresponding item of the function's value
        # - a different number of items than number of control_signals,
        #     leave things alone, and allow any errant indices for control_signals to be caught later.
        else:
            self.defaults.value = np.array(self.function.value)
            self.parameters.value._set(copy.deepcopy(self.defaults.value), context)

            len_fct_value = len(self.function.value)

            # Assign each ControlSignal's variable_spec to index of ControlMechanism's value
            for i, control_signal in enumerate(self.control):

                # If number of control_signals is same as number of items in function's value,
                #    assign each ControlSignal to the corresponding item of the function's value
                if len_fct_value == num_control_signals:
                    control_signal._variable_spec = [(OWNER_VALUE, i)]

                if not isinstance(control_signal.owner_value_index, int):
                    assert False, \
                        f"PROGRAM ERROR: The \'owner_value_index\' attribute for {control_signal.name} " \
                            f"of {self.name} ({control_signal.owner_value_index})is not an int."

    def _instantiate_control_signal(self,  control_signal, context=None):
        """Parse and instantiate ControlSignal (or subclass relevant to ControlMechanism subclass)

        Temporarily assign variable to default allocation value to avoid chicken-and-egg problem:
           value, output_states and control_signals haven't been expanded yet to accomodate the new
           ControlSignal; reassign control_signal.variable to actual OWNER_VALUE below,
           once value has been expanded
        """

        if self._output_states is None:
            self._output_states = []

        control_signal = self._instantiate_control_signal_type(control_signal, context)
        control_signal.owner = self

        self._check_for_duplicates(control_signal, self.control_signals, context)

        # Update control_signal_costs to accommodate instantiated Projection
        control_signal_costs = self.parameters.control_signal_costs._get(context)
        try:
            control_signal_costs = np.append(control_signal_costs, np.zeros((1, 1)), axis=0)
        except (AttributeError, ValueError):
            control_signal_costs = np.zeros((1, 1))
        self.parameters.control_signal_costs._set(control_signal_costs, context)

        # UPDATE output_states AND control_projections -------------------------------------------------------------

        # FIX: 9/14/19 - THIS SHOULD BE IMPLEMENTED
        # TBI: For ControlMechanisms that accumulate, starting output must be equal to the initial "previous value"
        # so that modulation that occurs BEFORE the control mechanism executes is computed appropriately
        # if (isinstance(self.function, IntegratorFunction)):
        #     control_signal._intensity = function.initializer

        # Add ControlSignal to end of list of ControlSignals at start of output_states list
        # FIX: 9/25/19 - PUT ALL ControlSignals AT THE BEGINNING OF THE LIST;
        #                ALLOW OTHERS OUTPUTSTATES TO BE SPECIFIED
        self._output_states.append(control_signal)

        return control_signal

    def _instantiate_control_signal_type(self, control_signal_spec, context):
        """Instantiate actual ControlSignal, or subclass if overridden"""
        from psyneulink.core.components.states.state import _instantiate_state
        from psyneulink.core.components.projections.projection import ProjectionError

        allocation_parameter_default = self.parameters.control_allocation.default_value

        control_signal = _instantiate_state(state_type=ControlSignal,
                                               owner=self,
                                               variable=self.default_allocation           # User specified value
                                                        or allocation_parameter_default,  # Parameter default
                                               reference_value=allocation_parameter_default,
                                               modulation=self.modulation,
                                               state_spec=control_signal_spec,
                                               context=context)
        if not type(control_signal) in convert_to_list(self.outputStateTypes):
            raise ProjectionError(f'{type(control_signal)} inappropriate for {self.name}')
        return control_signal

    def _check_for_duplicates(self, control_signal, control_signals, context):
        """
        Check that control_signal is not a duplicate of one already instantiated for the ControlMechanism

        Can happen if control of parameter is specified in constructor for a Mechanism
            and also in the ControlMechanism's **control** arg

        control_signals arg passed in to allow override by subclasses
        """

        for existing_ctl_sig in control_signals:
            # OK if control_signal is one already assigned to ControlMechanism (i.e., let it get processed below);
            # this can happen if it was in deferred_init status and initalized in call to _instantiate_state above.
            if control_signal == existing_ctl_sig:
                continue

            # Return if *all* projections from control_signal are identical to ones in an existing control_signal
            for proj in control_signal.efferents:
                if proj not in existing_ctl_sig.efferents:
                    # A Projection in control_signal is not in this existing one: it is different,
                    #    so break and move on to next existing_mod_sig
                    break
                return

            # Warn if *any* projections from control_signal are identical to ones in an existing control_signal
            projection_type = existing_ctl_sig.paramClassDefaults[PROJECTION_TYPE]
            if any(
                    any(new_p.receiver == existing_p.receiver
                        for existing_p in existing_ctl_sig.efferents) for new_p in control_signal.efferents):
                warnings.warn(f"Specification of {control_signal.name} for {self.name} "
                              f"has one or more {projection_type}s redundant with ones already on "
                              f"an existing {ControlSignal.__name__} ({existing_ctl_sig.name}).")

    def show(self):
        """Display the OutputStates monitored by ControlMechanism's `objective_mechanism
        <ControlMechanism.objective_mechanism>` and the parameters modulated by its `control_signals
        <ControlMechanism.control_signals>`.
        """

        print("\n---------------------------------------------------------")

        print("\n{0}".format(self.name))
        print("\n\tMonitoring the following Mechanism OutputStates:")
        for state in self.objective_mechanism.input_states:
            for projection in state.path_afferents:
                monitored_state = projection.sender
                monitored_state_mech = projection.sender.owner
                # ContentAddressableList
                monitored_state_index = self.monitored_output_states.index(monitored_state)

                weight = self.monitored_output_states_weights_and_exponents[monitored_state_index][0]
                exponent = self.monitored_output_states_weights_and_exponents[monitored_state_index][1]

                print ("\t\t{0}: {1} (exp: {2}; wt: {3})".
                       format(monitored_state_mech.name, monitored_state.name, weight, exponent))

        try:
            if self.control_signals:
                print ("\n\tControlling the following Mechanism parameters:".format(self.name))
                # Sort for consistency of output:
                state_names_sorted = sorted(self.control_signals.names)
                for state_name in state_names_sorted:
                    for projection in self.control_signals[state_name].efferents:
                        print ("\t\t{0}: {1}".format(projection.receiver.owner.name, projection.receiver.name))
        except:
            pass

        try:
            if self.gating_signals:
                print ("\n\tGating the following States:".format(self.name))
                # Sort for consistency of output:
                state_names_sorted = sorted(self.gating_signals.names)
                for state_name in state_names_sorted:
                    for projection in self.gating_signals[state_name].efferents:
                        print ("\t\t{0}: {1}".format(projection.receiver.owner.name, projection.receiver.name))
        except:
            pass

        print ("\n---------------------------------------------------------")

    def add_to_monitor(self, monitor_specs, context=None):
        """Instantiate OutputStates to be monitored by ControlMechanism's `objective_mechanism
        <ControlMechanism.objective_mechanism>`.

        **monitored_output_states** can be any of the following:
            - `Mechanism`;
            - `OutputState`;
            - `tuple specification <InputState_Tuple_Specification>`;
            - `State specification dictionary <InputState_Specification_Dictionary>`;
            - list with any of the above.
        If any item is a Mechanism, its `primary OutputState <OutputState_Primary>` is used.
        OutputStates must belong to Mechanisms in the same `System` as the ControlMechanism.
        """
        output_states = self.objective_mechanism.add_to_monitor(monitor_specs=monitor_specs, context=context)
        if self.system:
            self.system._validate_monitored_states_in_system(output_states, context=context)

    def _add_process(self, process, role:str):
        super()._add_process(process, role)
        if self.objective_mechanism:
            self.objective_mechanism._add_process(process, role)

    # FIX: TBI FOR COMPOSITION
    @tc.typecheck
    @handle_external_context()
    def assign_as_controller(self, system:System_Base, context=None):
        """Assign ControlMechanism as `controller <System.controller>` for a `System`.

        **system** must be a System for which the ControlMechanism should be assigned as the `controller
        <System.controller>`.
        If the specified System already has a `controller <System.controller>`, it will be replaced by the current
        one, and the current one will inherit any ControlSignals previously specified for the old controller or the
        System itself.
        If the current one is already the `controller <System.controller>` for another System, it will be disabled
        for that System.
        COMMENT:
            [TBI:
            The ControlMechanism's `objective_mechanism <ControlMechanism.objective_mechanism>`,
            `monitored_output_states` and `control_signal <ControlMechanism.control_signals>` attributes will also be
            updated to remove any assignments that are not part of the new System, and add any that are specified for
            the new System.]
        COMMENT

        COMMENT:
            IMPLEMENTATION NOTE:  This is handled as a method on ControlMechanism (rather than System) so that:

                                  - [TBI: if necessary, it can detach itself from a System for which it is already the
                                    `controller <System.controller>`;]

                                  - any class-specific actions that must be taken to instantiate the ControlMechanism
                                    can be handled by subclasses of ControlMechanism (e.g., an EVCControlMechanism must
                                    instantiate its Prediction Mechanisms). However, the actual assignment of the
                                    ControlMechanism the System's `controller <System.controller>` attribute must
                                    be left to the System to avoid recursion, since it is a property, the setter of
                                    which calls the current method.
        COMMENT
        """

        if context.source == ContextFlags.COMMAND_LINE:
            system.controller = self
            return

        if self.objective_mechanism is None:
            self._instantiate_objective_mechanism(context=context)

        # NEED TO BUFFER OBJECTIVE_MECHANISM AND CONTROL_SIGNAL ARGUMENTS FOR USE IN REINSTANTIATION HERE
        # DETACH AS CONTROLLER FOR ANY EXISTING SYSTEM (AND SET THAT ONE'S CONTROLLER ATTRIBUTE TO None)
        # DELETE ALL EXISTING OBJECTIVE_MECHANISM AND CONTROL_SIGNAL ASSIGNMENTS
        # REINSTANTIATE ITS OWN OBJECTIVE_MECHANISM and CONTROL_SIGNAL ARGUMENT AND THOSE OF THE SYSTEM
        # SUBCLASSES SHOULD ADD OVERRIDE FOR ANY CLASS-SPECIFIC ACTIONS (E.G., INSTANTIATING PREDICTION MECHANISMS)
        # DO *NOT* ASSIGN AS CONTROLLER FOR SYSTEM... LET THE SYSTEM HANDLE THAT
        # Assign the current System to the ControlMechanism

        # Validate that all of the ControlMechanism's monitored_output_states and controlled parameters
        #    are in the new System
        system._validate_monitored_states_in_system(self.monitored_output_states)
        system._validate_control_signals(self.control_signals)

        # Get any and all OutputStates specified in:
        # - **monitored_output_states** argument of the System's constructor
        # - in a monitor_for_control specification for individual OutputStates and/or Mechanisms
        # - already being montiored by the ControlMechanism being assigned
        monitored_output_states = list(system._get_monitored_output_states_for_system(controller=self, context=context))

        # Don't add any OutputStates that are already being monitored by the ControlMechanism's ObjectiveMechanism
        for monitored_output_state in monitored_output_states.copy():
            if monitored_output_state.output_state in self.monitored_output_states:
                monitored_output_states.remove(monitored_output_state)

        # Add all other monitored_output_states to the ControlMechanism's monitored_output_states attribute
        #    and to its ObjectiveMechanisms monitored_output_states attribute
        if monitored_output_states:
            self.add_to_monitor(monitored_output_states)

        # The system does NOT already have a controller,
        #    so assign it ControlSignals for any parameters in the System specified for control
        if system.controller is None:
            system_control_signals = system._get_control_signals_for_system(system.control_signals_arg, context=context)
        # The system DOES already have a controller,
        #    so assign it the old controller's ControlSignals
        else:
            system_control_signals = system.control_signals
            for control_signal in system_control_signals:
                control_signal.owner = None

        # Get rid of default ControlSignal if it has no ControlProjections
        if (len(self.control_signals)==1
                and self.control_signals[0].name=='ControlSignal-0'
                and not self.control_signals[0].efferents):
            # FIX: REPLACE WITH remove_states
            del self._output_states[0]
            # del self.control_signals[0]

        # Add any ControlSignals specified for System
        for control_signal_spec in system_control_signals:
            control_signal = self._instantiate_control_signal(control_signal=control_signal_spec, context=context)
            # FIX: 1/18/18 - CHECK FOR SAME NAME IN _instantiate_control_signal
            # # Don't add any that are already on the ControlMechanism
            # if control_signal.name in self.control_signals.names and (self.verbosePref or system.verbosePref):
            if ((self.verbosePref or system.verbosePref)
                    and control_signal.name in [cs.name for cs in self.control_signals]):
                warnings.warn("{} specified for {} has same name (\'{}\') "
                              "as one in controller ({}) being assigned to the {}."
                              "".format(ControlSignal.__name__, system.name,
                                        control_signal.name, self.name, system.__class__.__name__))
            self.control_signals.append(control_signal)

        # If it HAS been assigned a System, make sure it is the current one
        if self.system and not self.system is system:
            raise SystemError("The controller being assigned to {} ({}) already belongs to another System ({})".
                              format(system.name, self.name, self.system.name))

        # Assign assign the current System to the ControlMechanism's system attribute
        #    (needed for it to validate and instantiate monitored_output_states and control_signals)
        self.system = system

        # Flag ObjectiveMechanism as associated with a ControlMechanism that is a controller for the System
        self.objective_mechanism.for_controller = True

        if context.source != ContextFlags.PROPERTY:
            system._controller = self

        self._activate_projections_for_compositions(system)

    def _remove_default_control_signal(self, type:tc.enum(CONTROL_SIGNAL, GATING_SIGNAL)):
        if type == CONTROL_SIGNAL:
            ctl_sig_attribute = self.control_signals
        elif type == GATING_SIGNAL:
            ctl_sig_attribute = self.gating_signals
        else:
            assert False, \
                f"PROGRAM ERROR:  bad 'type' arg ({type})passed to " \
                    f"{ControlMechanism.__name__}._remove_default_control_signal" \
                    f"(should have been caught by typecheck"

        if (len(ctl_sig_attribute)==1
                and ctl_sig_attribute[0].name==type+'-0'
                and not ctl_sig_attribute[0].efferents):
            self.remove_states(ctl_sig_attribute[0])

    def _activate_projections_for_compositions(self, composition=None):
        """Activate eligible Projections to or from nodes in Composition.
        If Projection is to or from a node NOT (yet) in the Composition,
        assign it the node's aux_components attribute but do not activate it.
        """
        dependent_projections = set()

        if self.objective_mechanism:
            # Safe to add this, as it is already in the ControlMechanism's aux_components
            #    and will therefore be added to the Composition along with the ControlMechanism
            assert self.objective_mechanism in self.aux_components, \
                f"PROGRAM ERROR:  {OBJECTIVE_MECHANISM} for {self.name} not listed in its 'aux_components' attribute."
            dependent_projections.add(self._objective_projection)

            for aff in self.objective_mechanism.afferents:
                dependent_projections.add(aff)

        for ms in self.control_signals:
            for eff in ms.efferents:
                dependent_projections.add(eff)

        # FIX: 9/15/19 - HOW IS THIS DIFFERENT THAN objective_mechanism's AFFERENTS ABOVE?
        # assign any deferred init objective mech monitored output state projections to this system
        if self.objective_mechanism:
            for output_state in self.objective_mechanism.monitored_output_states:
                for eff in output_state.efferents:
                    dependent_projections.add(eff)

        # FIX: 9/15/19 - HOW IS THIS DIFFERENT THAN control_signal's EFFERENTS ABOVE?
        for eff in self.efferents:
            dependent_projections.add(eff)

        for proj in dependent_projections:
            proj._activate_for_compositions(composition)

    def _apply_control_allocation(self, control_allocation, runtime_params, context):
        """Update values to `control_signals <ControlMechanism.control_signals>`
        based on specified `control_allocation <ControlMechanism.control_allocation>`
        (used by controller of a Composition in simulations)
        """
        value = [np.atleast_1d(a) for a in control_allocation]
        self.parameters.value._set(value, context)
        self._update_output_states(context=context,
                                   runtime_params=runtime_params,)

    @property
    def monitored_output_states(self):
        try:
            return self.objective_mechanism.monitored_output_states
        except AttributeError:
            return None

    @monitored_output_states.setter
    def monitored_output_states(self, value):
        try:
            self.objective_mechanism._monitored_output_states = value
        except AttributeError:
            return None

    @property
    def monitored_output_states_weights_and_exponents(self):
        try:
            return self.objective_mechanism.monitored_output_states_weights_and_exponents
        except:
            return None

    @property
    def control_signals(self):
        """Get ControlSignals from OutputStates"""
        try:
            # # MODIFIED 9/25/19 OLD:
            # return ContentAddressableList(component_type=ControlSignal,
            #                               list=[state for state in self.output_states
            #                                     if isinstance(state, (ControlSignal, GatingSignal))])
            # # MODIFIED 9/25/19 NEW: [JDC]
            # return [state for state in self.output_states if isinstance(state, (ControlSignal, GatingSignal))]
            # # MODIFIED 9/25/19 NEWER: [JDC]
            # return [state for state in self.output_states if isinstance(state, ControlSignal)]
            # MODIFIED 9/26/19 NEWEST: [JDC]
            return ContentAddressableList(component_type=ControlSignal,
                                          list=[state for state in self.output_states
                                                if isinstance(state, (ControlSignal))])
            # MODIFIED 9/25/19 END
        except:
            return []

    @property
    def control_projections(self):
        try:
            return [projection for control_signal in self.control_signals for projection in control_signal.efferents]
        except:
            return None

    # # MODIFIED 9/26/19 OLD:
    # @property
    # def gating_signals(self):
    #     try:
    #         return ContentAddressableList(component_type=GatingSignal,
    #                                       list=[state for state in self.output_states
    #                                             if isinstance(state, GatingSignal)])
    #     except:
    #         return None
    #
    # @property
    # def gating_projections(self):
    #     try:
    #         return [projection for gating_signal in self.gating_signals for projection in gating_signal.efferents]
    #     except:
    #         return None
    # MODIFIED 9/26/19 END

    @property
    def _sim_count_lock(self):
        try:
            return self.__sim_count_lock
        except AttributeError:
            self.__sim_count_lock = threading.Lock()
            return self.__sim_count_lock

    def get_next_sim_id(self, context):
        with self._sim_count_lock:
            try:
                sim_num = self._sim_counts[context.execution_id]
                self._sim_counts[context.execution_id] += 1
            except KeyError:
                sim_num = 0
                self._sim_counts[context.execution_id] = 1

        return '{0}{1}-{2}'.format(context.execution_id, EID_SIMULATION, sim_num)

    @property
    def _dependent_components(self):
        return list(itertools.chain(
            super()._dependent_components,
            # [self.objective_mechanism],
            [self.objective_mechanism] if self.objective_mechanism else [],
        ))
