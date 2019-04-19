import numpy as np
import psyneulink as pnl


def extractValues(outputLog):
    decisionVariable = []
    probabilityUpper = []
    probabilityLower = []
    responseTime = []

    DECISION_VARIABLE = outputLog[1][1][4]
    PROBABILITY_LOWER_THRESHOLD = outputLog[1][1][5]
    PROBABILITY_UPPER_THRESHOLD = outputLog[1][1][6]
    RESPONSE_TIME = outputLog[1][1][7]

    for j in range(1, len(PROBABILITY_LOWER_THRESHOLD)):
        decision = DECISION_VARIABLE[j]
        trialUpper = PROBABILITY_UPPER_THRESHOLD[j]
        trialLower = PROBABILITY_LOWER_THRESHOLD[j]
        reaction = RESPONSE_TIME[j]

        decisionVariable.append(decision[0])
        probabilityUpper.append(trialUpper[0])
        probabilityLower.append(trialLower[0])
        responseTime.append(reaction[0])

    return probabilityUpper, probabilityLower


def computeAccuracy(variable):

    # variable is the list of values given by the monitored output states in the Objective Mechanism
    print("Inputs to ComputeAccuracy Function: ", variable)

    taskInputs = variable[0]
    stimulusInputs = variable[1]
    upperThreshold = variable[2]
    lowerThreshold = variable[3]
    print(taskInputs)

    accuracy = []
    for i in range(0, len(taskInputs)):
        print(taskInputs[i])

        colorTrial = (taskInputs[i][0] == 1)
        motionTrial = (taskInputs[i][1] == 1)

        # during color trials

        if colorTrial:
            # if the correct answer is the upper threshold
            if stimulusInputs[i][0] == 1:
                accuracy.append(upperThreshold)
                print('Color Trial: 1')

            # if the correct answer is the lower threshold
            elif stimulusInputs[i][0] == -1:
                accuracy.append(lowerThreshold)
                print('Color Trial: -1')

        if motionTrial:
            # if the correct answer is the upper threshold
            if stimulusInputs[i][1] == 1:
                accuracy.append(upperThreshold)
                print('Motion Trial: 1')

            # if the correct answer is the lower threshold
            elif stimulusInputs[i][1] == -1:
                accuracy.append(lowerThreshold)
                print('Motion Trial: -1')

    # added in after original "concept" for function to account for simulations where the variable does pass in inputs
    # as expected, which is exactly the problem we're currently trying to solve
    # if len(accuracy) == 0:
    #     accuracy = [0]
    #     # print('No Input')
    accuracy = accuracy[0]
    return accuracy



##### BEGIN STABILITY FLEXIBILITY MODEL CONSTRUCTION

tau = 0.9 # time constant
g = 1


excitatoryWeight = np.asarray([[1]])
inhibitoryWeight = np.asarray([[-1]])
gain = np.asarray([[g]])

DRIFT = 1 # Drift Rate
STARTING_POINT = 0.0 # Starting Point
THRESHOLD = 0.0475 # Threshold
NOISE = 0.04 # Noise
T0 = 0.2 # T0


# first element is color task attendance, second element is motion task attendance
inputLayer = pnl.TransferMechanism(#default_variable=[[0.0, 0.0]],
                                   size=2,
                                   function=pnl.Linear(slope=1, intercept=0),
                                   output_states = [pnl.RESULT],
                                   name='Input')
inputLayer.set_log_conditions([pnl.RESULT])

# Recurrent Transfer Mechanism that models the recurrence in the activation between the two stimulus and action
# dimensions. Positive self excitation and negative opposite inhibition with an integrator rate = tau
# Modulated variable in simulations is the GAIN variable of this mechanism
activation = pnl.RecurrentTransferMechanism(default_variable=[[0.0, 0.0]],
                                            function=pnl.Logistic(gain=0.3),
                                            matrix=[[1.0, -1.0],
                                                    [-1.0, 1.0]],
                                            integrator_mode = True,
                                            integrator_function=pnl.AdaptiveIntegrator(rate=(tau)),
                                            initial_value=np.array([[0.0, 0.0]]),
                                            output_states = [pnl.RESULT],
                                            name = 'Activity')

