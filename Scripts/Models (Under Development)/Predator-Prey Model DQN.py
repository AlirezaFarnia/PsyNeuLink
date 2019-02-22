import timeit
import numpy as np
from psyneulink import *

from double_dqn import DoubleDQNAgent

from gym_forager.envs.forager_env import ForagerEnv

# *********************************************************************************************************************
# *********************************************** CONSTANTS ***********************************************************
# *********************************************************************************************************************

# Runtime Switches:
MPI_IMPLEMENTATION = True
RENDER = False
PNL_COMPILE = False
RUN = True
SHOW_GRAPH = False
# MODEL_PATH = '/Users/jdc/Dropbox (Princeton)/Documents (DropBox)/Python/double-dqn/models/trained_models/policy_net_trained_0.99_20190214-1651.pt'
MODEL_PATH = '../../../double-dqn/models/trained_models/policy_net_trained_0.99_20190214-1651.pt'

# These should probably be replaced by reference to ForagerEnv constants:
obs_len = 2
obs_coords = 2
action_len = 2

player_idx = 0
player_obs_start_idx = player_idx * obs_len
player_value_idx = player_idx * obs_len + obs_coords
player_coord_slice = slice(player_obs_start_idx,player_value_idx)

predator_idx = 1
predator_obs_start_idx = predator_idx * obs_len
predator_value_idx = predator_idx * obs_len + obs_coords
predator_coord_slice = slice(predator_obs_start_idx,predator_value_idx)

prey_idx = 2
prey_obs_start_idx = prey_idx * obs_len
prey_value_idx = prey_idx * obs_len + obs_coords
prey_coord_slice = slice(prey_obs_start_idx,prey_value_idx)

player_len = prey_len = predator_len = obs_coords

cost_rate = -.05
cost_bias = -1
min_alloc = 0
max_alloc = 500


# **********************************************************************************************************************
# **************************************  CREATE COMPOSITION ***********************************************************
# **********************************************************************************************************************

# ************************************** DOUBLE_DQN AGENT **************************************************************

# ddqn_agent = DoubleDQNAgent(env=env, model_load_path='', eval_mode=True)
ddqn_agent = DoubleDQNAgent(model_load_path=MODEL_PATH,
                            eval_mode=True,
                            render=False
                            )
perceptual_state = None
veridical_state = None

def new_episode():
    global perceptual_state
    global veridical_state
    observation = ddqn_agent.env.reset()
    g=GaussianDistort()
    perceptual_state = ddqn_agent.buffer.next(g(observation), is_new_episode=True)
    veridical_state = ddqn_agent.buffer.next(observation, is_new_episode=True)

def get_optimal_action(observation):
    # Get new state based on observation:
    veridical_state = ddqn_agent.buffer.next(np.array(observation))
    optimal_action = np.array(ddqn_agent._io_map(ddqn_agent._select_action(veridical_state).item()))
    return optimal_action

# **************************************  PROCESSING MECHANISMS ********************************************************

# Perceptual Mechanisms
player_percept = ProcessingMechanism(size=prey_len, function=GaussianDistort, name="PLAYER PERCEPT")
predator_percept = ProcessingMechanism(size=predator_len, function=GaussianDistort, name="PREDATOR PERCEPT")
prey_percept = ProcessingMechanism(size=prey_len, function=GaussianDistort, name="PREY PERCEPT")

optimal_action_mech = ProcessingMechanism(size=action_len, name="OPTIMAL ACTION")

def get_action(variable=[[0,0],[0,0],[0,0]]):
    global perceptual_state
    # Convert variable to observation:
    observation = np.array(list(variable[0]) + list(variable[1]) + list(variable[2]))
    # Get new state based on observation:
    perceptual_state = ddqn_agent.buffer.next(observation)
    action = np.array(ddqn_agent._io_map(ddqn_agent._select_action(perceptual_state).item()))
    return action

# Action Mechanism
#    Use ddqn's eval function to compute action for a given observation
#    note: unitization is done in main loop, to allow compilation of LinearCombination function in ObjectiveMech) (TBI)
action_mech = ProcessingMechanism(default_variable=[[0,0],[0,0],[0,0]], function=get_action, name='ACTION')

# ************************************** BASIC COMPOSITION *************************************************************

agent_comp = Composition(name='PREDATOR-PREY COMPOSITION')
# agent_comp.add_linear_processing_pathway([player_percept, action_mech.input_states[0]])
# agent_comp.add_linear_processing_pathway([predator_percept, action_mech.input_states[1]])
# agent_comp.add_linear_processing_pathway([prey_percept, action_mech.input_states[2]])

