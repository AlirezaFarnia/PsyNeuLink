import numpy as np
import psyneulink as pnl


# here we implement a test demo as in the EVC paper example:
#in v2 we add control signals and a EVC mechanism to the model

# EVC params for Umemoto et al

w_t = 0.065
w_d = -0.065 # made negative here to match -1 values for distractor
f_t = 1
f_d = 1


# EVC params for Umemoto et al
t0 = 0.2
c = 0.19
thresh = 0.21
x_0 = 0 # starting point

#wTarget = 0.065 # I think this has to do with learning and is constant over trials in Umemoto
costParam1 = 0.35
reconfCostParam1 = 5
#rewardTaskA = 50
#rewardTaskBToA = 0.7


# Control Parameters
signalSearchRange = np.arange(0.0, 4.1, 0.2) #like in MATLAB Umemoto[0.0:0.2:4.0]# needs to be adjusted
print(signalSearchRange)

# Stimulus Mechanisms
Target_Stim = pnl.TransferMechanism(name='Target Stimulus', function=pnl.Linear)
Target_Stim.set_log_conditions('value') # Log Target_Rep

Distractor_Stim = pnl.TransferMechanism(name='Distractor Stimulus', function=pnl.Linear)
Distractor_Stim.set_log_conditions('value') # Log Target_Rep

# Processing Mechanisms (Control)
Target_Rep = pnl.TransferMechanism(name='Target Representation',
                                   function=pnl.Linear(
                                       slope=(
                                           1.0,
                                           pnl.ControlProjection(
                                               function=pnl.Linear,
                                               control_signal_params={pnl.ALLOCATION_SAMPLES: signalSearchRange}
                                           ))))

Target_Rep.set_log_conditions('value') # Log Target_Rep
Target_Rep.loggable_items

Distractor_Rep = pnl.TransferMechanism(name='Distractor Representation',
                                       function=pnl.Linear(
                                           slope=(
                                               1.0,
                                               pnl.ControlProjection(
                                                   function=pnl.Linear,
                                                   control_signal_params={pnl.ALLOCATION_SAMPLES: signalSearchRange}
                                               ))))

Distractor_Rep.set_log_conditions('value') # Log Flanker_Rep
Distractor_Rep.loggable_items
# Processing Mechanism (Automatic)

Automatic_Component = pnl.TransferMechanism(name='Automatic Component',function=pnl.Linear)
Automatic_Component.loggable_items
Automatic_Component.set_log_conditions('value')


# Decision Mechanisms
Decision = pnl.DDM(function=pnl.DriftDiffusionAnalytical(
       # drift_rate=(0.1170),
        threshold=(thresh),
        noise=(c),
        starting_point=(x_0),
        t0=t0
    ),name='Decision',
    output_states=[
        pnl.DECISION_VARIABLE,
        pnl.RESPONSE_TIME,
        pnl.PROBABILITY_UPPER_THRESHOLD,
        {
            pnl.NAME: 'OFFSET RT',
            pnl.VARIABLE: (pnl.OWNER_VALUE, 2),
            pnl.FUNCTION: pnl.Linear(0, slope=1.0, intercept=1)
        }
    ],) #drift_rate=(1.0),threshold=(0.2645),noise=(0.5),starting_point=(0), t0=0.15

# Decision.set_log_conditions('DECISION_VARIABLE')
# Decision.set_log_conditions('value')
# Decision.set_log_conditions('PROBABILITY_UPPER_THRESHOLD')
Decision.set_log_conditions('InputState-0')
# Decision.set_log_conditions('RESPONSE_TIME')

# Decision.loggable_items

# Outcome Mechanisms:
Reward = pnl.TransferMechanism(size = 1,
                               name='Reward')

# Composition
Umemoto_comp = pnl.Composition(name="Umemoto_System")



### ADD pathways
TargetControl_pathway = [Target_Stim, Target_Rep, Decision]

