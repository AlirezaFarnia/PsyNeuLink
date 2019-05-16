from psyneulink import *
import numpy as np

class TestModulatoryMechanism:

    # def test_control_modulation_in_system(self):
    #     Tx = TransferMechanism(name='Tx')
    #     Ty = TransferMechanism(name='Ty')
    #     Tz = TransferMechanism(name='Tz')
    #     C =  ModulatoryMechanism(
    #             # function=Linear,
    #             default_variable=[1],
    #             monitor_for_modulation=Ty,
    #             modulatory_signals=ControlSignal(modulation=OVERRIDE,
    #                                               projections=(SLOPE,Tz)))
    #     P1=Process(pathway=[Tx,Tz])
    #     P2=Process(pathway=[Ty, C])
    #     S=System(processes=[P1, P2])
    #     from pprint import pprint
    #     pprint(S.execution_graph)
    #
    #     assert Tz.parameter_states[SLOPE].mod_afferents[0].sender.owner == C
    #     result = S.run(inputs={Tx:[1,1], Ty:[4,4]})
    #     assert result == [[[4.], [4.]], [[4.], [4.]]]

    def test_assignment_of_control_and_gating_signals(self):
        m = ProcessingMechanism(function=Logistic)
        c = ModulatoryMechanism(
                modulatory_signals=[
                    ControlSignal(name="CS1", projections=(GAIN,m)),
                    GatingSignal(name="GS", projections=m),
                    ControlSignal(name="CS2", projections=(BIAS,m)),
                ]
        )
        assert  c.output_states.names == ['CS1', 'GS', 'CS2']
        assert m.parameter_states['gain'].mod_afferents[0].sender.owner == c
        assert m.parameter_states['bias'].mod_afferents[0].sender.owner == c
        assert m.input_state.mod_afferents[0].sender.owner == c

    def test_control_modulation_in_composition(self):
        Tx = TransferMechanism(name='Tx')
        Ty = TransferMechanism(name='Ty')
        Tz = TransferMechanism(name='Tz')
        C =  ModulatoryMechanism(
                default_variable=[1],
                monitor_for_modulation=Ty,
                modulatory_signals=ControlSignal(modulation=OVERRIDE,
                                                  projections=(SLOPE,Tz)))

        comp = Composition(enable_controller=True)
        comp.add_linear_processing_pathway(pathway=[Tx,Tz])
        comp.add_node(Ty, required_roles=NodeRole.TERMINAL)
        comp.add_controller(C)

        assert Tz.parameter_states[SLOPE].mod_afferents[0].sender.owner == C
        assert np.allclose(comp.results,[[[1.], [4.]], [[4.], [4.]]])