# agent_comp.add_nodes([player_percept, predator_percept, prey_percept, action_mech])
# agent_comp.add_projection(sender=player_percept, receiver=action_mech.input_states[0])
# agent_comp.add_projection(sender=predator_percept, receiver=action_mech.input_states[1])
# agent_comp.add_projection(sender=prey_percept, receiver=action_mech.input_states[2])

agent_comp.add_nodes([player_percept, predator_percept, prey_percept, optimal_action_mech])
agent_comp.add_node(action_mech, required_roles=[NodeRole.OUTPUT])

a = MappingProjection(sender=player_percept, receiver=action_mech.input_states[0])
b = MappingProjection(sender=predator_percept, receiver=action_mech.input_states[1])
c = MappingProjection(sender=prey_percept, receiver=action_mech.input_states[2])
agent_comp.add_projection(a)
agent_comp.add_projection(b)
agent_comp.add_projection(c)


# **************************************  CONOTROL APPRATUS ************************************************************

difference = Distance(metric=DIFFERENCE)
#   function for ObjectiveMechanism

def objective_function(variable):
    '''Return difference between optimal and actual actions'''
    actual_action = variable[0]
    optimal_action = variable[1]
    similarity = 1-difference([optimal_action, actual_action])/4
    return similarity

ocm = OptimizationControlMechanism(features={SHADOW_INPUTS:[player_percept, predator_percept, prey_percept]},
                                   agent_rep=agent_comp, # Use Composition itself (i.e., fully "model-based" evaluation)
                                   function=GridSearch(direction=MAXIMIZE, save_values=True),
                                   objective_mechanism=ObjectiveMechanism(function=objective_function,
                                                                          monitor=[action_mech, optimal_action_mech]),
                                   control_signals=[ControlSignal(projections=(VARIANCE,player_percept),
                                                                  allocation_samples=[min_alloc, max_alloc],
                                                                  intensity_cost_function=Exponential(rate=cost_rate,
                                                                                                      bias=cost_bias)),
                                                    ControlSignal(projections=(VARIANCE,predator_percept),
                                                                  allocation_samples=[min_alloc, max_alloc],
                                                                  intensity_cost_function=Exponential(rate=cost_rate,
                                                                                                      bias=cost_bias)),
                                                    ControlSignal(projections=(VARIANCE,prey_percept),
                                                                  allocation_samples=[min_alloc, max_alloc],
                                                                  intensity_cost_function=Exponential(rate=cost_rate,
                                                                                                      bias=cost_bias))])
# Add controller to Composition
agent_comp.add_model_based_optimizer(ocm)
agent_comp.enable_model_based_optimizer = True

if SHOW_GRAPH:
    # agent_comp.show_graph(show_mechanism_structure='ALL')
    agent_comp.show_graph(show_control=True)


# *********************************************************************************************************************
# ******************************************   RUN SIMULATION  ********************************************************
# *********************************************************************************************************************

num_episodes = 1