Umemoto_comp.add_linear_processing_pathway(pathway = TargetControl_pathway)


FlankerControl_pathway = [Distractor_Stim, Distractor_Rep, Decision]

Umemoto_comp.add_linear_processing_pathway(pathway = FlankerControl_pathway)

TargetAutomatic_pathway = [Target_Stim, Automatic_Component, Decision]

Umemoto_comp.add_linear_processing_pathway(pathway = TargetAutomatic_pathway)

FlankerAutomatic_pathway = [Distractor_Stim, Automatic_Component, Decision]

Umemoto_comp.add_linear_processing_pathway(pathway = FlankerAutomatic_pathway)


Reward_pathway = [Reward]

Umemoto_comp.add_linear_processing_pathway(pathway = Reward_pathway)

Umemoto_comp.add_c_node(Decision, required_roles=pnl.CNodeRole.TERMINAL)


### COMPOSITION

Umemoto_comp.add_model_based_optimizer(optimizer=pnl.OptimizationControlMechanism(agent_rep=Umemoto_comp, features={
            pnl.SHADOW_EXTERNAL_INPUTS: [Target_Stim, Distractor_Stim, Reward]}, feature_function=pnl.AdaptiveIntegrator(
            rate=1.0), objective_mechanism=pnl.ObjectiveMechanism(monitor_for_control=[Reward,
                                                                                       (
                                                                                       Decision.PROBABILITY_UPPER_THRESHOLD,
                                                                                       1, -1)]),
                                                                                  function=pnl.GridSearch(),
                                                                                  control_signals=[
                                                                                      ("slope", Target_Rep),
                                                                                      ("slope", Distractor_Rep)]))
Umemoto_comp.enable_model_based_optimizer = True

Umemoto_comp.model_based_optimizer.control_signals[0].intensity_cost_function = pnl.Exponential(scale=1, rate=1).function
Umemoto_comp.model_based_optimizer.control_signals[0].adjustment_cost_function = pnl.Exponential(scale=1, rate=1, offset=-1).function

Umemoto_comp.model_based_optimizer.control_signals[1].intensity_cost_function = pnl.Exponential(scale=1, rate=1).function
Umemoto_comp.model_based_optimizer.control_signals[1].adjustment_cost_function = pnl.Exponential(scale=1, rate=1, offset=-1).function


# System:
# mySystem = pnl.System(processes=[TargetControl_pathway,
#         FlankerControl_pathway,
#         TargetAutomatic_pathway,
#         FlankerAutomatic_pathway,
#          Reward_pathway],
#     controller=pnl.EVCControlMechanism( control_signals=[pnl.ControlSignal(projections=[(pnl.SLOPE, Target_Rep)
#                                                                                        ],
#
#                                                                   # function=pnl.Linear,
#                                                                   cost_options=[pnl.ControlSignalCosts.INTENSITY,
#                                                                                 pnl.ControlSignalCosts.ADJUSTMENT],
#                                                                   intensity_cost_function =pnl.Exponential(scale=1, rate=1, offset=-1),
#                                                                   adjustment_cost_function = pnl.Exponential(scale=1, rate=1, offset=-1),#pnl.Linear(slope=0, intercept=0),
#                                                                   #duration_cost_function=None,#pnl.IntegratorFunction(None),
#                                                                   #cost_combination_function=pnl.SUM(),
#                                                                   allocation_samples=signalSearchRange,
#                                                                   ),
#                                                          pnl.ControlSignal(projections=[(pnl.SLOPE, Distractor_Rep)
#                                                                                         ],
#                                                                            # function=pnl.Linear,
#                                                                            cost_options=[
#                                                                                pnl.ControlSignalCosts.INTENSITY,
#                                                                                pnl.ControlSignalCosts.ADJUSTMENT],
#                                                                            intensity_cost_function= pnl.Exponential(scale=1, rate=1),
#                                                                            adjustment_cost_function= pnl.Exponential(scale=1, rate=1, offset= -1),#pnl.Linear(slope=0, intercept=0),
#                                                                            # duration_cost_function=None,#pnl.IntegratorFunction(None),
#                                                                            # cost_combination_function=pnl.SUM(),
#                                                                            allocation_samples=signalSearchRange,
#                                                                            )
#                                                          ]),#cost_function=),         # changes by Markus September 7 2018
#     enable_controller=True,
#     monitor_for_control=[
#         # (None, None, np.ones((2,1))), # what the **** is this for? Markus October 25 2018
#         Reward,
#         Decision.PROBABILITY_UPPER_THRESHOLD,
#         ('OFFSET RT', 1, -1),
#     ],
#     name='EVC Umemoto Composition')