activation.set_log_conditions([pnl.RESULT, "mod_gain"])


stimulusInfo = pnl.TransferMechanism(default_variable=[[0.0, 0.0]],
                                     size = 2,
                                     function = pnl.Linear(slope=1, intercept=0),
                                     output_states = [pnl.RESULT],
                                     name = "Stimulus Info")

stimulusInfo.set_log_conditions([pnl.RESULT])

controlledElement = pnl.TransferMechanism(default_variable=[[0.0, 0.0]],
                                          size = 2,
                                          function=pnl.Linear(slope=1, intercept= 0),
                                          input_states=pnl.InputState(combine=pnl.PRODUCT),
                                          output_states = [pnl.RESULT],
                                          name = 'Stimulus Info * Activity')

controlledElement.set_log_conditions([pnl.RESULT])

ddmCombination = pnl.TransferMechanism(size = 1,
                                       function = pnl.Linear(slope=1, intercept=0),
                                       output_states = [pnl.RESULT],
                                       name = "DDM Integrator")
ddmCombination.set_log_conditions([pnl.RESULT])

decisionMaker = pnl.DDM(function=pnl.DriftDiffusionAnalytical(drift_rate = DRIFT,
                                                                 starting_point = STARTING_POINT,
                                                                 threshold = THRESHOLD,
                                                                 noise = NOISE,
                                                                 t0 = T0),
                                                                 output_states = [pnl.DECISION_VARIABLE, pnl.RESPONSE_TIME,
                                                                                  pnl.PROBABILITY_UPPER_THRESHOLD, pnl.PROBABILITY_LOWER_THRESHOLD],
                                                                 name='DDM')

decisionMaker.set_log_conditions([pnl.PROBABILITY_UPPER_THRESHOLD, pnl.PROBABILITY_LOWER_THRESHOLD,
                            pnl.DECISION_VARIABLE, pnl.RESPONSE_TIME])

########### Composition

stabilityFlexibility = pnl.Composition()

### NODE CREATION

stabilityFlexibility.add_node(inputLayer)
stabilityFlexibility.add_node(activation)
stabilityFlexibility.add_node(controlledElement)
stabilityFlexibility.add_node(stimulusInfo)
stabilityFlexibility.add_node(ddmCombination)
stabilityFlexibility.add_node(decisionMaker)


stabilityFlexibility.add_projection(sender= inputLayer, receiver = activation)
stabilityFlexibility.add_projection(sender = activation, receiver = controlledElement)
stabilityFlexibility.add_projection(sender = stimulusInfo, receiver = controlledElement)
stabilityFlexibility.add_projection(sender = stimulusInfo, receiver = ddmCombination)
stabilityFlexibility.add_projection(sender = controlledElement, receiver = ddmCombination)
stabilityFlexibility.add_projection(sender = ddmCombination, receiver = decisionMaker)

# testing input
taskTrain = [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0],
             [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]
stimulusTrain = [[1, -1], [1, -1], [1, -1], [1, -1], [1, -1],
                 [1, -1], [1, -1], [1, -1], [1, -1], [1, -1]]


inputs = {inputLayer: taskTrain, stimulusInfo: stimulusTrain}
# stabilityFlexibility.add_model_based_optimizer(meta_controller)
# stabilityFlexibility.enable_model_based_optimizer = True

print("Beginning of Run")
stabilityFlexibility.run(inputs)

decisions = decisionMaker.log.nparray()
upper, lower = extractValues(decisions)
print(upper)
print(lower)
variable = []
variable.append(taskTrain)
variable.append(stimulusTrain)
variable.append(upper)
variable.append(lower)

print(computeAccuracy(variable))