def main():
    reward = 0
    done = False
    if RENDER:
        ddqn_agent.env.render()  # If visualization is desired
    else:
        print("Running simulation...")
    steps = 0
    start_time = timeit.default_timer()
    new_episode()
    for _ in range(num_episodes):
        observation = ddqn_agent.env.reset()
        optimal_action=[0,0]
        while True:
            execution_id = 'TEST'
            if PNL_COMPILE:
                BIN_EXECUTE = 'LLVM'
            else:
                BIN_EXECUTE = 'Python'
            optimal_action = get_optimal_action(observation)
            run_results = agent_comp.run(inputs={player_percept:[observation[player_coord_slice]],
                                                 predator_percept:[observation[predator_coord_slice]],
                                                 prey_percept:[observation[prey_coord_slice]],
                                                 optimal_action_mech:optimal_action},
                                         execution_id=execution_id,
                                         bin_execute=BIN_EXECUTE,
                                         )
            action = np.where(run_results[0]==0,0,run_results[0]/np.abs(run_results[0]))
            # action = np.squeeze(np.where(greedy_action_mech.value==0,0,
            #                              greedy_action_mech.value[0]/np.abs(greedy_action_mech.value[0])))
            print('\n**********************\nSTEP: ', steps)

            print('Observations:')
            print('\tPlayer:\n\t\tveridical: {}\n\t\tperceived: {}'.format(player_percept.parameters.variable.get(execution_id),
                                                                           player_percept.parameters.value.get(execution_id)))
            print('\tPredator:\n\t\tveridical: {}\n\t\tperceived: {}'.format(predator_percept.parameters.variable.get(execution_id),
                                                                           predator_percept.parameters.value.get(execution_id)))
            print('\tPrey:\n\t\tveridical: {}\n\t\tperceived: {}'.format(prey_percept.parameters.variable.get(execution_id),
                                                                         prey_percept.parameters.value.get(execution_id)))
            print('Actions:')
            print('\tActual: {}\n\tOptimal: {}'.format(action, optimal_action))
            # print('ObjectiveMechanism:')
            # print('\tActual: {}\n\tOptimal: {}\n\tSimilarity: {}'.
            #       format(ocm.objective_mechanism.parameters.variable.get(execution_id)[0],
            #              ocm.objective_mechanism.parameters.variable.get(execution_id)[1],
            #              ocm.objective_mechanism.parameters.value.get(execution_id)))
            print('Outcome: {}'.format(ocm.objective_mechanism.parameters.value.get(execution_id)))

            # print('Variance Params:')
            # print('\tPlayer:\t\t{}\n\tPredator\t{}\n\tPrey:\t\t{}'.
            #       format(player_percept.parameter_states[VARIANCE].parameters.value.get(execution_id),
            #              predator_percept.parameter_states[VARIANCE].parameters.value.get(execution_id),
            #              prey_percept.parameter_states[VARIANCE].parameters.value.get(execution_id)))

            print('OCM ControlSignals:')
            print('\tPlayer:\t\t{}\n\tPredator\t{}\n\tPrey:\t\t{}'.
                  format(ocm.control_signals[0].parameters.value.get(execution_id),
                         ocm.control_signals[1].parameters.value.get(execution_id),
                         ocm.control_signals[2].parameters.value.get(execution_id)))

            print('OCM ControlSignal Costs:')
            print('\tPlayer:\t\t{}\n\tPredator:\t{}\n\tPrey:\t\t{}'.
                  format(ocm.control_signals[0].parameters.cost.get(execution_id),
                         ocm.control_signals[1].parameters.cost.get(execution_id),
                         ocm.control_signals[2].parameters.cost.get(execution_id)))

            # print('Control Projection Senders\' Values (<percept>.parameter_states[VARIANCE].mod_afferents[0].sender.value):')
            # print('\tPlayer:\t\t{}\n\tPredator\t{}\n\tPrey:\t\t{}'.
            #       format(player_percept.parameter_states[VARIANCE].mod_afferents[0].sender.parameters.value.get(execution_id),
            #              predator_percept.parameter_states[VARIANCE].mod_afferents[0].sender.parameters.value.get(execution_id),
            #              prey_percept.parameter_states[VARIANCE].mod_afferents[0].sender.parameters.value.get(execution_id)))
            #
            # print('Control Projection Variables (<percept>.parameter_states[VARIANCE].mod_afferents[0].variable)):')
            # print('\tPlayer:\t\t{}\n\tPredator\t{}\n\tPrey:\t\t{}'.
            #       format(player_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.variable.get(execution_id),
            #              predator_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.variable.get(execution_id),
            #              prey_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.variable.get(execution_id)))
            #
            # print('Control Projection Values (<percept>.parameter_states[VARIANCE].mod_afferents[0].value):')
            # print('\tPlayer:\t\t{}\n\tPredator\t{}\n\tPrey:\t\t{}'.
            #       format(player_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.value.get(execution_id),
            #              predator_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.value.get(execution_id),
            #              prey_percept.parameter_states[VARIANCE].mod_afferents[0].parameters.value.get(execution_id)))

            print('SIMULATION (PREP FOR NEXT TRIAL):')
            for sample, value in zip(ocm.saved_samples, ocm.saved_values):
                print('\t\tSample: {} Value: {}'.format(sample, value))

            print('OCM Allocation (ocm.control_allocation):\n\t{}'.
                  format(repr(list(np.squeeze(ocm.parameters.control_allocation.get(execution_id))))))

            # Get observation for next iteration (based on action taken on this one)
            observation, reward, done, _ = ddqn_agent.env.step(action)
            steps += 1
            if done:
                break
    stop_time = timeit.default_timer()
    print(f'{steps / (stop_time - start_time):.1f} steps/second, {steps} total steps in '
          f'{stop_time - start_time:.2f} seconds')
    if RENDER:
        ddqn_agent.env.render(close=True)  # If visualization is desired

if RUN:
    if __name__ == "__main__":
        main()