# log controller


# Show characteristics of system:
# mySystem.controller.show()

# Show graph of system
# mySystem.show_graph(show_control=True, show_dimensions=True)

#Markus: incongruent trial weights:

# f = np.array([1,1])
# W_inc = np.array([[1.0, 0.0],[0.0, 1.5]])
# W_con = np.array([[1.0, 0.0],[1.5, 0.0]])


# generate stimulus environment
nTrials = 3
targetFeatures = [w_t]
flankerFeatures_inc = [w_d]
reward = [100]#[100]


targetInputList = targetFeatures
flankerInputList = flankerFeatures_inc
rewardList = reward

stim_list_dict = {
    Target_Stim: targetInputList,
    Distractor_Stim: flankerInputList,
     Reward: rewardList
}
#
# def x():
#     #print(mySystem.conroller.)
#     # print(mySystem.controller.control_signals.values)
#     print("============== ")
#     print("decision input vale:", Decision.input_values)
#     print("============== ")

    # print(Decision.output_states[pnl.PROBABILITY_UPPER_THRESHOLD].value)
    # print(Decision.output_states[pnl.DECISION_VARIABLE].value)
    # print(Decision.output_states[pnl.RESPONSE_TIME].value)
    # print(Target_Rep.input_values)
    # print("target rep variable:", Target_Rep.input_states[0].variable)
    # print("target rep input states:", Target_Rep.input_states)
    # print("output target stim", Target_Stim.output_values)
    #
    # print(Target_Rep.path_afferents)
    # print("control proj sender value:", Target_Rep.mod_afferents[0].sender.value)
    #
    # # print(Target_Rep.path_afferents)
    #
    #
    # print("distractor rep input: ", Distractor_Rep.input_values)
    # print("my system controller: ", mySystem.controller.control_signals.values)
    # print("my system controller SLOPE: ", mySystem.controller.control_signals.values)
    #
    # print("input state bla bla:", Target_Rep.input_states[0].function_object.exponents)
    # print("============== ")
    # print("my system  stuff: ", mySystem.controller.control_signals.values)
    #





    # print(Target_Rep.output_values)
    # print(Automatic_Component_Target.output_values)
    #
    # print(Distractor_Rep.output_values)
    # print(Automatic_Component_Flanker.output_values)

# mySystem.controller.control_signals[0].value = 1.8
# mySystem.controller.control_signals[1].value = 0.0

Umemoto_comp.run(num_trials=nTrials,
             inputs=stim_list_dict)#,
              # call_after_trial=x)

#Distractor_Rep.log.print_entries()
#Target_Rep.log.print_entries()
#Automatic_Component.log.print_entries()

#from pprint import pprint
#a = Decision.log.nparray_dictionary()
#pprint(a)
# Target_Stim.log.print_entries()
# Distractor_Stim.log.print_entries()
# Target_Rep.log.print_entries()
# Distractor_Rep.log.print_entries()
#
# Decision.log.print_entries()
# Automatic_Component.log.print_entries()
Target_Rep.log.print_entries()
#mySystem.controller.control_signals.values

